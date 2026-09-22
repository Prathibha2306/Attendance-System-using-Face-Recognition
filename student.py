# student.py

from tkinter import *
from tkinter import ttk, messagebox, filedialog
import mysql.connector
import csv
import os
import cv2

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

student_data = []

class Student:
    def __init__(self, root):
        self.root = root
        self.root.title("Student Management")
        self.root.state('zoomed')

        # ====== Variables ======
        self.var_id = StringVar()
        self.var_roll = StringVar()
        self.var_name = StringVar()
        self.var_section = StringVar()
        self.var_dep = StringVar()

        # ====== Title ======
        title_lb = Label(self.root, text="Student Management System", font=("Verdana", 20, "bold"), bg="navy", fg="white")
        title_lb.pack(side=TOP, fill=X)

        # ====== Main Frame (fills whatever screen size is available) ======
        main_frame = Frame(self.root, bd=2, bg="white", relief=RIDGE)
        main_frame.place(x=10, y=60, relwidth=1, relheight=1, width=-20, height=-70)

        # ====== Left Frame: Student Form ======
        left_frame = LabelFrame(main_frame, text="Student Details", font=("Verdana", 12, "bold"), bg="white", fg="navy", bd=2, relief=RIDGE)
        left_frame.place(x=10, y=10, width=600, height=580)

        Label(left_frame, text="Student ID:", font=("Verdana", 12, "bold"), bg="white", fg="navy").grid(row=0, column=0, padx=10, pady=10, sticky=W)
        Entry(left_frame, textvariable=self.var_id, font=("Verdana", 12), width=20).grid(row=0, column=1, padx=10, pady=10)

        Label(left_frame, text="Roll No:", font=("Verdana", 12, "bold"), bg="white", fg="navy").grid(row=1, column=0, padx=10, pady=10, sticky=W)
        Entry(left_frame, textvariable=self.var_roll, font=("Verdana", 12), width=20).grid(row=1, column=1, padx=10, pady=10)

        Label(left_frame, text="Name:", font=("Verdana", 12, "bold"), bg="white", fg="navy").grid(row=2, column=0, padx=10, pady=10, sticky=W)
        Entry(left_frame, textvariable=self.var_name, font=("Verdana", 12), width=20).grid(row=2, column=1, padx=10, pady=10)

        Label(left_frame, text="Section:", font=("Verdana", 12, "bold"), bg="white", fg="navy").grid(row=3, column=0, padx=10, pady=10, sticky=W)
        section_combo = ttk.Combobox(left_frame, textvariable=self.var_section, font=("Verdana", 12), width=17, state="readonly")
        section_combo["values"] = ("A", "B", "C", "D")
        section_combo.grid(row=3, column=1, padx=10, pady=10)

        Label(left_frame, text="Department:", font=("Verdana", 12, "bold"), bg="white", fg="navy").grid(row=4, column=0, padx=10, pady=10, sticky=W)
        Entry(left_frame, textvariable=self.var_dep, font=("Verdana", 12), width=20).grid(row=4, column=1, padx=10, pady=10)

        # ====== Buttons ======
        btn_frame = Frame(left_frame, bg="white")
        btn_frame.place(x=10, y=250, width=560, height=50)

        Button(btn_frame, text="Add", command=self.add_student, font=("Verdana", 12, "bold"), bg="green", fg="white", width=12).grid(row=0, column=0, padx=5)
        Button(btn_frame, text="Update", command=self.update_student, font=("Verdana", 12, "bold"), bg="blue", fg="white", width=12).grid(row=0, column=1, padx=5)
        Button(btn_frame, text="Delete", command=self.delete_student, font=("Verdana", 12, "bold"), bg="red", fg="white", width=12).grid(row=0, column=2, padx=5)
        Button(btn_frame, text="Reset", command=self.reset_fields, font=("Verdana", 12, "bold"), bg="orange", fg="white", width=12).grid(row=0, column=3, padx=5)

        # ====== Import/Export Buttons ======
        btn_csv_frame = Frame(left_frame, bg="white")
        btn_csv_frame.place(x=10, y=310, width=560, height=50)

        Button(btn_csv_frame, text="Import CSV", command=self.import_csv, font=("Verdana", 12, "bold"), bg="purple", fg="white", width=12).grid(row=0, column=0, padx=5)
        Button(btn_csv_frame, text="Export CSV", command=self.export_csv, font=("Verdana", 12, "bold"), bg="brown", fg="white", width=12).grid(row=0, column=1, padx=5)

        # ====== Face Capture Button ======
        btn_face_frame = Frame(left_frame, bg="white")
        btn_face_frame.place(x=10, y=370, width=560, height=50)

        Button(btn_face_frame, text="Capture Faces", command=self.capture_faces, font=("Verdana", 12, "bold"), bg="navy", fg="white", width=25).grid(row=0, column=0, padx=5)

        # ====== Right Frame: Student Table ======
        right_frame = LabelFrame(main_frame, text="Student Records", font=("Verdana", 12, "bold"), bg="white", fg="navy", bd=2, relief=RIDGE)
        right_frame.place(x=620, y=10, width=610, height=580)

        table_frame = Frame(right_frame, bg="white")
        table_frame.place(x=10, y=10, width=580, height=550)

        scroll_x = ttk.Scrollbar(table_frame, orient=HORIZONTAL)
        scroll_y = ttk.Scrollbar(table_frame, orient=VERTICAL)

        self.student_table = ttk.Treeview(table_frame, columns=("id", "roll", "name", "section", "dep"), xscrollcommand=scroll_x.set, yscrollcommand=scroll_y.set)
        scroll_x.pack(side=BOTTOM, fill=X)
        scroll_y.pack(side=RIGHT, fill=Y)
        scroll_x.config(command=self.student_table.xview)
        scroll_y.config(command=self.student_table.yview)

        self.student_table.heading("id", text="ID")
        self.student_table.heading("roll", text="Roll No")
        self.student_table.heading("name", text="Name")
        self.student_table.heading("section", text="Section")
        self.student_table.heading("dep", text="Department")
        self.student_table["show"] = "headings"

        self.student_table.column("id", width=50)
        self.student_table.column("roll", width=100)
        self.student_table.column("name", width=150)
        self.student_table.column("section", width=60)
        self.student_table.column("dep", width=100)

        self.student_table.pack(fill=BOTH, expand=1)
        self.student_table.bind("<ButtonRelease-1>", self.get_cursor)

        self.fetch_students()

    # ================== Database Functions ==================
    def add_student(self):
        if self.var_id.get() == "" or self.var_roll.get() == "" or self.var_name.get() == "" or self.var_section.get() == "" or self.var_dep.get() == "":
            messagebox.showerror("Error", "All fields are required!", parent=self.root)
        else:
            try:
                conn = mysql.connector.connect(host='localhost', user='root', password='itsmesim', database='face_recognizer', port=3306)
                mycursor = conn.cursor()
                mycursor.execute("INSERT INTO student (id, roll_no, name, section, department) VALUES (%s,%s,%s,%s,%s)", (
                    self.var_id.get(),
                    self.var_roll.get(),
                    self.var_name.get(),
                    self.var_section.get(),
                    self.var_dep.get()
                ))
                conn.commit()
                self.fetch_students()
                conn.close()
                messagebox.showinfo("Success", "Student added successfully!", parent=self.root)
            except Exception as e:
                messagebox.showerror("Error", f"Error due to: {str(e)}", parent=self.root)

    def fetch_students(self):
        try:
            conn = mysql.connector.connect(host='localhost', user='root', password='itsmesim', database='face_recognizer', port=3306)
            mycursor = conn.cursor()
            mycursor.execute("SELECT * FROM student")
            rows = mycursor.fetchall()
            if len(rows) != 0:
                self.student_table.delete(*self.student_table.get_children())
                for row in rows:
                    self.student_table.insert("", END, values=row)
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", f"Error due to: {str(e)}", parent=self.root)

    def get_cursor(self, event=""):
        cursor_focus = self.student_table.focus()
        content = self.student_table.item(cursor_focus)
        data = content["values"]
        if data:
            self.var_id.set(data[0])
            self.var_roll.set(data[1])
            self.var_name.set(data[2])
            self.var_section.set(data[3])
            self.var_dep.set(data[4])

    def update_student(self):
        if self.var_id.get() == "" or self.var_roll.get() == "" or self.var_name.get() == "" or self.var_section.get() == "" or self.var_dep.get() == "":
            messagebox.showerror("Error", "All fields are required!", parent=self.root)
        else:
            try:
                conn = mysql.connector.connect(host='localhost', user='root', password='itsmesim', database='face_recognizer', port=3306)
                mycursor = conn.cursor()
                mycursor.execute("UPDATE student SET roll_no=%s, name=%s, section=%s, department=%s WHERE id=%s", (
                    self.var_roll.get(),
                    self.var_name.get(),
                    self.var_section.get(),
                    self.var_dep.get(),
                    self.var_id.get()
                ))
                conn.commit()
                self.fetch_students()
                conn.close()
                messagebox.showinfo("Success", "Student updated successfully!", parent=self.root)
            except Exception as e:
                messagebox.showerror("Error", f"Error due to: {str(e)}", parent=self.root)

    def delete_student(self):
        if self.var_id.get() == "":
            messagebox.showerror("Error", "Student ID is required", parent=self.root)
        else:
            try:
                delete = messagebox.askyesno("Delete", "Do you want to delete this student?", parent=self.root)
                if delete > 0:
                    conn = mysql.connector.connect(host='localhost', user='root', password='itsmesim', database='face_recognizer', port=3306)
                    mycursor = conn.cursor()
                    mycursor.execute("DELETE FROM student WHERE id=%s", (self.var_id.get(),))
                    conn.commit()
                    conn.close()
                    self.fetch_students()
                    self.reset_fields()
            except Exception as e:
                messagebox.showerror("Error", f"Error due to: {str(e)}", parent=self.root)

    def reset_fields(self):
        self.var_id.set("")
        self.var_roll.set("")
        self.var_name.set("")
        self.var_section.set("")
        self.var_dep.set("")

    # ================== CSV Functions ==================
    def import_csv(self):
        global student_data
        student_data.clear()
        file_path = filedialog.askopenfilename(initialdir=os.getcwd(), title="Open CSV", filetypes=(("CSV File", "*.csv"), ("All files", "*.*")), parent=self.root)
        if file_path:
            with open(file_path, newline="") as file:
                csv_reader = csv.reader(file)
                for row in csv_reader:
                    student_data.append(row)
            self.insert_csv_to_db(student_data)
            self.fetch_students()

    def insert_csv_to_db(self, rows):
        try:
            conn = mysql.connector.connect(host='localhost', user='root', password='itsmesim', database='face_recognizer', port=3306)
            mycursor = conn.cursor()
            for row in rows:
                if len(row) == 5:  # id, roll_no, name, section, department
                    mycursor.execute("INSERT INTO student (id, roll_no, name, section, department) VALUES (%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE roll_no=%s, name=%s, section=%s, department=%s", (
                        row[0], row[1], row[2], row[3], row[4], row[1], row[2], row[3], row[4]
                    ))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "CSV data imported into database!", parent=self.root)
        except Exception as e:
            messagebox.showerror("Error", f"Error due to: {str(e)}", parent=self.root)

    def export_csv(self):
        global student_data
        try:
            if len(student_data) == 0:
                messagebox.showerror("Error", "No data to export", parent=self.root)
                return
            file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV file", "*.csv")])
            with open(file_path, mode="w", newline="") as file:
                csv_writer = csv.writer(file)
                for row in student_data:
                    csv_writer.writerow(row)
            messagebox.showinfo("Success", "Data exported successfully", parent=self.root)
        except Exception as e:
            messagebox.showerror("Error", f"Error due to: {str(e)}", parent=self.root)

    # ================== Face Capture Function ==================
    def capture_faces(self):
        student_id = self.var_id.get()
        if student_id == "":
            messagebox.showerror("Error", "Enter/select a Student ID first (Add them if new).", parent=self.root)
            return

        faces_dir = os.path.join(BASE_DIR, "Faces_img")
        os.makedirs(faces_dir, exist_ok=True)

        cascade_path = os.path.join(BASE_DIR, "haarcascade_frontalface_default.xml")
        face_cascade = cv2.CascadeClassifier(cascade_path)

        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            messagebox.showerror("Error", "Could not access webcam.", parent=self.root)
            return

        SAMPLES_NEEDED = 100
        count = 0

        messagebox.showinfo(
            "Capture Faces",
            "Look at the webcam. Capturing will start now and stop automatically\n"
            f"after {SAMPLES_NEEDED} face samples.\n\n"
            "Press Escape any time to stop early.",
            parent=self.root
        )

        while count < SAMPLES_NEEDED:
            ret, frame = cap.read()
            if not ret:
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

            for (x, y, w, h) in faces:
                count += 1
                # NOTE: unlike the old LBPH pipeline, the CNN embedding model
                # (train.py / face_recognition.py) expects a colour face crop,
                # not grayscale. Grayscale detection above still finds the
                # face location (Haar cascades work on intensity only), but
                # we save the crop from the original colour frame.
                face_img = frame[y:y + h, x:x + w]
                filename = os.path.join(faces_dir, f"user.{student_id}.{count}.jpg")
                cv2.imwrite(filename, face_img)

                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(frame, f"Samples: {count}/{SAMPLES_NEEDED}", (x, y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                break  # only take one face per frame to avoid duplicate saves

            cv2.imshow("Capturing Faces - Press Escape to stop", frame)

            key = cv2.waitKey(1) & 0xFF
            if key == 27:  # Escape
                break
            if cv2.getWindowProperty("Capturing Faces - Press Escape to stop", cv2.WND_PROP_VISIBLE) < 1:
                break

        cap.release()
        cv2.destroyAllWindows()

        if count > 0:
            messagebox.showinfo(
                "Done",
                f"Captured {count} face samples for Student ID {student_id}.\n"
                "You can now go to 'Train Data' to train the recognizer.",
                parent=self.root
            )
        else:
            messagebox.showwarning("No Faces Captured", "No face samples were saved.", parent=self.root)
