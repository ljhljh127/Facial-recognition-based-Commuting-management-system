# -- coding: utf-8 --
import tkinter as tk
from tkinter import ttk
from tkcalendar import DateEntry  # DateEntry를 사용하기 위한 모듈 추가
from tkinter import messagebox
import function

def close_window(root):
    root.destroy()


def sex_return(sex):
    if sex == '남':
        return 'm'
    else:
        return 'f'


def sign_up_result(value,root):
    if value == 'Created':
        messagebox.showinfo("가입 완료", "회원가입이 완료되었습니다. 로그인을 진행해 주세요")
        close_window(root)
    elif value == 'ID_dup':
        messagebox.showerror("가입 실패", "존재하는 아이디입니다. 가입을 다시 시도해 주세요.")
        close_window(root)
    elif value == 'Password_confirm':
        messagebox.showerror("가입 실패", "비밀번호와 비밀번호 확인이 일치하지 않습니다. 다시 입력해 주세요.")
        close_window(root)



def signup_window():
    signup_root = tk.Tk()
    signup_root.geometry("400x500")
    signup_root.title("회원가입")

    # 입력 창 및 프레임
    user_id = tk.StringVar()
    user_password = tk.StringVar()
    user_password_confirm = tk.StringVar()
    user_name = tk.StringVar()
    user_sex = tk.StringVar()
    user_phonenumber = tk.StringVar()

    id_label = ttk.Label(signup_root, text="아이디")
    id_entry = ttk.Entry(signup_root, textvariable=user_id)

    password_label = ttk.Label(signup_root, text="비밀번호")
    password_entry = ttk.Entry(signup_root, textvariable=user_password, show='*')

    password_confirm_label = ttk.Label(signup_root, text="비밀번호 확인")
    password_confirm_entry = ttk.Entry(signup_root, textvariable=user_password_confirm, show='*')

    name_label = ttk.Label(signup_root, text="이름")
    name_entry = ttk.Entry(signup_root, textvariable=user_name)

    birth_label = ttk.Label(signup_root, text="생년월일")
    birth_entry = DateEntry(signup_root, locale='ko_KR', date_pattern='y-mm-dd')  # DateEntry 사용

    sex_label = ttk.Label(signup_root, text="성별")
    sex_combobox = ttk.Combobox(signup_root, textvariable=user_sex, state="readonly")  # 콤보박스 사용
    sex_combobox["values"] = ("남", "여")  # 선택 가능한 값을 설정
    sex_combobox.current(0)  # 기본 선택 값 설정

    phonenumber_label = ttk.Label(signup_root, text="전화번호")
    phonenumber_entry = ttk.Entry(signup_root, textvariable=user_phonenumber)

    # 배치
    id_label.pack()
    id_entry.pack()

    password_label.pack()
    password_entry.pack()

    password_confirm_label.pack()
    password_confirm_entry.pack()

    name_label.pack()
    name_entry.pack()

    birth_label.pack()
    birth_entry.pack()

    sex_label.pack()
    sex_combobox.pack()

    phonenumber_label.pack()
    phonenumber_entry.pack()

    register_button = ttk.Button(signup_root, text="가입하기",
                                 command=lambda: sign_up_result(function.signup(id_entry.get(),
                                                                 password_entry.get(),
                                                                 password_confirm_entry.get(),
                                                                 name_entry.get(),
                                                                 sex_return(sex_combobox.get()),
                                                                 str(birth_entry.get()),
                                                                 phonenumber_entry.get()),signup_root))
    register_button.pack(pady=10)

    main_button = ttk.Button(signup_root, text="메인화면", command=lambda: close_window(signup_root))
    main_button.pack(pady=10)
    signup_root.mainloop()
