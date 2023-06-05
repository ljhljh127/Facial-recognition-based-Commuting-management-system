import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import function

def close_window(root):
    root.destroy()

def train_result(value,root):
    
    messagebox.showinfo("정보",value)
    root.destroy()

def permit_result(value,id,root):
    if value == 'success':
        messagebox.showinfo("허용완료", "학습 데이터에 추가하였습니다.")
        function.updatefaceExist(id)
    else:
        messagebox.showerror("실패", "학습 데이터에 추가에 실패하였습니다.")
    
    root.destroy()


def face_permitwindow():
    facepermit_root = tk.Tk()
    facepermit_root.geometry("400x500")
    facepermit_root.title("얼굴 허용")

    facewait_label = ttk.Label(facepermit_root, text='허용 대기중인 유저 리스트', font=("Helvetica", 14))
    facewait_label.grid(row=0, column=0, columnspan=2, padx=10, pady=10)

 # 허용 대기중인 유저 리스트
    waitlist = function.facewaitlist()
    users = waitlist["허용 대기중인 유저"]

    for index, user in enumerate(users):
        facewait_user_label = ttk.Label(facepermit_root, text=user, font=("Helvetica", 12))
        facewait_user_label.grid(row=index+1, column=0)

    user_id = tk.StringVar()
    id_label = ttk.Label(facepermit_root, text="허용할 아이디", font=("Helvetica", 14))
    id_entry = ttk.Entry(facepermit_root, textvariable=user_id, font=("Helvetica", 12))
    id_label.grid(row=len(users)+1, column=0, padx=10, pady=10)
    id_entry.grid(row=len(users)+1, column=1)

    permit_button = tk.Button(facepermit_root, text="허용하기", font=("Helvetica", 14),command=lambda: permit_result(function.facepermit(id_entry.get()),id_entry.get(),facepermit_root))
    permit_button.grid(row=len(users)+2, column=0, columnspan=2, padx=10, pady=20)

    training_label = ttk.Label(facepermit_root, text="모델 학습하기", font=("Helvetica",14))
    training_label.grid(row=len(users)+4, column=0, padx=20)

    training_button = tk.Button(facepermit_root, text="학습하기", font=("Helvetica", 14),command=lambda: train_result(function.modeltrain(),facepermit_root))
    training_button.grid(row=len(users)+4, column=1, padx=10)


    facepermit_root.mainloop()




def administrator_window():
    administrator_root = tk.Tk()
    administrator_root.geometry("300x300")
    administrator_root.title("관리자 페이지")

    start_button = ttk.Button(administrator_root, text="출근", command=lambda:function.facerecognizestart())
    start_button.grid(row=0, column=0, columnspan=2, padx=10, pady=10)

    end_button = ttk.Button(administrator_root, text="퇴근", command=lambda:function.facerecognizeend())
    end_button.grid(row=1, column=0, columnspan=2, padx=10, pady=10)

    face_permit_button = ttk.Button(administrator_root, text="얼굴 허용", command=face_permitwindow)
    face_permit_button.grid(row=2, column=0, columnspan=2, padx=10, pady=10)

    main_button = ttk.Button(administrator_root, text="종료", command=lambda: close_window(administrator_root))
    main_button.grid(row=3, column=0, columnspan=2, padx=10, pady=10)


    administrator_root.mainloop()

