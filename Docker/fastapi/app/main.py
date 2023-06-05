from datetime import date
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, Enum, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# FastAPI 애플리케이션 생성
app = FastAPI()

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

# 데이터베이스 연결 정보 설정
DB_USERNAME = 'root'
DB_PASSWORD = '11271209'
DB_HOST = '172.17.0.4'
DB_PORT = '3306'
DB_NAME = 'mydatabase'

# SQLAlchemy 연결 URL 생성
DB_URL = f'mysql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

# 데이터베이스 연결 엔진 생성
engine = create_engine(DB_URL)

# 세션 생성
Session = sessionmaker(bind=engine)
session = Session()


# 사용자 정보를 위한 모델 정의
class UserCreate(BaseModel):
    UserID: str
    UserPassword: str
    UserName: str
    UserSex: str
    UserBirth: date
    UserPhoneNumber: str
    class Config:
        orm_mode = True

class UserUpdate(BaseModel):
    UserPassword: str
    UserName: str
    UserSex: str
    UserBirth: date
    UserPhoneNumber: str
    class Config:
        orm_mode = True

# 사용자 생성 API 201은 Created를 의미함
@app.post("/users", status_code=201)
def create_user(user: UserCreate):
    new_user = UserTable(**user.dict())
    session.add(new_user)
    session.commit()
    session.refresh(new_user)  # 새로운 사용자 정보를 새로고침
    return UserCreate.from_orm(new_user)  # Pydantic 모델로 변환하여 반환

# 사용자 조회 API
@app.get("/users/{user_id}")
def get_user(user_id: str):
    user = session.query(UserTable).filter(UserTable.UserID == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="유저를 찾을 수 없습니다")
    return user

# 사용자 수정 API
@app.put("/users/{user_id}")
def update_user(user_id: str, user: UserUpdate):
    existing_user = session.query(UserTable).filter(UserTable.UserID == user_id).first()
    if not existing_user:
        raise HTTPException(status_code=404, detail="유저를 찾을 수 없습니다")
    for field, value in user.dict().items():
        setattr(existing_user, field, value)
    session.commit()
    session.refresh(existing_user)  # 수정된 사용자 정보를 새로고침
    return UserUpdate.from_orm(existing_user)  # Pydantic 모델로 변환

# 사용자 삭제 API
@app.delete("/users/{user_id}")
def delete_user(user_id: str):
    user = session.query(UserTable).filter(UserTable.UserID == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="유저를 찾을 수 없습니다")
    session.delete(user)
    session.commit()
    return {"message": "유저 삭제가 완료 되었습니다."}
