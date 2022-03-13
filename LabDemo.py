# -*- coding: utf-8 -*-
"""
Created on Sun Mar 6 17:59:22 2022

@author: NathanAinsley
"""
import sqlite3
import tkinter as tk
from datetime import date
from tkinter import *
from tkinter.scrolledtext import ScrolledText
from Cryptodome.Protocol.KDF import PBKDF2
from Cryptodome.Hash import SHA512

database = 'database.db'
con = sqlite3.connect(database)
cur = con.cursor()
cur.execute('''CREATE TABLE  IF NOT EXISTS User(
                                Username text ,
                                Password text,
                                JobTitle text, 
                                Salt text,
                                Department text,
                                PRIMARY KEY (Username)
                                FOREIGN KEY (Department) REFERENCES Department(Departmentname))''')
cur.execute('''CREATE TABLE  IF NOT EXISTS Manager(
                                Username text ,
                                Password text,
                                JobTitle text, 
                                Salt text,
                                Department text,
                                PRIMARY KEY(Username)
                                FOREIGN KEY (Department) REFERENCES Department(Departmentname))''')
cur.execute('''CREATE TABLE  IF NOT EXISTS Department(
                                Departmentname text ,
                                Managername text,
                                Description text, 
                                PRIMARY KEY (Departmentname)
                                FOREIGN KEY (Managername) REFERENCES Manager(Username))''')
cur.execute('''CREATE TABLE  IF NOT EXISTS Records(
                                Departmentname text ,
                                Poster text,
                                Text text,
                                Date text,
                                PRIMARY KEY (Text)
                                FOREIGN KEY (Departmentname) REFERENCES Department(Departmentname))''')
con.commit()
con.close()

def TogglePasswordsLog(PassEnter,TogglePassword):
    if (PassEnter["show"] == "*"):
        PassEnter.configure(show="")
        TogglePassword.configure(text="Hide Password")
    else:
        PassEnter.configure(show="*")
        TogglePassword.configure(text="Show Password")
def Encrypt_User_Password(password,salt):
    key = PBKDF2(password, salt, 64, count=50000, hmac_hash_module=SHA512)
    return key
def populateResultsBox(ResultsBox):
    print(Log_user_name)
    print(level)
    ResultsBox.config(state=NORMAL)
    ResultsBox.delete('1.0', END)
    con=sqlite3.connect(database)
    cur = con.cursor()
    if (level == 'user'):
        cur.execute('''Select Department from User Where Username = ?''',(Log_user_name,))
        Department = cur.fetchone()
    elif(level =='manager'):
        cur.execute('''Select Department from Manager Where Username = ?''',(Log_user_name,))
        Department = cur.fetchone()
    cur.execute('''SELECT * FROM Records where Departmentname = ?''',(Department[0],))
    user1=cur.fetchall()
    for f in user1:
        print(f[1])
        print(f[2])
        print(f[3])
        statement = "["+f[1] + "] (" + f[3] +"): " + f[2]
        ResultsBox.insert(END, statement + '\n')
    con.close()
    ResultsBox.config(state=DISABLED)

def PostToBoard():
    print(Log_user_name)
    post = Post_Var.get()
    print(post)
    con=sqlite3.connect(database)
    cur = con.cursor()
    cur.execute('''Select Department from User Where Username = ?''',(Log_user_name,))
    Department = cur.fetchone()
    print(Department)
    Date = date.today().strftime("%d/%m/%Y")
    print(Date)
    cur.execute('''Insert into Records VALUES (?,?,?,?)''',(Department[0],Log_user_name,post,Date,))
    con.commit()
    con.close()
def PostBoard():
    global Post_Var
    Post_Var = StringVar()
    PostBox = Entry(root, textvariable = Post_Var)
    PostBox.place(x=150, y=470,width=300,height=20)
    PostButton = Button(root, text="Post",command = lambda: [ PostToBoard(),populateResultsBox(ResultsBox)])
    PostButton.place(x=50,y=470,width=100,height=20)
    ResultsBox = ScrolledText(root)
    ResultsBox.place(x=50, y=50,width=400,height=420)
    populateResultsBox(ResultsBox)
    RefreshButton = Button(root, text="Refresh",command = lambda: [ populateResultsBox(ResultsBox)])
    RefreshButton.place(x=50,y=10,width=100,height=20)
def clearWindow():
    for widget in root.winfo_children():
        widget.destroy()
def LoginUser():
    global Logged_In_User, Log_user_name, level
    level = 'user'
    Log_user_name = LogUsername_Var.get()
    LogPassword = LogPassword_Var.get()
    con=sqlite3.connect(database)
    cur = con.cursor()
    cur.execute('''SELECT Password,Salt FROM User WHERE Username=?''', (Log_user_name,))
    user1=cur.fetchall()
    if (len(user1)==0):
        messagebox.showerror("Error","No user found with that Username")
    else:
        P = user1[0][0]
        S = user1[0][1]
        con.close()
        key = (Encrypt_User_Password(LogPassword, S)).hex()
        if(key == P):
            Logged_In_User = "User: " + Log_user_name
            clearWindow()
            PostBoard()
        else:
            messagebox.showerror("Error","Password did not match")
def LoginManager():
    global Logged_In_User, Log_user_name, level
    
    level = 'manager'
    Log_user_name = LogUsername_Var.get()
    print(Log_user_name)
    LogPassword = LogPassword_Var.get()
    con=sqlite3.connect(database)
    cur = con.cursor()
    cur.execute('''SELECT Password,Salt FROM Manager WHERE Username=?''', (Log_user_name,))
    user1=cur.fetchall()
    if (len(user1)==0):
        messagebox.showerror("Error","No Manager found with that Username")
    else:
        P = user1[0][0]
        S = user1[0][1]
        con.close()
        key = (Encrypt_User_Password(LogPassword, S)).hex()
        if(key == P):
            Logged_In_User = "User: " + Log_user_name
            clearWindow()
            PostBoard()
        else:
            messagebox.showerror("Error","Password did not match")
def Loginmenu():
    global LogUsername_Var,LogPassword_Var
    LoginLabel = Label(root, text="Login", font=("Arial", 25))
    LoginLabel.place(x=200,y=50)
    Username = Label(root, text="Username: ")
    Username.place (x=100,y=100)
    LogUsername_Var = StringVar()
    UserEnter = Entry(root, textvariable = LogUsername_Var)
    UserEnter.place(x=175, y=100,width=200,height=20)
    Password = Label(root, text="Password: ")
    Password.place (x=100,y=150)
    LogPassword_Var = StringVar()
    PassEnter = Entry(root, textvariable = LogPassword_Var,show="*")
    PassEnter.place(x=175, y=150,width=200,height=20)
    TogglePassword = Button(root, text="Show Password", command = lambda:[TogglePasswordsLog(PassEnter,TogglePassword)])
    TogglePassword.place (x=200,y=200,width=100,height=30)
    LoginB = Button (root, text="Login", command = lambda:[ LoginUser()])
    LoginB.place (x=200,y=275,width=100,height=50)
def ManagerLoginmenu():
    global LogUsername_Var,LogPassword_Var
    LoginLabel = Label(root, text="Manager Login", font=("Arial", 25))
    LoginLabel.place(x=200,y=50)
    Username = Label(root, text="Username: ")
    Username.place (x=100,y=100)
    LogUsername_Var = StringVar()
    UserEnter = Entry(root, textvariable = LogUsername_Var)
    UserEnter.place(x=175, y=100,width=200,height=20)
    Password = Label(root, text="Password: ")
    Password.place (x=100,y=150)
    LogPassword_Var = StringVar()
    PassEnter = Entry(root, textvariable = LogPassword_Var,show="*")
    PassEnter.place(x=175, y=150,width=200,height=20)
    TogglePassword = Button(root, text="Show Password", command = lambda:[TogglePasswordsLog(PassEnter,TogglePassword)])
    TogglePassword.place (x=200,y=200,width=100,height=30)
    LoginB = Button (root, text="Login", command = lambda:[ LoginManager()])
    LoginB.place (x=200,y=275,width=100,height=50)
def root():
    global root
    root = tk.Tk()
    root.title('Nathan Ainsley (18028669) SSD Application')
    root.resizable(False, False)
    root.geometry("500x500")
    Login = Button (root, text="User Login", command = lambda: [ clearWindow(),Loginmenu()])
    Login.place (x=200,y=225,width=100,height=50)
    Login2 = Button (root, text="Manager Login", command = lambda: [ clearWindow(),ManagerLoginmenu()])
    Login2.place (x=200,y=275,width=100,height=50)
    root.mainloop()
root()
