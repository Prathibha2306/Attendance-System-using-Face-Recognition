import os
import csv
from tkinter import *
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import mysql.connector
from datetime import datetime
from tkcalendar import DateEntry

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Global variable for CSV data
mydata = []

class Attendance:
    def __init__(self, root):
        self.root = root
        self.root.title("Smart Attendance Management System using Facial Recognition")
        self.root.state("zoomed")

        # Fit to the actual screen size
        self.screen_w = self.root.winfo_screenwidth()
        self.screen_h = self.root.winfo_screenheight()
        self.root.geometry(f"{self.screen_w}x{self.screen_h}+0+0")

        # ============== Variables ==============
        self.var_id = StringVar()
        self.var_roll = StringVar()
        self.var_name = StringVar()
        self.var_subject = StringVar()
        self.var_section = StringVar()
        self.var_time = StringVar()
        self.var_date = StringVar()
        self.var_attend = StringVar(value="Status")

        # ---- Filter variables ----
        self.filter_date = StringVar()
        self.filter_roll = StringVar()
        self.filter_subject = StringVar()
        self.filter_section = StringVar(value="All")
        self.filter_status = StringVar(value="All")
        self.filter_all_dates = BooleanVar(value=False)

        # ============== Header Image ==============
        try:
            img = Image.open(os.path.join(BASE_DIR, "data_img", "app_banner.png"))
            img = img.resize((self.screen_w, 130), Image.LANCZOS)
            self.photoimg = ImageTk.PhotoImage(img)
        except Exception as e:
            print("Error loading header image:", e)
            self.photoimg = None

        if self.photoimg:
            f_lb1 = Label(self.root, image=self.photoimg)
            f_lb1.place(x=0, y=0, width=self.screen_w, height=130)

        # ============== Background Frame (fills the rest of the screen) ==============
        bg_img = Frame(self.root, bg="lightgray")
        bg_img.place(x=0, y=130, relwidth=1, relheight=1, height=-130)

        # Title
        title_lb1 = Label(bg_img, text="Attendance Management", font=("verdana", 20, "bold"),
                          bg="navyblue", fg="white")
        title_lb1.place(x=0, y=0, relwidth=1, height=40)

        # Main Frame
        main_frame = Frame(bg_img, bd=2, bg="white")
        main_frame.place(x=0, y=40, relwidth=1, relheight=1, height=-40)

        # ============== Left Frame (Student Data) ==============
        left_frame = LabelFrame(main_frame, bd=2, bg="white", relief=RIDGE, text="Recognized Today (auto-marked by Face Recognition)",
                                font=("verdana", 12, "bold"), fg="navyblue")
        left_frame.place(x=10, y=10, width=640, height=430)

        # Labels and Entry Fields
        Label(left_frame, text="Student ID:", font=("verdana", 12, "bold"), fg="navyblue", bg="white").grid(row=0, column=0, padx=5, pady=5, sticky=W)
        ttk.Entry(left_frame, textvariable=self.var_id, width=15, font=("verdana", 12, "bold")).grid(row=0, column=1, padx=5, pady=5)

        Label(left_frame, text="Roll No:", font=("verdana", 12, "bold"), fg="navyblue", bg="white").grid(row=0, column=2, padx=5, pady=5, sticky=W)
        ttk.Entry(left_frame, textvariable=self.var_roll, width=15, font=("verdana", 12, "bold")).grid(row=0, column=3, padx=5, pady=5)

        Label(left_frame, text="Name:", font=("verdana", 12, "bold"), fg="navyblue", bg="white").grid(row=1, column=0, padx=5, pady=5, sticky=W)
        ttk.Entry(left_frame, textvariable=self.var_name, width=15, font=("verdana", 12, "bold")).grid(row=1, column=1, padx=5, pady=5)

        Label(left_frame, text="Subject:", font=("verdana", 12, "bold"), fg="navyblue", bg="white").grid(row=1, column=2, padx=5, pady=5, sticky=W)
        manual_subject_combo = ttk.Combobox(left_frame, textvariable=self.var_subject, width=13, font=("verdana", 11, "bold"), state="readonly")
        manual_subject_combo["values"] = ("Deep Learning", "Cloud Computing and Security", "PEC", "OEC")
        manual_subject_combo.grid(row=1, column=3, padx=5, pady=5)

        Label(left_frame, text="Time:", font=("verdana", 12, "bold"), fg="navyblue", bg="white").grid(row=2, column=0, padx=5, pady=5, sticky=W)
        ttk.Entry(left_frame, textvariable=self.var_time, width=15, font=("verdana", 12, "bold")).grid(row=2, column=1, padx=5, pady=5)

        Label(left_frame, text="Date:", font=("verdana", 12, "bold"), fg="navyblue", bg="white").grid(row=2, column=2, padx=5, pady=5, sticky=W)
        ttk.Entry(left_frame, textvariable=self.var_date, width=15, font=("verdana", 12, "bold")).grid(row=2, column=3, padx=5, pady=5)

        Label(left_frame, text="Status:", font=("verdana", 12, "bold"), fg="navyblue", bg="white").grid(row=3, column=0, padx=5, pady=5, sticky=W)
        attend_combo = ttk.Combobox(left_frame, textvariable=self.var_attend, width=13, font=("verdana", 12, "bold"), state="readonly")
        attend_combo["values"] = ("present", "absent")
        attend_combo.current(0)
        attend_combo.grid(row=3, column=1, padx=5, pady=5, sticky=W)

        Label(left_frame, text="Section:", font=("verdana", 12, "bold"), fg="navyblue", bg="white").grid(row=3, column=2, padx=5, pady=5, sticky=W)
        section_combo = ttk.Combobox(left_frame, textvariable=self.var_section, width=13, font=("verdana", 12, "bold"), state="readonly")
        section_combo["values"] = ("A", "B", "C", "D")
        section_combo.grid(row=3, column=3, padx=5, pady=5, sticky=W)

        # ============== Left Table (Recognized Today) ==============
        table_frame = Frame(left_frame, bd=2, bg="white", relief=RIDGE)
        table_frame.place(x=10, y=140, width=615, height=240)

        scroll_x = ttk.Scrollbar(table_frame, orient=HORIZONTAL)
        scroll_y = ttk.Scrollbar(table_frame, orient=VERTICAL)
        self.attendanceReport_left = ttk.Treeview(table_frame,
                                                  columns=("ID", "Roll_No", "Name", "Section", "Subject", "Time", "Date", "Attend"),
                                                  xscrollcommand=scroll_x.set, yscrollcommand=scroll_y.set)
        scroll_x.pack(side=BOTTOM, fill=X)
        scroll_y.pack(side=RIGHT, fill=Y)
        scroll_x.config(command=self.attendanceReport_left.xview)
        scroll_y.config(command=self.attendanceReport_left.yview)

        for col, width in zip(("ID", "Roll_No", "Name", "Section", "Subject", "Time", "Date", "Attend"), (40, 55, 80, 55, 80, 60, 60, 65)):
            self.attendanceReport_left.heading(col, text=col)
            self.attendanceReport_left.column(col, width=width)
        self.attendanceReport_left["show"] = "headings"
        self.attendanceReport_left.pack(fill=BOTH, expand=1)
        self.attendanceReport_left.bind("<ButtonRelease>", self.get_cursor_left)

        # Buttons
        Label(left_frame, text="Fill in the fields above (or select a row) and click 'Add to Database' to insert manually.",
             font=("verdana", 8, "italic"), fg="gray30", bg="white").place(x=10, y=368, width=615, height=15)

        btn_frame = Frame(left_frame, bg="white")
        btn_frame.place(x=10, y=385, width=615, height=40)
        Button(btn_frame, text="⟳ Refresh && Save to Database", command=self.refresh_and_save, width=28, bg="green", fg="white", font=("verdana", 11, "bold")).grid(row=0, column=0, padx=8)
        Button(btn_frame, text="+ Add to Database", command=self.action, width=20, bg="navyblue", fg="white", font=("verdana", 11, "bold")).grid(row=0, column=1, padx=8)

        # ============== Right Frame (MySQL Table) ==============
        right_frame = LabelFrame(main_frame, bd=2, bg="white", relief=RIDGE, text="Database Records",
                                 font=("verdana", 12, "bold"), fg="navyblue")
        right_frame.place(x=660, y=10, width=600, height=430)

        # ---- Filter Row 1: Roll No, Subject, Section ----
        Label(right_frame, text="Roll No:", font=("verdana", 9, "bold"), bg="white", fg="navyblue").place(x=10, y=40)
        ttk.Entry(right_frame, textvariable=self.filter_roll, width=8, font=("verdana", 9)).place(x=68, y=40)

        Label(right_frame, text="Subject:", font=("verdana", 9, "bold"), bg="white", fg="navyblue").place(x=145, y=40)
        subject_filter_combo = ttk.Combobox(right_frame, textvariable=self.filter_subject, width=20,
                                            font=("verdana", 9), state="readonly")
        subject_filter_combo["values"] = ("All", "Deep Learning", "Cloud Computing and Security", "PEC", "OEC")
        subject_filter_combo.current(0)
        subject_filter_combo.place(x=198, y=40)

        Label(right_frame, text="Section:", font=("verdana", 9, "bold"), bg="white", fg="navyblue").place(x=380, y=40)
        section_filter_combo = ttk.Combobox(right_frame, textvariable=self.filter_section, width=4,
                                            font=("verdana", 9), state="readonly")
        section_filter_combo["values"] = ("All", "A", "B", "C", "D")
        section_filter_combo.current(0)
        section_filter_combo.place(x=430, y=40)

        Label(right_frame, text="Status:", font=("verdana", 9, "bold"), bg="white", fg="navyblue").place(x=10, y=70)
        status_filter_combo = ttk.Combobox(right_frame, textvariable=self.filter_status, width=7,
                                           font=("verdana", 9), state="readonly")
        status_filter_combo["values"] = ("All", "present", "absent")
        status_filter_combo.place(x=55, y=70)

        # ---- Filter Row 2 (continued): Date (calendar picker), All Dates toggle, Filter/Clear ----
        Label(right_frame, text="Date:", font=("verdana", 9, "bold"), bg="white", fg="navyblue").place(x=140, y=70)
        self.date_filter_widget = DateEntry(right_frame, width=9, font=("verdana", 9),
                                            date_pattern="dd/mm/yyyy", background="teal",
                                            foreground="white", borderwidth=2)
        self.date_filter_widget.place(x=175, y=70)

        self.all_dates_check = Checkbutton(right_frame, text="All Dates", variable=self.filter_all_dates,
                                           font=("verdana", 9), bg="white", fg="navyblue")
        self.all_dates_check.place(x=280, y=68)

        Button(right_frame, text="Filter", command=self.apply_filters, width=6, bg="teal", fg="white",
              font=("verdana", 9, "bold")).place(x=445, y=68)
        Button(right_frame, text="Clear", command=self.clear_filters, width=6, bg="gray40", fg="white",
              font=("verdana", 9, "bold")).place(x=505, y=68)

        table_frame = Frame(right_frame, bd=2, bg="white", relief=RIDGE)
        table_frame.place(x=10, y=105, width=580, height=315)

        scroll_x = ttk.Scrollbar(table_frame, orient=HORIZONTAL)
        scroll_y = ttk.Scrollbar(table_frame, orient=VERTICAL)
        self.attendanceReport = ttk.Treeview(table_frame,
                                             columns=("ID", "Roll_No", "Name", "Section", "Subject", "Time", "Date", "Attend"),
                                             xscrollcommand=scroll_x.set, yscrollcommand=scroll_y.set)
        scroll_x.pack(side=BOTTOM, fill=X)
        scroll_y.pack(side=RIGHT, fill=Y)
        scroll_x.config(command=self.attendanceReport.xview)
        scroll_y.config(command=self.attendanceReport.yview)

        for col, width in zip(("ID", "Roll_No", "Name", "Section", "Subject", "Time", "Date", "Attend"), (40, 55, 80, 55, 80, 60, 60, 65)):
            self.attendanceReport.heading(col, text=col)
            self.attendanceReport.column(col, width=width)
        self.attendanceReport["show"] = "headings"
        self.attendanceReport.pack(fill=BOTH, expand=1)
        self.attendanceReport.bind("<ButtonRelease>", self.get_cursor_right)

        Button(right_frame, text="Edit", command=self.update_data, width=12, bg="navyblue", fg="white", font=("verdana", 12, "bold")).place(x=10, y=10)
        Button(right_frame, text="Delete", command=self.delete_data, width=12, bg="navyblue", fg="white", font=("verdana", 12, "bold")).place(x=130, y=10)
        Button(right_frame, text="Export Report", command=self.export_report, width=14, bg="purple", fg="white", font=("verdana", 12, "bold")).place(x=250, y=10)

        # Load today's attendance by default (not the full history) and any pending recognitions
        self.apply_filters()
        self.load_pending()

    # ===================== CSV Import/Export =====================
    def fetchData(self, rows):
        global mydata
        mydata = rows
        self.attendanceReport_left.delete(*self.attendanceReport_left.get_children())
        for i in rows:
            self.attendanceReport_left.insert("", END, values=i)

    # ===================== Pending Recognitions Queue =====================
    def load_pending(self):
        """Loads faces recognized by the Recognition screen (pending_attendance.csv)
        into the left table, waiting for the admin to confirm Present/Absent."""
        global mydata
        pending_path = os.path.join(BASE_DIR, "pending_attendance.csv")
        mydata = []
        self.attendanceReport_left.delete(*self.attendanceReport_left.get_children())
        if os.path.exists(pending_path):
            with open(pending_path, newline="") as f:
                reader = csv.reader(f)
                next(reader, None)  # skip header
                for row in reader:
                    if row:
                        mydata.append(row)
                        self.attendanceReport_left.insert("", END, values=row)

    def importCsv(self):
        mydata.clear()
        fln = filedialog.askopenfilename(initialdir=os.getcwd(), title="Open CSV",
                                         filetypes=(("CSV File", "*.csv"), ("All File", "*.*")), parent=self.root)
        if fln:
            with open(fln) as myfile:
                csvread = csv.reader(myfile, delimiter=",")
                for i in csvread:
                    mydata.append(i)
            self.fetchData(mydata)

    def exportCsv(self):
        try:
            if len(mydata) < 1:
                messagebox.showerror("Error", "No Data Found!", parent=self.root)
                return
            fln = filedialog.asksaveasfilename(initialdir=os.getcwd(), title="Save CSV",
                                               filetypes=(("CSV File", "*.csv"), ("All File", "*.*")), parent=self.root)
            if fln:
                with open(fln, mode="w", newline="") as myfile:
                    exp_write = csv.writer(myfile, delimiter=",")
                    for i in mydata:
                        exp_write.writerow(i)
                messagebox.showinfo("Success", "Data exported successfully!", parent=self.root)
        except Exception as es:
            messagebox.showerror("Error", f"Due to: {str(es)}", parent=self.root)

    # ===================== Cursor Functions =====================
    def get_cursor_left(self, event=""):
        cursor_focus = self.attendanceReport_left.focus()
        content = self.attendanceReport_left.item(cursor_focus)
        data = content.get("values", [])
        if data:
            self.var_id.set(data[0])
            self.var_roll.set(data[1])
            self.var_name.set(data[2])
            self.var_section.set(data[3])
            self.var_subject.set(data[4])
            self.var_time.set(data[5])
            self.var_date.set(data[6])
            self.var_attend.set(data[7])

    def get_cursor_right(self, event=""):
        cursor_focus = self.attendanceReport.focus()
        content = self.attendanceReport.item(cursor_focus)
        data = content.get("values", [])
        if data:
            self.var_id.set(data[0])
            self.var_roll.set(data[1])
            self.var_name.set(data[2])
            self.var_section.set(data[3])
            self.var_subject.set(data[4])
            self.var_time.set(data[5])
            self.var_date.set(data[6])
            self.var_attend.set(data[7])

    # ===================== Reset Data =====================
    def reset_data(self):
        self.var_id.set("")
        self.var_roll.set("")
        self.var_name.set("")
        self.var_section.set("")
        self.var_subject.set("")
        self.var_time.set("")
        self.var_date.set("")
        self.var_attend.set("Status")

    # ===================== Database Actions =====================
    def fetch_data(self):
        try:
            conn = mysql.connector.connect(user='root', password='itsmesim', host='localhost',
                                           database='face_recognizer', port=3306)
            mycursor = conn.cursor()
            mycursor.execute("SELECT * FROM stdattendance")
            data = mycursor.fetchall()
            if data:
                self.attendanceReport.delete(*self.attendanceReport.get_children())
                for row in data:
                    self.attendanceReport.insert("", END, values=row)
            conn.close()
        except Exception as es:
            messagebox.showerror("Error", f"Database fetch error: {str(es)}", parent=self.root)

    # ===================== Filtering =====================
    def apply_filters(self):
        """Filters the Database Records table by roll number, subject,
        section, status, and/or a specific date picked from the calendar.
        Check 'All Dates' to search across every date. Any field can be
        left blank/default to widen the search."""
        roll_val = self.filter_roll.get().strip()
        subject_val = self.filter_subject.get().strip()
        section_val = self.filter_section.get().strip()
        status_val = self.filter_status.get().strip()
        show_all_dates = self.filter_all_dates.get()
        date_val = "" if show_all_dates else self.date_filter_widget.get().strip()

        conditions = []
        params = []
        if roll_val:
            conditions.append("std_roll_no LIKE %s")
            params.append(f"%{roll_val}%")
        if date_val:
            conditions.append("std_date = %s")
            params.append(date_val)
        if subject_val and subject_val != "All":
            conditions.append("std_subject = %s")
            params.append(subject_val)
        if section_val and section_val != "All":
            conditions.append("std_section = %s")
            params.append(section_val)
        if status_val and status_val != "All":
            conditions.append("std_attendance = %s")
            params.append(status_val)

        query = "SELECT * FROM stdattendance"
        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        try:
            conn = mysql.connector.connect(user='root', password='itsmesim', host='localhost',
                                           database='face_recognizer', port=3306)
            mycursor = conn.cursor()
            mycursor.execute(query, tuple(params))
            data = mycursor.fetchall()
            conn.close()

            self.attendanceReport.delete(*self.attendanceReport.get_children())
            for row in data:
                self.attendanceReport.insert("", END, values=row)

            if not data:
                messagebox.showinfo("No Matches", "No attendance records match those filters.", parent=self.root)
        except Exception as es:
            messagebox.showerror("Error", f"Filter error: {str(es)}", parent=self.root)

    def clear_filters(self):
        self.filter_roll.set("")
        self.filter_subject.set("All")
        self.filter_section.set("All")
        self.filter_status.set("All")
        self.filter_all_dates.set(False)
        self.date_filter_widget.set_date(datetime.now())
        self.apply_filters()

    def action(self):
        if (self.var_id.get() == "" or self.var_roll.get() == "" or self.var_name.get() == "" or
            self.var_section.get() == "" or self.var_subject.get() == "" or self.var_time.get() == "" or
            self.var_date.get() == "" or self.var_attend.get() == ""):
            messagebox.showerror("Error", "Please fill in all required fields!", parent=self.root)
        else:
            try:
                conn = mysql.connector.connect(user='root', password='itsmesim', host='localhost',
                                               database='face_recognizer', port=3306)
                mycursor = conn.cursor()
                mycursor.execute("INSERT INTO stdattendance (std_id,std_roll_no,std_name,std_section,std_subject,std_time,std_date,std_attendance) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
                                 (self.var_id.get(), self.var_roll.get(), self.var_name.get(), self.var_section.get(),
                                  self.var_subject.get(), self.var_time.get(), self.var_date.get(), self.var_attend.get()))
                conn.commit()
                self.apply_filters()
                conn.close()
                messagebox.showinfo("Success", "Record added successfully!", parent=self.root)
            except Exception as es:
                messagebox.showerror("Error", f"Database insert error: {str(es)}", parent=self.root)

    def refresh_and_save(self):
        """Pulls every face the Recognition screen has logged
        (pending_attendance.csv), saves each new one straight into the
        MySQL stdattendance table (auto-marked Present, no admin decision
        needed), then refreshes both tables so it's ready to export."""
        pending_path = os.path.join(BASE_DIR, "pending_attendance.csv")
        if not os.path.exists(pending_path):
            self.load_pending()
            messagebox.showinfo("Nothing New", "No new recognitions to save yet.", parent=self.root)
            return

        with open(pending_path, newline="") as f:
            reader = csv.reader(f)
            next(reader, None)
            rows = [r for r in reader if r]

        if not rows:
            self.load_pending()
            messagebox.showinfo("Nothing New", "No new recognitions to save yet.", parent=self.root)
            return

        saved_count = 0
        try:
            conn = mysql.connector.connect(user='root', password='itsmesim', host='localhost',
                                           database='face_recognizer', port=3306)
            mycursor = conn.cursor()
            for row in rows:
                if len(row) < 8:
                    continue
                id_, roll_, name_, section_, subject_, time_, date_, status_ = row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7]

                mycursor.execute("SELECT 1 FROM stdattendance WHERE std_id=%s AND std_date=%s AND std_subject=%s", (id_, date_, subject_))
                if mycursor.fetchone():
                    continue  # already saved earlier, skip

                mycursor.execute(
                    "INSERT INTO stdattendance (std_id,std_roll_no,std_name,std_section,std_subject,std_time,std_date,std_attendance) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
                    (id_, roll_, name_, section_, subject_, time_, date_, status_))
                saved_count += 1

            conn.commit()
            conn.close()

            # Show only the most recent (today's) attendance after saving —
            # not the entire history — matching the default filter view.
            self.filter_roll.set("")
            self.filter_subject.set("All")
            self.filter_section.set("All")
            self.filter_status.set("All")
            self.filter_all_dates.set(False)
            self.date_filter_widget.set_date(datetime.now())
            self.apply_filters()
            self.load_pending()
            messagebox.showinfo("Saved", f"{saved_count} new attendance record(s) saved to the database.\nShowing today's attendance below. You can now export the report.", parent=self.root)
        except Exception as es:
            messagebox.showerror("Error", f"Database insert error: {str(es)}", parent=self.root)

    def export_report(self):
        """Exports whatever is currently shown in the Database Records
        table — if a filter is active (date/subject/status), only the
        filtered rows are exported; otherwise the full table is exported."""
        try:
            rows = [self.attendanceReport.item(i)["values"] for i in self.attendanceReport.get_children()]

            if not rows:
                messagebox.showerror("Error", "No attendance records to export. Try Clear filters or Refresh first.", parent=self.root)
                return

            fln = filedialog.asksaveasfilename(initialdir=os.getcwd(), title="Save Attendance Report",
                                               defaultextension=".csv",
                                               filetypes=(("CSV File", "*.csv"), ("All File", "*.*")), parent=self.root)
            if fln:
                with open(fln, mode="w", newline="") as myfile:
                    writer = csv.writer(myfile)
                    writer.writerow(["ID", "Roll_No", "Name", "Section", "Subject", "Time", "Date", "Attendance"])
                    writer.writerows(rows)
                messagebox.showinfo("Success", "Attendance report exported successfully!", parent=self.root)
        except Exception as es:
            messagebox.showerror("Error", f"Export error: {str(es)}", parent=self.root)

    def update_data(self):
        if self.var_id.get() == "":
            messagebox.showerror("Error", "Please select a record to update!", parent=self.root)
        else:
            try:
                conn = mysql.connector.connect(user='root', password='itsmesim', host='localhost',
                                               database='face_recognizer', port=3306)
                mycursor = conn.cursor()
                mycursor.execute(
                    "UPDATE stdattendance SET std_roll_no=%s,std_name=%s,std_section=%s,std_subject=%s,std_time=%s,std_date=%s,std_attendance=%s WHERE std_id=%s",
                    (self.var_roll.get(), self.var_name.get(), self.var_section.get(), self.var_subject.get(),
                     self.var_time.get(), self.var_date.get(), self.var_attend.get(), self.var_id.get()))
                conn.commit()
                self.apply_filters()
                conn.close()
                messagebox.showinfo("Success", "Record updated successfully!", parent=self.root)
            except Exception as es:
                messagebox.showerror("Error", f"Database update error: {str(es)}", parent=self.root)

    def delete_data(self):
        if self.var_id.get() == "":
            messagebox.showerror("Error", "Please select a record to delete!", parent=self.root)
        else:
            try:
                conn = mysql.connector.connect(user='root', password='itsmesim', host='localhost',
                                               database='face_recognizer', port=3306)
                mycursor = conn.cursor()
                mycursor.execute("DELETE FROM stdattendance WHERE std_id=%s", (self.var_id.get(),))
                conn.commit()
                self.apply_filters()
                conn.close()
                messagebox.showinfo("Success", "Record deleted successfully!", parent=self.root)
            except Exception as es:
                messagebox.showerror("Error", f"Database delete error: {str(es)}", parent=self.root)

# ===================== Example of opening Attendance window from main app =====================
if __name__ == "__main__":
    root = Tk()
    app = Attendance(root)
    root.mainloop()
