import requests
import json
import base64
import cv2
import numpy as np
import requests
import io
from tkinter import messagebox


class Config:
    baseURL = "http://119.65.155.84"

def login(UserID,UserPassword):
    payload={
        'UserID':UserID,
        'UserPassword':UserPassword
    }
    headers = {'Content-Type': 'application/json'}
    response = requests.post(Config.baseURL + ':8000/token', headers=headers, json=payload)

    if response.status_code == 200:
        token_info=response.json()
        access_token=token_info['access_token']
        return access_token
    elif response.status_code == 404:
        return 404
    elif response.status_code == 400:
        return 400
    else:
        return 500


def signup(UserID, UserPassword, UserPasswordConfirm, UserName, UserSex, UserBirth, UserPhoneNumber):
    if UserPassword == UserPasswordConfirm:
        payload = {
            'UserID': UserID,
            'UserPassword': UserPassword,
            'UserName': UserName,
            'UserSex': UserSex,
            'UserBirth': UserBirth,
            'UserPhoneNumber': UserPhoneNumber
        }
        headers = {'Content-Type': 'application/json'}
        response = requests.post(Config.baseURL + ':8000/users', headers=headers, json=payload)

        if response.status_code == 201:
            return 'Created'

        elif response.status_code == 400:
            return 'ID_dup'

    else:
        return 'Password_confirm'


def user_delete(UserID,UserPassword):
    try:
        response = requests.delete(f"{Config.baseURL}:8000/users/{UserID}", json={"password": UserPassword})
        response.raise_for_status()
        return 'success'
    
        

    except requests.exceptions.HTTPError as e:
        status_code = e.response.status_code
        return status_code



def user_info(access_token_str):
    access_token_encoded_payload = access_token_str.split('.')[1]
    access_token_payload = json.loads(base64.b64decode(access_token_encoded_payload + '==').decode('utf-8'))
    user_id = access_token_payload.get('sub')

    headers = {'Authorization': f'Bearer {access_token_str}'}
    response = requests.get(f"{Config.baseURL}:8000/users/{user_id}", headers=headers)

    if response.status_code == 200:
        user_info = response.json()
        return user_info
    else:
        print("유저 정보 가져오기를 실패하였습니다.")




def face_extractor(img):
    face_classifier = cv2.CascadeClassifier('haarcascade_frontalface_alt.xml')
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_classifier.detectMultiScale(gray, 1.3, 5)

    if faces is ():
        return None

    for (x, y, w, h) in faces:
        cropped_face = img[y:y + h, x:x +w]

    return cropped_face


def faceregist(user_id):
    print(user_id)
    faceid = user_id
    cap = cv2.VideoCapture(0)
    count = 0
    
    while True:
        ret, frame = cap.read()
        if face_extractor(frame) is not None:
            count += 1
            face = cv2.resize(face_extractor(frame), (200, 200))
            face = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)

            # Save the image to memory
            is_success, buffer = cv2.imencode('.jpg', face)
            io_buf = io.BytesIO(buffer)

            # Upload the image from memory to the API
            requests.post(Config.baseURL + ':8000/upload', files={'image': (f'{faceid}.{count}.jpg', io_buf, 'image/jpeg')}, data={'user_id': faceid})

            cv2.putText(face, str(count), (50, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 2)
            cv2.imshow('facecollect', face)
        else:
            print("Face not Found")
            pass

        if cv2.waitKey(1) == 13 or count == 30:
            break

    cap.release()
    cv2.destroyAllWindows()
    messagebox.showinfo('얼굴 등록 성공','관리자의 승인을 기다리세요.')


def facewaitlist():
    response = requests.get(Config.baseURL + ':8000/folders')
    return response.json()


def facepermit(userid):
    response = requests.post(Config.baseURL + ':8000/move_face_permit',data={'user_id': userid})
    return str(response.json())



def updatefaceExist(userid):
    headers = {'Content-type': 'application/json'} 
    data = {"FaceExist": 1}  
    response = requests.put(Config.baseURL + ':8000/FaceExist/'+userid, data=json.dumps(data), headers=headers)
    return str(response.json())


def modeltrain():
    messagebox.showinfo("알림","잠시만 기다려주세요")
    response = requests.post(Config.baseURL + ':8000/training')
    return str(response.json())


def facerecognizestart():
    # 라즈베리 카메라 초기화 및 화면 설정()
    camera = cv2.VideoCapture(0)
    camera.set(3, 640) # set video widht
    camera.set(4, 480) # set video height


    while True:
        ret, frame = camera.read()

        if ret:
            _, img_encoded = cv2.imencode('.jpg', frame)
            response = requests.post(Config.baseURL+':8000/stream', data=img_encoded.tobytes(), headers={'Content-Type': 'image/jpeg'})

            if response.status_code == 200:
                response_data=response.json()
                image_base64=response_data["image_base64"]
                image_data=base64.b64decode(image_base64)
                np_arr = np.frombuffer(image_data, np.uint8)
                processed_img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

                if processed_img is not None and processed_img.size != 0:
                    cv2.imshow('출근', processed_img)
                    if(response_data["face_detection"]=='success'):
                        id=response_data["faces"]
                        result=messagebox.askyesno("정보",f"{id}가 맞으신가요?")
                        if result==True:
                            response=start(id)
                            messagebox.showinfo("알림",response.json())
                            break
                        else:
                            pass

                else:
                    print("사진을 받아오지 못했습니다.")
            else:
                print(f"Request failed with status code {response.status_code}")
        else:
            print("카메라 에러가 발생하였습니다.")

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    camera.release()
    cv2.destroyAllWindows()
    


def facerecognizeend():
    # 라즈베리 카메라 초기화 및 화면 설정()
    camera = cv2.VideoCapture(0)
    camera.set(3, 640) # set video widht
    camera.set(4, 480) # set video height


    while True:
        ret, frame = camera.read()

        if ret:
            _, img_encoded = cv2.imencode('.jpg', frame)
            response = requests.post(Config.baseURL+':8000/stream', data=img_encoded.tobytes(), headers={'Content-Type': 'image/jpeg'})

            if response.status_code == 200:
                response_data=response.json()
                image_base64=response_data["image_base64"]
                image_data=base64.b64decode(image_base64)
                np_arr = np.frombuffer(image_data, np.uint8)
                processed_img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

                if processed_img is not None and processed_img.size != 0:
                    cv2.imshow('퇴근', processed_img)
                    if(response_data["face_detection"]=='success'):
                        id=response_data["faces"]
                        result=messagebox.askyesno("정보",f"{id}가 맞으신가요?")
                        if result==True:
                            response=end(id)
                            messagebox.showinfo("알림",response.json())
                            break
                        else:
                            pass

                else:
                    print("사진을 받아오지 못했습니다.")
            else:
                print(f"Request failed with status code {response.status_code}")
        else:
            print("카메라 에러가 발생하였습니다.")

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    camera.release()
    cv2.destroyAllWindows()
   


def start(userid):
    response = requests.post(f"{Config.baseURL}:8000/attendance/start",data=json.dumps({"UserID": userid}),headers={"Content-Type": "application/json"})
    return response


def end(userid):
    response = requests.put(f"{Config.baseURL}:8000/attendance/end",data=json.dumps({"UserID": userid}),headers={"Content-Type": "application/json"})
    return response


def worked_hours(userid):
    response = requests.get(f"{Config.baseURL}:8000/attendance/worked_hours",data=json.dumps({"UserID": userid}),headers={"Content-Type": "application/json"})
    return response
