# -- coding: utf-8 --
import tkinter as tk
from tkinter import ttk
import function
import signup
import mypage
import administrator
from tkinter import messagebox


# 필드 클리어 함수
def clear_entry(widget, text):
    if widget.get() == text:
        widget.delete(0, tk.END)

def close_window(root):
    root.destroy()


def login_result(value,root):
    if value == 404:
        messagebox.showerror('로그인 에러','존재하지 않는 ID입니다.')
    elif value == 400:
        messagebox.showerror('로그인 에러','비밀번호가 틀립니다.')
    elif value== 500:
        messagebox.showerror('서버 에러','서버에 오류가 발생하였습니다.')
    else:
        messagebox.showinfo('로그인 성공','환영합니다.')
        close_window(root)
        user_info=function.user_info(value)
        if(user_info["UserID"]=='Administrator'):
            administrator.administrator_window()       
        else:
            mypage.mypage_window(user_info)



root=tk.Tk()
root.geometry("500x400")
root.title("홍익 Company")

# 제목 생성 및 배치
title_frame = tk.Frame(root)
title_frame.pack(pady=20)

hongik_text = tk.Label(title_frame, text="홍익", font=("Helvetica", 24,'bold'))
hongik_text.pack()

company_text = tk.Label(title_frame, text="Company", font=("Helvetica", 16,'bold'))
company_text.pack()

# 아이디와 비밀번호 프레임 및 입력창 생성
user_id = tk.StringVar()
user_password = tk.StringVar()

user_id_frame = tk.Frame(root, bg="white")
user_password_frame = tk.Frame(root, bg="white")
user_id_frame.pack(pady=5)
user_password_frame.pack(pady=5)

id_entry = ttk.Entry(user_id_frame, textvariable=user_id, width=30)
id_entry.pack()
id_entry.insert(0, "아이디")
id_entry.bind("<FocusIn>", lambda e: clear_entry(id_entry, "아이디"))

password_entry = ttk.Entry(user_password_frame, textvariable=user_password, width=30, show='*')
password_entry.pack()
password_entry.configure(show='•')
password_entry.insert(0, "****")
password_entry.bind("<FocusIn>", lambda e: clear_entry(password_entry, "****"))

# 로그인과 회원가입 프레임 및 버튼 생성
login_frame=tk.Frame(root,bg='white')
login_frame.pack(pady=15)

signup_frame = tk.Frame(root)
signup_frame.pack(pady=5)

login_button = ttk.Button(login_frame, text="로그인", command=lambda: login_result(function.login(id_entry.get(), password_entry.get()),root))
login_button.pack()

signup_label = tk.Label(signup_frame, text="아직 회원이 아니신가요?")
signup_label.pack(side=tk.LEFT)

signup_button = ttk.Button(signup_frame, text="회원가입",command=signup.signup_window)
signup_button.pack(side=tk.LEFT)

root.mainloop()
