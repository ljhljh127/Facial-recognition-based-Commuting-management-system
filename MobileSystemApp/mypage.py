# -- coding: utf-8 --
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import function

def close_window(root):
    root.destroy()


def sex_return(sex):
    if sex == 'm':
        return '남'
    else:
        return '여'


def delete_result(value,mainroot,deleteroot):
    if value == 'success':
        messagebox.showinfo("탈퇴 완료", "회원 탈퇴가 완료되었습니다.")
        close_window(deleteroot)
        close_window(mainroot)
    elif value == 404:
        #이 에러가 뜬다면 현재 코드에 이상이 발생함 정상적이라면 아이디는 그냥 들어가야함
        messagebox.showerror("탈퇴 실패", "아이디가 존재하지 않습니다.")
        close_window(deleteroot)
    elif value == 401:
        messagebox.showerror("탈퇴 실패", "비밀번호가 일치하지 않습니다.")
        close_window(deleteroot)
    else:
        messagebox.showerror("서버에러","서버에서 알수없는 에러가 발생하였습니다.")
        close_window(deleteroot)
        close_window(mainroot)



def delete_window(userid,mainroot):
    delete_root = tk.Tk()
    delete_root.geometry("400x500")
    delete_root.title("회원탈퇴")

    # 입력 창 및 프레임

    user_password = tk.StringVar()




    password_label = ttk.Label(delete_root, text="비밀번호")
    password_entry = ttk.Entry(delete_root, textvariable=user_password, show='*')


    # 배치

    password_label.pack()
    password_entry.pack()

    delete_button = ttk.Button(delete_root, text="탈퇴하기",command=lambda:(delete_result(function.user_delete(userid,password_entry.get()),mainroot,delete_root)))
    delete_button.pack(pady=10)

    main_button = ttk.Button(delete_root, text="창 닫기", command=lambda: close_window(delete_root))
    main_button.pack(pady=10)
    delete_root.mainloop()





def mypage_window(value):
    mypage_root = tk.Tk()
    mypage_root.geometry("400x400")
    mypage_root.title("마이페이지")


    userid=value["UserID"]


    user_name_label = tk.Label(mypage_root, text=f"이름: {value['UserName']}")
    user_name_label.pack()

    usersex=sex_return(value['UserSex'])
    user_sex_label=tk.Label(mypage_root, text=f"성별: {usersex}")
    user_sex_label.pack()

    user_birth_label = tk.Label(mypage_root, text=f"생일: {value['UserBirth']}")
    user_birth_label.pack()

    user_phonenumber_label = tk.Label(mypage_root, text=f"휴대전화 번호: {value['UserPhoneNumber']}")
    user_phonenumber_label.pack()

    worked_hours_label = tk.Label(mypage_root, text=function.worked_hours(userid).json())
    worked_hours_label.pack()

    if value['FaceExist']==0:
        face_button = ttk.Button(mypage_root, text="얼굴등록", command=lambda:function.faceregist(value['UserID']))
        face_button.pack(side=tk.LEFT)

    main_button = ttk.Button(mypage_root, text="종료", command=lambda: close_window(mypage_root))
    main_button.pack(side=tk.LEFT)

    delete_button = ttk.Button(mypage_root, text="회원탈퇴", command=lambda: delete_window(userid,mypage_root))
    delete_button.pack(side=tk.LEFT)
    mypage_root.mainloop()
