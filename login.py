import math
from tkinter import* 
from tkinter import ttk
from PIL import Image,ImageTk,ImageDraw,ImageFont
from datetime import *
import time
from math import *
from tkinter import messagebox
from register import Register
import mysql.connector

# --------------------------
from train import Train
from student import Student
from train import Train
from face_recognition import Face_Recognition
from attendance import Attendance
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def safe_open_image(rel_path, size, fallback_color=(3, 31, 60)):
    """Open an image from the project folder. If it's missing, generate a
    plain placeholder of the right size instead of crashing."""
    full_path = os.path.join(BASE_DIR, rel_path)
    try:
        return Image.open(full_path)
    except FileNotFoundError:
        return Image.new("RGB", size, fallback_color)


class Login:
    def __init__(self,root):
        self.root=root
        self.root.title("Sign in")
        self.root.state('zoomed')
        self.root.config(bg="#031F3C")

        # Fit to the actual screen size (for accurate centering)
        self.screen_w = self.root.winfo_screenwidth()
        self.screen_h = self.root.winfo_screenheight()
        self.root.geometry(f"{self.screen_w}x{self.screen_h}+0+0")

        # Single solid dark-blue background across the whole window
        bg_all = Label(self.root, bg="#031F3C", bd=0)
        bg_all.place(x=0, y=0, relwidth=1, relheight=1)

        # Frame — centered on screen, regardless of resolution
        card_w, card_h = 800, 500
        card_x = (self.screen_w - card_w) // 2
        card_y = (self.screen_h - card_h) // 2
        login_frame = Frame(self.root, bg="white")
        login_frame.place(x=card_x, y=card_y, width=card_w, height=card_h)

        title = Label(login_frame, text="LOG IN", font=("times new roman", 30, "bold"), bg="white", fg="navyblue")
        title.place(x=250, y=50)

        #variable
        self.var_ssq=StringVar()
        self.var_sa=StringVar()
        self.var_pwd=StringVar()

        email = Label(login_frame, text="Email", font=("times new roman", 18, "bold"), bg="white", fg="navyblue").place(x=250, y=150)
        self.txtuser = Entry(login_frame, font=("times new roman", 15), bg="lightgray")
        self.txtuser.place(x=250, y=180, width=350, height=35)

        pass_ = Label(login_frame, text="Password", font=("times new roman", 18, "bold"), bg="white", fg="navyblue").place(x=250, y=250)
        self.txtpwd = Entry(login_frame, font=("times new roman", 15), bg="lightgray")
        self.txtpwd.place(x=250, y=280, width=350, height=35)

        btn_reg = Button(login_frame, cursor="hand2", command=self.reg, text="Sign up ", font=("times new roman", 14), bg="white", bd=0, fg="navyblue").place(x=250, y=330)

        btn_forgetpwd = Button(login_frame, cursor="hand2", command=self.forget_pwd, text="Forgot password?", font=("times new roman", 14), bg="white", bd=0, fg="navyblue").place(x=500, y=330)

        btn_login = Button(login_frame, text="Log in", command=self.login, font=("times new roman", 20, "bold"), fg="white", cursor="hand2", bg="navyblue").place(x=250, y=380, width=180, height=40)




        # Clock — small decorative element, tucked in the top-left corner
        # so it never collides with the centered login card
        now = datetime.now()
        self.lbl = Label(self.root, compound=BOTTOM, bg="#031F3C", bd=0)
        self.lbl.place(x=40, y=40, height=240, width=240)

        self.digital_lbl = Label(self.root, text="", font=("Verdana", 16, "bold"), fg="#E6C86E", bg="#031F3C")
        self.digital_lbl.place(x=40, y=285, height=28, width=240)

        self.date_lbl = Label(self.root, text="", font=("times new roman", 11), fg="white", bg="#031F3C")
        self.date_lbl.place(x=40, y=313, height=22, width=240)

        self.working()


    def clock_image(self, hr, min_, sec_):
        SIZE = 220
        PANEL_BG = (3, 31, 60)
        clock = Image.new("RGB", (SIZE, SIZE), PANEL_BG)
        draw = ImageDraw.Draw(clock)

        cx, cy = SIZE // 2, SIZE // 2
        R = 95

        try:
            font_num = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 12)
        except Exception:
            font_num = ImageFont.load_default()

        # Outer metallic-gold rim
        draw.ellipse((cx-R-6, cy-R-6, cx+R+6, cy+R+6), fill=(201, 162, 39))
        draw.ellipse((cx-R-2, cy-R-2, cx+R+2, cy+R+2), fill=(230, 200, 110))
        # Inner navy face
        draw.ellipse((cx-R, cy-R, cx+R, cy+R), fill=(13, 27, 62))
        # Subtle inner ring accent
        draw.ellipse((cx-R+7, cy-R+7, cx+R-7, cy+R-7), outline=(80, 110, 150), width=1)

        # Hour ticks + numerals
        for i in range(12):
            angle = math.radians(i * 30)
            is_major = i % 3 == 0
            outer_r = R - 6
            inner_r = R - (16 if is_major else 10)
            x1 = cx + outer_r * math.sin(angle)
            y1 = cy - outer_r * math.cos(angle)
            x2 = cx + inner_r * math.sin(angle)
            y2 = cy - inner_r * math.cos(angle)
            draw.line((x1, y1, x2, y2), fill=(230, 200, 110), width=3 if is_major else 2)

            num = i if i != 0 else 12
            num_r = R - 23
            nx = cx + num_r * math.sin(angle)
            ny = cy - num_r * math.cos(angle)
            text = str(num)
            tb = draw.textbbox((0, 0), text, font=font_num)
            tw, th = tb[2]-tb[0], tb[3]-tb[1]
            draw.text((nx - tw/2, ny - th/2 - 2), text, font=font_num, fill=(255, 255, 255))

        # Minute ticks (small dots)
        for i in range(60):
            if i % 5 == 0:
                continue
            angle = math.radians(i * 6)
            outer_r = R - 6
            inner_r = R - 9
            x1 = cx + outer_r * math.sin(angle)
            y1 = cy - outer_r * math.cos(angle)
            x2 = cx + inner_r * math.sin(angle)
            y2 = cy - inner_r * math.cos(angle)
            draw.line((x1, y1, x2, y2), fill=(90, 120, 160), width=1)

        # Hour hand
        draw.line((cx, cy, cx + 38*math.sin(math.radians(hr)), cy - 38*math.cos(math.radians(hr))),
                  fill=(255, 255, 255), width=5)
        # Minute hand
        draw.line((cx, cy, cx + 62*math.sin(math.radians(min_)), cy - 62*math.cos(math.radians(min_))),
                  fill=(230, 200, 110), width=3)
        # Second hand
        draw.line((cx, cy, cx + 72*math.sin(math.radians(sec_)), cy - 72*math.cos(math.radians(sec_))),
                  fill=(223, 0, 94), width=2)

        # Center hub
        draw.ellipse((cx-6, cy-6, cx+6, cy+6), fill=(201, 162, 39))
        draw.ellipse((cx-2, cy-2, cx+2, cy+2), fill=(255, 255, 255))

        clock.save(os.path.join(BASE_DIR, "clock_new4.png"))

    def working(self):
        now = datetime.now()
        h = now.time().hour
        m = now.time().minute
        s = now.time().second

        hr = ((h % 12) / 12) * 360 + (m / 60) * 30
        min_ = (m / 60) * 360
        sec_ = (s / 60) * 360

        self.clock_image(hr, min_, sec_)
        self.img = ImageTk.PhotoImage(file=os.path.join(BASE_DIR, "clock_new4.png"))
        self.lbl.config(image=self.img)

        # 12-hour digital readout with AM/PM
        self.digital_lbl.config(text=now.strftime("%I:%M:%S %p"))
        self.date_lbl.config(text=now.strftime("%A, %d %B %Y"))

        self.lbl.after(200, self.working)


    #  THis function is for open register window
    def reg(self):
        self.new_window=Toplevel(self.root)
        self.app=Register(self.new_window)
        self.new_window.state('zoomed')

    #  THis function is for open login frame
    def login(self):
        if (self.txtuser.get()=="" or self.txtpwd.get()==""):
            messagebox.showerror("Error","All fields required!")
        elif(self.txtuser.get()=="admin" and self.txtpwd.get()=="admin"):
            messagebox.showinfo("Sussessfully","Welcome to Face Recognition Management System")
        else:
            # messagebox.showerror("Error","Please Check Username or Password !")
            conn = mysql.connector.connect(user='root', password='itsmesim',host='localhost',database='face_recognizer',port=3306)
            mycursor = conn.cursor()
            mycursor.execute("select * from regteach where email=%s and pwd=%s",(
                self.txtuser.get(),
                self.txtpwd.get()
            ))
            row=mycursor.fetchone()
            if row==None:
                messagebox.showerror("Error","Invalid email and password!")
            else:
                open_min=messagebox.askyesno("Admin","Succesful! Do yo want continue")
                if open_min>0:
                    self.new_window=Toplevel(self.root)
                    self.app=Face_Recognition_System(self.new_window)
                else:
                    if not open_min:
                        return
            conn.commit()
            conn.close()
#=======================Reset Passowrd Function=============================
    def reset_pass(self):
        if self.var_ssq.get()=="Select":
            messagebox.showerror("Error","Choose a security question!",parent=self.root2)
        elif(self.var_sa.get()==""):
            messagebox.showerror("Error","Please enter your answer!",parent=self.root2)
        elif(self.var_pwd.get()==""):
            messagebox.showerror("Error","Please enter a new password!",parent=self.root2)
        else:
            conn = mysql.connector.connect(user='root', password='itsmesim',host='localhost',database='face_recognizer',port=3306)
            mycursor = conn.cursor()
            query=("select * from regteach where email=%s and ss_que=%s and s_ans=%s")
            value=(self.txtuser.get(),self.var_ssq.get(),self.var_sa.get())
            mycursor.execute(query,value)
            row=mycursor.fetchone()
            if row==None:
                messagebox.showerror("Error","Please enter the correct answer!",parent=self.root2)
            else:
                query=("update regteach set pwd=%s where email=%s")
                value=(self.var_pwd.get(),self.txtuser.get())
                mycursor.execute(query,value)

                conn.commit()
                conn.close()
                messagebox.showinfo("Info","Successfully Your password has been reset, Please login with a new Password!",parent=self.root2)
                



# =====================Forget window=========================================
    def forget_pwd(self):
        if self.txtuser.get()=="":
            messagebox.showerror("Error","Please enter Email ID to reset Password!")
        else:
            conn = mysql.connector.connect(user='root', password='itsmesim',host='localhost',database='face_recognizer',port=3306)
            mycursor = conn.cursor()
            query=("select * from regteach where email=%s")
            value=(self.txtuser.get(),)
            mycursor.execute(query,value)
            row=mycursor.fetchone()
            # print(row)

            if row==None:
                messagebox.showerror("Error","Please enter a valid email ID!")
            else:
                conn.close()
                self.root2=Toplevel()
                self.root2.title("Forget MK")
                self.root2.geometry("350x450+80+120")
                l=Label(self.root2,text="Forgot password",font=("times new roman",25,"bold"),fg="#fff",bg="#002B53")
                l.place(x=0,y=10,relwidth=1)
                # -------------------fields-------------------
                #label1 
                ssq =lb1= Label(self.root2,text="Select a security question:",font=("times new roman",15,"bold"),fg="#002B53",bg="#F2F2F2")
                ssq.place(x=45,y=80)

                #Combo Box1
                self.combo_security = ttk.Combobox(self.root2,textvariable=self.var_ssq,font=("times new roman",15,"bold"),state="readonly")
                self.combo_security["values"]=("Select","Date of birth","Nick Name","Favorite books")
                self.combo_security.current(0)
                self.combo_security.place(x=45,y=110,width=270)


                #label2 
                sa =lb1= Label(self.root2,text="Answer:",font=("times new roman",15,"bold"),fg="#002B53",bg="#F2F2F2")
                sa.place(x=45,y=150)

                #entry2 
                self.txtpwd=ttk.Entry(self.root2,textvariable=self.var_sa,font=("times new roman",15,"bold"))
                self.txtpwd.place(x=45,y=180,width=270)

                #label2 
                new_pwd =lb1= Label(self.root2,text="new password:",font=("times new roman",15,"bold"),fg="#002B53",bg="#F2F2F2")
                new_pwd.place(x=45,y=220)

                #entry2 
                self.new_pwd=ttk.Entry(self.root2,textvariable=self.var_pwd,font=("times new roman",15,"bold"))
                self.new_pwd.place(x=45,y=250,width=270)

                # Creating Button New Password
                loginbtn=Button(self.root2,command=self.reset_pass,text="Reset pass",font=("times new roman",15,"bold"),bd=0,relief=RIDGE,fg="#fff",bg="#002B53",activeforeground="white",activebackground="#007ACC")
                loginbtn.place(x=45,y=300,width=270,height=35)


            

# =====================main program Face deteion system====================

class Face_Recognition_System:
    def __init__(self,root):
        self.root=root
        self.root.state('zoomed')
        self.root.title("Attendance management system using facial recognition")

        # Fit to the actual screen size, not a hardcoded 1280x800 canvas
        self.screen_w = self.root.winfo_screenwidth()
        self.screen_h = self.root.winfo_screenheight()
        self.root.geometry(f"{self.screen_w}x{self.screen_h}+0+0")

# This part is image labels setting start 
        # first header image  
        img=safe_open_image(os.path.join("data_img", "app_banner.png"), (self.screen_w, 130))
        img=img.resize((self.screen_w,130),Image.LANCZOS)
        self.photoimg=ImageTk.PhotoImage(img)

        # set image as lable
        f_lb1 = Label(self.root,image=self.photoimg)
        f_lb1.place(x=0,y=0,width=self.screen_w,height=130)

        # backgorund image 
        body_h = self.screen_h - 130
        bg1=safe_open_image(os.path.join("data_img", "app_bg.png"), (self.screen_w, body_h))
        bg1=bg1.resize((self.screen_w,body_h),Image.LANCZOS)
        self.photobg1=ImageTk.PhotoImage(bg1)

        # set image as lable
        bg_img = Label(self.root,image=self.photobg1)
        bg_img.place(x=0,y=130,width=self.screen_w,height=body_h)


        #title section
        title_lb1 = Label(bg_img,text="Face recognition attendance system",font=("verdana",20,"bold"),bg="navyblue",fg="white")
        title_lb1.place(x=0,y=0,relwidth=1,height=40)

        # Center the button grid (designed for a 1280-wide canvas) within the real screen width
        self.offx = max(0, (self.screen_w - 1280) // 2)

        # Create buttons below the section 
        # ------------------------------------------------------------------------------------------------------------------- 
        # student button 1
        std_img_btn = safe_open_image(os.path.join("data_img", "student.jpeg"), (220, 220))
        std_img_btn = std_img_btn.resize((220, 220), Image.LANCZOS)
        self.std_img1 = ImageTk.PhotoImage(std_img_btn)

        std_b1 = Button(bg_img, command=self.student_pannels, image=self.std_img1, cursor="hand2")
        std_b1.place(x=220+self.offx, y=70, width=220, height=180)

        std_b1_1 = Button(bg_img, command=self.student_pannels, text="Student", cursor="hand2",
                          font=("tahoma", 15, "bold"), bg="white", fg="navyblue")
        std_b1_1.place(x=220+self.offx, y=220, width=220, height=40)

        # Detect Face  button 2
        det_img_btn = safe_open_image(os.path.join("data_img", "recognition.jpg"), (220, 220))
        det_img_btn = det_img_btn.resize((220, 220), Image.LANCZOS)
        self.det_img1 = ImageTk.PhotoImage(det_img_btn)

        det_b1 = Button(bg_img, command=self.face_rec, image=self.det_img1, cursor="hand2", )
        det_b1.place(x=480+self.offx, y=70, width=220, height=180)

        det_b1_1 = Button(bg_img, command=self.face_rec, text="Recognition", cursor="hand2",font=("tahoma", 15, "bold"), bg="white", fg="navyblue")
        det_b1_1.place(x=480+self.offx, y=220, width=220, height=40)

        # Attendance System  button 3
        att_img_btn = safe_open_image(os.path.join("data_img", "attendence.png"), (220, 220))
        att_img_btn = att_img_btn.resize((220, 220), Image.LANCZOS)
        self.att_img1 = ImageTk.PhotoImage(att_img_btn)

        att_b1 = Button(bg_img, command=self.attendance_pannel, image=self.att_img1, cursor="hand2", )
        att_b1.place(x=740+self.offx, y=70, width=220, height=180)

        att_b1_1 = Button(bg_img, command=self.attendance_pannel, text="Attendance", cursor="hand2",font=("tahoma", 15, "bold"), bg="white", fg="navyblue")
        att_b1_1.place(x=740+self.offx, y=220, width=220, height=40)

        tra_img_btn = safe_open_image(os.path.join("data_img", "train_data.png"), (220, 220))
        tra_img_btn = tra_img_btn.resize((220, 220), Image.LANCZOS)
        self.tra_img1 = ImageTk.PhotoImage(tra_img_btn)

        tra_b1 = Button(bg_img, command=self.train_pannels, image=self.tra_img1, cursor="hand2", )
        tra_b1.place(x=220+self.offx, y=270, width=220, height=180)

        tra_b1_1 = Button(bg_img, command=self.train_pannels, text="Train Data", cursor="hand2",font=("tahoma", 15, "bold"), bg="white", fg="navyblue")
        tra_b1_1.place(x=220+self.offx, y=420, width=220, height=40)

        # Photo   button 6
        pho_img_btn = safe_open_image(os.path.join("data_img", "dataset.png"), (220, 220))
        pho_img_btn = pho_img_btn.resize((220, 220), Image.LANCZOS)
        self.pho_img1 = ImageTk.PhotoImage(pho_img_btn)

        pho_b1 = Button(bg_img, command=self.open_img, image=self.pho_img1, cursor="hand2", )
        pho_b1.place(x=480+self.offx, y=270, width=220, height=180)

        pho_b1_1 = Button(bg_img, command=self.open_img, text="Faces Data", cursor="hand2", font=("tahoma", 15, "bold"),bg="white", fg="navyblue")
        pho_b1_1.place(x=480+self.offx, y=420, width=220, height=40)

        # exit   button 8
        exi_img_btn = safe_open_image(os.path.join("data_img", "exit.png"), (220, 220))
        exi_img_btn = exi_img_btn.resize((220, 220), Image.LANCZOS)
        self.exi_img1 = ImageTk.PhotoImage(exi_img_btn)

        exi_b1 = Button(bg_img, command=self.Close, image=self.exi_img1, cursor="hand2", )
        exi_b1.place(x=740+self.offx, y=270, width=220, height=180)

        exi_b1_1 = Button(bg_img, command=self.Close, text="Exit", cursor="hand2", font=("tahoma", 15, "bold"),bg="white", fg="navyblue")
        exi_b1_1.place(x=740+self.offx, y=420, width=220, height=40)
# ==================Funtion for Open Images Folder==================
    def open_img(self):
        faces_dir = os.path.join(BASE_DIR, "Faces_img")
        os.makedirs(faces_dir, exist_ok=True)  # in case no student has been captured yet
        os.startfile(faces_dir)
# ==================Functions Buttons=====================
    def student_pannels(self):
        self.new_window=Toplevel(self.root)
        self.app=Student(self.new_window)
        self.new_window.state('zoomed')

    def train_pannels(self):
        self.new_window=Toplevel(self.root)
        self.app=Train(self.new_window)
        self.new_window.state('zoomed')
        
    def face_rec(self):
        self.new_window=Toplevel(self.root)
        self.app=Face_Recognition(self.new_window)
        self.new_window.state('zoomed')

    def attendance_pannel(self):
        self.new_window=Toplevel(self.root)
        self.app=Attendance(self.new_window)
        self.new_window.state('zoomed')


    def Close(self):
        root.destroy()


if __name__ == "__main__":
    root=Tk()
    app=Login(root)
    root.mainloop()
    