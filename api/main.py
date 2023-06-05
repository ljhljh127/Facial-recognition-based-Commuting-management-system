from datetime import date,time,datetime, timedelta
from fastapi import FastAPI, HTTPException, Body,File, UploadFile, Form,Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse,StreamingResponse
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, Enum, Date,Time,ForeignKey,create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import bcrypt
from typing import Optional
from builtins import setattr
import jwt
from typing import List
import os
import shutil
import cv2
import numpy as np
from PIL import Image
import json
import io
import base64
import re

# FastAPI 애플리케이션 생성
app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://119.65.155.84",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# SQLAlchemy 모델 선언을 위한 베이스 클래스 생성
Base = declarative_base()


# UserTable 모델 정의
class UserTable(Base):
    __tablename__ = 'UserTable'
    UserID = Column(String(50), primary_key=True)
    UserPassword = Column(String(255), nullable=False)
    UserName = Column(String(30), nullable=False)
    UserSex = Column(Enum('m', 'f'), nullable=False)
    UserBirth = Column(Date, nullable=False)
    UserPhoneNumber = Column(String(50), nullable=False)
    FaceExist = Column(Integer, nullable=False, default=0)


# Attendance Table 모델 정의
class AttendanceTable(Base):
    __tablename__ = 'AttendanceTable'
    AttendanceID = Column(Integer, primary_key=True, autoincrement=True)
    UserID = Column(String(50), ForeignKey('UserTable.UserID'), nullable=False)
    Date = Column(Date, nullable=False)
    StartTime = Column(Time, nullable=False)
    EndTime = Column(Time, nullable=True)



# 데이터베이스 연결 정보 설정
DB_USERNAME = 'root'
DB_PASSWORD = '11271209'
DB_HOST = '172.17.0.3'
DB_PORT = '3306'
DB_NAME = 'mydatabase'

# SQLAlchemy 연결 URL 생성
DB_URL = f'mysql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

# 데이터베이스 연결 엔진 생성
engine = create_engine(DB_URL)

# 세션 생성
Session = sessionmaker(bind=engine)
session = Session()


# 사용자 생성을 위한 모델 정의
class UserCreate(BaseModel):
    UserID: str
    UserPassword: str
    UserName: str
    UserSex: str
    UserBirth: date
    UserPhoneNumber: str

    class Config:
        orm_mode = True


class UserGet(BaseModel):
    UserID: str
    UserName: str
    UserSex: str
    UserBirth: date
    UserPhoneNumber: str
    FaceExist: int

    class Config:
        orm_mode = True


# Update 구문에서 Optional로 처리하여서 필드를 선택적으로 처리
class UserUpdate(BaseModel):
    UserPassword: Optional[str]
    UserName: Optional[str]
    UserSex: Optional[str]
    UserBirth: Optional[date]
    UserPhoneNumber: Optional[str]

    class Config:
        orm_mode = True


# 로그인 모델
class UserLogin(BaseModel):
    UserID: str
    UserPassword: str

    class Config:
        orm_mode = True


class UpdateExist(BaseModel):
    FaceExist: int

    class Config:
        orm_mode = True


class Attendance(BaseModel):
    UserID: str

    class Config:
        orm_mode = True







# JWT(secret key) 액세스 토큰
SECRET_KEY = "dlwjdgusdlwjdgus123411234"  # 암호화를 위한 비밀 키
ALGORITHM = "HS256"  # 암호화 알고리즘
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # 액세스 토큰 만료 시간

# tokenUrl이 "token"인 OAuth2PasswordBearer 인스턴스 생성
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# 함수 모음

# 토큰 생성 함수
def create_access_token(data: dict):
    to_encode = data.copy()  # 입력된 데이터를 복사
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)  # 현재 UTC 시간에 액세스 토큰 만료 시간을 더해 만료 시간 계산
    to_encode.update({"exp": expire})  # 만료 시간을 데이터에 추가
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)  # 입력된 데이터와 비밀 키, 알고리을 이용해 JWT 생성
    return encoded_jwt  # 생성된 JWT 반환


recognizer = cv2.face.LBPHFaceRecognizer_create()
path = 'permit_faces'  # getImage, 와 train_faces에 들어감


def getImagesAndLabels(path):
    if not os.path.exists(path):
        return [], [], {}, {}  # 폴더가 없을 경우 비어있는 리스트와 딕셔너리를 반환합니다.

    detector = cv2.CascadeClassifier("haarcascades/haarcascade_frontalface_default.xml")
    imagePaths = [os.path.join(path, f) for f in os.listdir(path)]

    if not imagePaths:
        return [], [], {}, {}  # 폴더가 비었으면 여기서 비어있는 리스트와 딕셔너리를 반환합니다.

    faceSamples = []
    ids = []
    for imagePath in imagePaths:
        PIL_img = Image.open(imagePath).convert('L')
        img_numpy = np.array(PIL_img, 'uint8')
        id = os.path.split(imagePath)[-1].split(".")[0]
        faces = detector.detectMultiScale(img_numpy)
        for (x, y, w, h) in faces:
            faceSamples.append(img_numpy[y:y + h, x:x + w])
            ids.append(id)
    id_map = create_id_map(ids)
    decoded_ids = {v: k for k, v in id_map.items()}
    return faceSamples, ids, id_map, decoded_ids


async def train_faces():
    try:
        print("\n [INFO] 얼굴 학습 중입니다....")
        faces, ids, id_map, decoded_ids = getImagesAndLabels(path)

        if not faces or not ids:  # 얼굴과 ID 리스트가 비어있는지 확인합니다.
            print("학습할 얼굴이 없습니다.")
            return {"info": "학습할 얼굴이 없습니다."}

        encoded_ids = [id_map[i] for i in ids]
        encoded_ids = np.array(encoded_ids)
        recognizer.train(faces, encoded_ids)
        save_mapping(id_map, decoded_ids)
        if not os.path.exists('trainer'):
            os.makedirs('trainer')

        recognizer.write('trainer/trainer.yml')

        trained_faces = [v for v in decoded_ids.values()]
        print({"info": f"{len(np.unique(ids))} 개의 얼굴이 학습되었습니다.", "현재 모델에 학습된 얼굴": trained_faces})
        return {"info": f"{len(np.unique(ids))} 개의 얼굴이 학습되었습니다.", "현재 모델에 학습된 얼굴": trained_faces}

    except Exception as e:
        raise HTTPException(status_code=500, detail="서버에 알 수 없는 에러가 발생하였습니다.")


# id를 토대로 숫자부여
def create_id_map(ids):
    unique_ids = list(set(ids))
    id_map = {unique_ids[i]: i for i in range(len(unique_ids))}
    return id_map


# id를 토대로 숫자를 부여한 것을 저장함
def save_mapping(id_map, decoded_ids):
    mapping = {
        'id_map': id_map,
        'decoded_ids': decoded_ids
    }
    with open('mapping.json', 'w') as f:
        json.dump(mapping, f)


# 아까 저장한 파일로 숫자를 통하여 id반환
def load_mapping():
    with open('mapping.json', 'r') as f:
        mapping = json.load(f)
    return mapping['id_map'], mapping['decoded_ids']


cascadePath = "haarcascades/haarcascade_frontalface_default.xml"
faceCascade = cv2.CascadeClassifier(cascadePath);

if os.path.isfile('trainer/trainer.yml'):
    recognizer.read('trainer/trainer.yml')
else:
    print('trainer/trainer.yml 파일이 존재하지 않습니다.')


# user 엔드포인트

# 사용자 생성 API 201은 Created를 의미함
@app.post("/users", status_code=201)
def create_user(user: UserCreate):
    # 기존에 동일한 ID로 가입한 사용자가 있는지 확인
    existing_user = session.query(UserTable).filter(UserTable.UserID == user.UserID).first()
    if existing_user:  # 이미 해당 ID로 가입한 사용자가 있는 경우
        raise HTTPException(status_code=400, detail="중복된 ID가 존재합니다.")  # 에러와 메세지 반환

    # 비밀번호 암호화
    hashed_password = bcrypt.hashpw(user.UserPassword.encode('utf-8'), bcrypt.gensalt())

    new_user = UserTable(
        UserID=user.UserID,
        UserPassword=hashed_password.decode('utf-8'),
        UserName=user.UserName,
        UserSex=user.UserSex,
        UserBirth=user.UserBirth,
        UserPhoneNumber=user.UserPhoneNumber
    )
    session.add(new_user)
    session.commit()
    session.refresh(new_user)  # 새로운 사용자 정보를 새로고침
    return UserCreate.from_orm(new_user)  # Pydantic 모델로 변환하여 반환


# 사용자 조회 API
@app.get("/users/{user_id}", response_model=UserGet)
def get_user(user_id: str, token: str = Depends(oauth2_scheme)):
    user = session.query(UserTable).filter(UserTable.UserID == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="유저를 찾을 수 없습니다")
    return user



# 사용자 삭제 API
@app.delete("/users/{user_id}")
async def delete_user(user_id: str, password: str = Body(..., embed=True)):
    # 사용자 조회
    user = session.query(UserTable).filter(UserTable.UserID == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="유저를 찾을 수 없습니다")

    # 비밀번호 인증
    if not bcrypt.checkpw(password.encode('utf-8'), user.UserPassword.encode('utf-8')):
        raise HTTPException(status_code=401, detail="비밀번호가 일치하지 않습니다")

    # 사용자 삭제
    session.delete(user)
    session.commit()

    # 사용자 삭제시 학습된 얼굴을 지워야함
    folder_path = 'permit_faces/'  # permit 폴더 경로
    id_regex = re.compile(f"{user_id}\.\d+\.jpg")  # id로 시작하는 jpg 확장자 모두 찾아내기 위함

    # 폴더 내 모든 파일 검색
    for filename in os.listdir(folder_path):
        filepath = os.path.join(folder_path, filename)

        # 파일 이름이 id로 시작하는지 검사
        if id_regex.match(filename):
            # 파일 삭제
            os.remove(filepath)

    # 학습된 모델 폴더 자체를 제거해 버린다. 이후 모델 재 학습을 진행해준다.
    if os.path.exists("trainer"):
        shutil.rmtree("trainer")

    # 모델을 재 학습시킨다.
    result = await train_faces()
    return {"message": "유저 삭제가 완료되었습니다."}


# 토큰 발급 API
@app.post("/token", response_model=dict)#딕셔너리 형태로 id의 토큰을 받기때문에 dict
async def login(user: UserLogin):
    existing_user = session.query(UserTable).filter(UserTable.UserID == user.UserID).first()
    if not existing_user:
        raise HTTPException(status_code=404, detail="유저를 찾을 수 없습니다.")

    password_check = bcrypt.checkpw(user.UserPassword.encode('utf-8'), existing_user.UserPassword.encode('utf-8'))
    if not password_check:
        raise HTTPException(status_code=400, detail="비밀번호가 일치하지 않습니다.")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.UserID, "username": existing_user.UserName},
    )
    return {"access_token": access_token, "token_type": "bearer"}


# 학습용 사진을 서버로 보내는 API
@app.post("/upload")
async def upload_image(image: UploadFile = File(...), user_id: str = Form(...)):
    # UserID를 가져와서 uploadedfaces/ID로 저장하게됨
    user_folder = os.path.join('uploaded_faces', user_id)
    # 해당 폴더가 존재하지 않는다면 폴더를 생성함
    os.makedirs(user_folder, exist_ok=True)
    # 이미지를 저장하기 위한 파일 경로
    save_path = os.path.join(user_folder, image.filename)

    try:
        with open(save_path, "wb") as f:
            f.write(image.file.read())
        return {"status": "success", "message": "이미지가 저장되었습니다.."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"이미지 저장에 실패했습니다.: {str(e)}")


# uploaded_faces 하위 폴더명을 전부 가져옴(이를 이용해서 얼굴 수락 할 사람 목록을 확인 할 수 있음)
@app.get("/folders")
def get_folders():
    main_folder = 'uploaded_faces'
    subfolders = [f.name for f in os.scandir(main_folder) if f.is_dir()]
    return {"허용 대기중인 유저": subfolders}


# 관리자 허용 API permit 폴더로 이동시킴
@app.post("/move_face_permit")
async def move_faces(user_id: str = Form(...)):
    uploaded_faces_folder_id = f"uploaded_faces/{user_id}"
    permit_faces_folder = "permit_faces"
    os.makedirs(permit_faces_folder, exist_ok=True)

    if os.path.exists(uploaded_faces_folder_id):
        for file in os.listdir(uploaded_faces_folder_id):
            if file.endswith(".jpg") or file.endswith(".png") or file.endswith(".jpeg"):
                shutil.copy(os.path.join(uploaded_faces_folder_id, file), permit_faces_folder)

        shutil.rmtree(uploaded_faces_folder_id)  # uploaded_faces 해당 id 폴더 삭제
        return 'success'
    else:
        return 'failed'


# 사용자 수정 API(얼굴 인식 관해서)
@app.put("/FaceExist/{user_id}")
def update_user(user_id: str, user: UpdateExist):
    existing_user = session.query(UserTable).filter(UserTable.UserID == user_id).first()
    if not existing_user:
        raise HTTPException(status_code=404, detail="유저를 찾을 수 없습니다")
        return 'failed'

    # 업데이트 필드 설정
    update_fields = {}
    if user.FaceExist:
        update_fields['FaceExist'] = user.FaceExist

    # 사용자 정보 업데이트
    for field, value in update_fields.items():
        # setattr로  existing_user필드 동적할당
        setattr(existing_user, field, value)

    session.commit()
    session.refresh(existing_user)  # 수정된 사용자 정보를 새로고침
    return 'success'

# 모델 훈련
@app.post("/training")
async def training_faces():
    result = await train_faces()
    return result

# 라즈베리파이로 받은 스트림을 처리해서 얼굴인식 후 다시 라즈베리파이로 보내준다.
@app.post("/stream")
async def process_image(request: Request):
    try:

        font = cv2.FONT_HERSHEY_SIMPLEX
        _, decoded_ids = load_mapping()
        content_type = request.headers['Content-Type']
        if content_type == 'image/jpeg':
            # 전송된 영상 데이터 읽기
            content = await request.body()
            np_array = np.frombuffer(content, np.uint8)
            img = cv2.imdecode(np_array, cv2.IMREAD_COLOR)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = faceCascade.detectMultiScale(
                gray,
                scaleFactor=1.2,
                minNeighbors=5,
            )

            for (x, y, w, h) in faces:
                cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
                id, confidence = recognizer.predict(gray[y:y + h, x:x + w])
                # confidence가 0에 가까울 수록 일치함 (100-confidence)이 유사도
                if (confidence < 100):
                    if (confidence < 55):
                        id = decoded_ids[str(id)]
                        confidence = "  {0}%".format(round(100 - confidence))
                        cv2.putText(img, str(id), (x + 5, y - 5), font, 1, (255, 255, 255), 2)
                        cv2.putText(img, str(confidence), (x + 5, y + h - 5), font, 1, (255, 255, 0), 1)
                        _, img_encoded = cv2.imencode('.jpg', img)
                        img_base64 = base64.b64encode(img_encoded.tobytes()).decode('utf-8')
                        return {"image_base64": img_base64, "face_detection": 'success', "faces": id}
                    else:
                        id = decoded_ids[str(id)]
                        confidence = "  {0}%".format(round(100 - confidence))
                        cv2.putText(img, str(id), (x + 5, y - 5), font, 1, (255, 255, 255), 2)
                        cv2.putText(img, str(confidence), (x + 5, y + h - 5), font, 1, (255, 255, 0), 1)
                        _, img_encoded = cv2.imencode('.jpg', img)
                        img_base64 = base64.b64encode(img_encoded.tobytes()).decode('utf-8')
                        return {"image_base64": img_base64, "face_detection": 'false', "faces": id}




                else:
                    id = "unknown"


                cv2.putText(img, str(id), (x + 5, y - 5), font, 1, (255, 255, 255), 2)


            # HTTP 응답 본문으로 전송하기
            _, img_encoded = cv2.imencode('.jpg', img)
            img_base64 = base64.b64encode(img_encoded.tobytes()).decode('utf-8')
            return {"image_base64": img_base64, "face_detection": 'false', "faces": ""}

        # 콘텐츠 타입이 image/jpeg가 아닌 경우 에러 메시지 반환
        else:
            return {"error": "Invalid content-type"}
    except Exception as e:
        return {"error": str(e)}


@app.post("/attendance/start")
def start(user:Attendance):
    start_time = datetime.now().strftime("%H:%M:%S")
    today_date = date.today()
    existing_attendance = session.query(AttendanceTable).filter(AttendanceTable.UserID == user.UserID, AttendanceTable.Date == today_date).first()

    if existing_attendance:
        return f"이미 출근 처리 되었습니다. 출근시간{existing_attendance.Date} {existing_attendance.StartTime}"
    else:
        attendance = AttendanceTable(UserID=user.UserID, Date=today_date, StartTime=start_time)
        session.add(attendance)
        session.commit()

        return f"출근 시간이 기록되었습니다. UserID: {user.UserID} 날짜: {today_date}, 출근 시간: {start_time}"



@app.put("/attendance/end")
def end(user:Attendance):
    end_time = datetime.now().strftime("%H:%M:%S")
    today_date = date.today()

    existing_attendance = session.query(AttendanceTable).filter(AttendanceTable.UserID == user.UserID, AttendanceTable.Date == today_date).first()

    if existing_attendance:
        existing_attendance.EndTime = end_time
        session.commit()
        return f"퇴근 시간이 업데이트되었습니다. UserID: {user.UserID} 날짜: {today_date}, 퇴근 시간: {end_time}"
    else:
        return "오늘 출근 기록이 없습니다."




@app.get("/attendance/worked_hours")
def get_worked_hours(user:Attendance):
    current_month = datetime.now().month

    start_date = date(datetime.now().year, current_month, 1) # 현재 년도,달과 1일 예를 들어 지금은 2023년 6월 1일
    end_date = date(datetime.now().year, current_month+1, 1) # 한마디로 end_date는 다음달 1일을 뜻함 그 사이 범위로 이번달 근무시간 계산
    if current_month==12:
        end_date=date(datetime.now().year+1,1,1)# 12월의 경우 한달을 더하면 13월이됨 ==> 내년 1월로 1일로 처리

    attendances = session.query(AttendanceTable).filter(
        AttendanceTable.UserID == user.UserID,
        AttendanceTable.Date >= start_date,
        AttendanceTable.Date < end_date,
        AttendanceTable.EndTime != None, #이 것을 이용하여 오늘 아직 퇴근처리가 안된건 미반영함
    ).all()

    worked_hours = timedelta() #0으로 초기화

    for list in attendances:
        start_time = datetime.strptime(str(list.StartTime), "%H:%M:%S")#DB에 Time형식이라 datetime과 호환하기 위해서 str변환후
        end_time = datetime.strptime(str(list.EndTime), "%H:%M:%S")#date time 형식으로 변환함
        worked_hours = worked_hours+end_time-start_time


    existing_user = session.query(UserTable).filter(UserTable.UserID == user.UserID).first()
    return f"{existing_user.UserName}님의 {current_month}월 총 근무 시간: {worked_hours}"
