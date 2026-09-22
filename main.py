from tkinter import *
from tkinter import messagebox
from PIL import Image, ImageTk
import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Import your modules/classes correctly
from student import Student
from attendance import Attendance
from train import Train       
from face_recognition import Face_Recognition  

class Face_Recognition_System:
    def __init__(self, root):
        self.root = root
        self.root.state('zoomed')
        self.root.title("Attendance Management System using Facial Recognition")

        # ===== Header Image =====
        header_img_path = os.path.join(BASE_DIR, "data_img", "app_banner.png")
        header_img = Image.open(header_img_path)
        header_img = header_img.resize((1280, 130), Image.LANCZOS)
        self.photoimg = ImageTk.PhotoImage(header_img)
        header_lbl = Label(self.root, image=self.photoimg)
        header_lbl.place(x=0, y=0, width=1280, height=130)

        # ===== Background Image =====
        bg_img_path = os.path.join(BASE_DIR, "data_img", "app_bg.png")
        bg_img = Image.open(bg_img_path)
        bg_img = bg_img.resize((1280, 500), Image.LANCZOS)
        self.photobg = ImageTk.PhotoImage(bg_img)
        bg_label = Label(self.root, image=self.photobg)
        bg_label.place(x=0, y=145, width=1280, height=500)

        # ===== Title =====
        title_lb = Label(bg_label, text="Face Recognition Attendance System", font=("Verdana", 20, "bold"), bg="navyblue", fg="white")
        title_lb.place(x=0, y=0, width=1280, height=40)

        # ===== Buttons with Images =====
        buttons = [
            (220, 70, os.path.join(BASE_DIR, "data_img", "student.jpeg"), "Student", self.student_panel),
            (480, 70, os.path.join(BASE_DIR, "data_img", "recognition.jpg"), "Recognition", self.recognition_panel),
            (740, 70, os.path.join(BASE_DIR, "data_img", "attendence.png"), "Attendance", self.attendance_panel),
            (220, 270, os.path.join(BASE_DIR, "data_img", "train_data.png"), "Train Data", self.train_panel),
            (480, 270, os.path.join(BASE_DIR, "data_img", "dataset.png"), "Dataset", self.open_dataset),
            (740, 270, os.path.join(BASE_DIR, "data_img", "exit.png"), "Exit", self.close_app)
        ]

        for x, y, img_path, text, cmd in buttons:
            self.add_button(bg_label, x, y, img_path, text, cmd)

    # ===== Helper to create buttons =====
    def add_button(self, parent, x, y, image_path, text, command):
        img = Image.open(image_path)
        img = img.resize((220, 220), Image.LANCZOS)
        photo = ImageTk.PhotoImage(img)
        btn = Button(parent, image=photo, command=command, cursor="hand2")
        btn.image = photo  # Keep reference to avoid garbage collection
        btn.place(x=x, y=y, width=220, height=180)
        btn_text = Button(parent, text=text, command=command, cursor="hand2",
                          font=("Tahoma", 15, "bold"), bg="white", fg="navyblue")
        btn_text.place(x=x, y=y+150, width=220, height=40)

    # ===== Button Functions =====
    def student_panel(self):
        new_window = Toplevel(self.root)
        Student(new_window)
        new_window.state('zoomed')

    def attendance_panel(self):
        new_window = Toplevel(self.root)
        Attendance(new_window)
        new_window.state('zoomed')

    def recognition_panel(self):
        new_window = Toplevel(self.root)
        Face_Recognition(new_window)
        new_window.state('zoomed')

    def train_panel(self):
        new_window = Toplevel(self.root)
        Train(new_window)
        new_window.state('zoomed')


    def open_dataset(self):
        folder_path = os.path.join(BASE_DIR, "data_img")
        if os.path.exists(folder_path) and os.path.isdir(folder_path):
            try:
                os.startfile(folder_path)
            except Exception as e:
                messagebox.showerror("Error", f"Unable to open folder!\nError: {str(e)}")
        else:
            messagebox.showerror("Error", "Dataset folder not found!")

    def close_app(self):
        self.root.destroy()


if __name__ == "__main__":
    root = Tk()
    obj = Face_Recognition_System(root)
    root.mainloop()
