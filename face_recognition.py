import mysql.connector
import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
import cv2
import numpy as np
import pickle
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from PIL import Image, ImageTk
from datetime import datetime

# See train.py for the full explanation. In short: identification is now a
# nearest-neighbour lookup in a pretrained CNN's embedding space (cosine
# similarity against the prototypes in embeddings.pkl) instead of an LBPH
# classifier's predict() call.
from deepface import DeepFace

EMBEDDING_MODEL = "Facenet"

# Cosine similarity acceptance threshold. This is the CNN-embedding
# equivalent of the old confidence > 77 cutoff, and it needs the same kind
# of on-site tuning: raise it to reduce false accepts (at the cost of more
# genuine students being rejected as Unknown), lower it if too many real
# students are being missed. 0.65 is a reasonable starting point for
# Facenet cosine similarity, not a measured optimum for any particular room.
SIMILARITY_THRESHOLD = 0.65

# Running the CNN on every detected face in every webcam frame is far more
# expensive than LBPH's histogram comparison was. Haar cascade detection
# (cheap) still runs every frame so the bounding box stays smooth; the CNN
# embedding (expensive) only runs every Nth frame. Faces keep their last
# known label on the frames in between.
RECOGNIZE_EVERY_N_FRAMES = 5


class Face_Recognition:
    def __init__(self, root):
        self.root = root
        self.root.state('zoomed')
        self.root.title("Attendance Management System - Face Recognition")

        # Fit to the actual screen size
        self.screen_w = self.root.winfo_screenwidth()
        self.screen_h = self.root.winfo_screenheight()
        self.root.geometry(f"{self.screen_w}x{self.screen_h}+0+0")
        body_h = self.screen_h - 130

        # ================= HEADER IMAGE =================
        img = Image.open(os.path.join(BASE_DIR, "data_img", "app_banner.png"))
        img = img.resize((self.screen_w, 130), Image.LANCZOS)
        self.photoimg = ImageTk.PhotoImage(img)
        Label(self.root, image=self.photoimg).place(x=0, y=0, width=self.screen_w, height=130)

        # ================= BACKGROUND IMAGE =================
        bg1 = Image.open(os.path.join(BASE_DIR, "data_img", "app_bg.png"))
        bg1 = bg1.resize((self.screen_w, body_h), Image.LANCZOS)
        self.photobg1 = ImageTk.PhotoImage(bg1)
        bg_label = Label(self.root, image=self.photobg1)
        bg_label.place(x=0, y=130, width=self.screen_w, height=body_h)

        # ================= TITLE =================
        Label(bg_label, text="FACE RECOGNITION SYSTEM (CNN EMBEDDINGS)", font=("Verdana", 20, "bold"),
              bg="navyblue", fg="white").place(x=0, y=0, relwidth=1, height=50)

        # ================= SUBJECT & SECTION SELECTION =================
        self.var_subject = StringVar()
        self.var_section = StringVar()
        subj_x = (self.screen_w // 2) - 160
        subj_y = (body_h // 2) - 110
        Label(bg_label, text="Subject:", font=("Verdana", 13, "bold"), bg="white", fg="navyblue").place(x=subj_x, y=subj_y, width=100, height=35)
        subject_entry = ttk.Combobox(bg_label, textvariable=self.var_subject, font=("Verdana", 13), justify=CENTER, state="readonly")
        subject_entry["values"] = ("Deep Learning", "Cloud Computing and Security", "PEC", "OEC")
        subject_entry.place(x=subj_x + 100, y=subj_y, width=220, height=35)

        sec_y = subj_y + 45
        Label(bg_label, text="Section:", font=("Verdana", 13, "bold"), bg="white", fg="navyblue").place(x=subj_x, y=sec_y, width=100, height=35)
        section_combo = ttk.Combobox(bg_label, textvariable=self.var_section, font=("Verdana", 13), justify=CENTER, state="readonly")
        section_combo["values"] = ("A", "B", "C", "D")
        section_combo.place(x=subj_x + 100, y=sec_y, width=220, height=35)

        Label(bg_label, text="(both are required before starting)", font=("Verdana", 9, "italic"),
              bg="white", fg="gray30").place(x=subj_x, y=sec_y + 38, width=320, height=20)

        # ================= RECOGNITION BUTTON =================
        btn_x = (self.screen_w // 2) - 140
        btn_y = (body_h // 2) + 20
        Button(bg_label, text="START FACE RECOGNITION", command=self.face_recog,
               font=("Tahoma", 16, "bold"), bg="white", fg="navyblue", cursor="hand2").place(x=btn_x, y=btn_y, width=280, height=60)

    # ================= AUTO-MARK ATTENDANCE =================
    def mark_attendance(self, id, roll_no, name, subject, section):
        """A recognized face is automatically marked Present (for the given
        subject/section) and logged to pending_attendance.csv. The Attendance
        screen picks this up and saves it into the database when the admin
        clicks Refresh — no present/absent decision is needed from the admin."""
        date_str = datetime.now().strftime("%d/%m/%Y")
        time_str = datetime.now().strftime("%H:%M:%S")
        pending_path = os.path.join(BASE_DIR, "pending_attendance.csv")

        # Skip if this student's attendance for this subject today is already saved in MySQL.
        try:
            conn = mysql.connector.connect(user='root', password='itsmesim', host='localhost', database='face_recognizer', port=3306)
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM stdattendance WHERE std_id=%s AND std_date=%s AND std_subject=%s", (id, date_str, subject))
            already_final = cursor.fetchone() is not None
            conn.close()
        except Exception:
            already_final = False

        if already_final:
            return

        if not os.path.exists(pending_path):
            with open(pending_path, "w", newline="") as f:
                f.write("ID,Roll_No,Name,Section,Subject,Time,Date,Status\n")

        with open(pending_path, "r+", newline="") as f:
            data = f.readlines()
            already_logged_today = any(
                len(line.split(",")) >= 7 and line.split(",")[0] == str(id) and line.split(",")[4] == subject and line.split(",")[6] == date_str
                for line in data[1:]
            )
            if not already_logged_today:
                f.writelines(f"{id},{roll_no},{name},{section},{subject},{time_str},{date_str},Present\n")

    # ================= AUTO-MARK ABSENTEES =================
    def finalize_absentees(self, subject, section, recognized_ids):
        """Called when a recognition session ends. Every student registered
        in the given section who was NOT recognized during this session is
        automatically logged as Absent for this subject/date."""
        date_str = datetime.now().strftime("%d/%m/%Y")
        time_str = datetime.now().strftime("%H:%M:%S")
        pending_path = os.path.join(BASE_DIR, "pending_attendance.csv")

        try:
            conn = mysql.connector.connect(user='root', password='itsmesim', host='localhost', database='face_recognizer', port=3306)
            cursor = conn.cursor()
            cursor.execute("SELECT id, roll_no, name FROM student WHERE section=%s", (section,))
            section_students = cursor.fetchall()
            conn.close()
        except Exception:
            section_students = []

        if not section_students:
            return

        if not os.path.exists(pending_path):
            with open(pending_path, "w", newline="") as f:
                f.write("ID,Roll_No,Name,Section,Subject,Time,Date,Status\n")

        with open(pending_path, "r") as f:
            existing_lines = f.readlines()

        new_lines = []
        for (sid, roll_no, name) in section_students:
            sid = str(sid)
            if sid in recognized_ids:
                continue  # already marked Present

            # Skip if already finalized in MySQL for this subject/date
            try:
                conn = mysql.connector.connect(user='root', password='itsmesim', host='localhost', database='face_recognizer', port=3306)
                cursor = conn.cursor()
                cursor.execute("SELECT 1 FROM stdattendance WHERE std_id=%s AND std_date=%s AND std_subject=%s", (sid, date_str, subject))
                already_final = cursor.fetchone() is not None
                conn.close()
            except Exception:
                already_final = False
            if already_final:
                continue

            # Skip if already queued (present or absent) for this subject/date
            already_queued = any(
                len(line.split(",")) >= 7 and line.split(",")[0] == sid and line.split(",")[4] == subject and line.split(",")[6] == date_str
                for line in existing_lines[1:] + new_lines
            )
            if already_queued:
                continue

            new_lines.append(f"{sid},{roll_no},{name},{section},{subject},{time_str},{date_str},Absent\n")

        if new_lines:
            with open(pending_path, "a", newline="") as f:
                f.writelines(new_lines)

    # ================= FACE RECOGNITION FUNCTION =================
    def face_recog(self):
        subject = self.var_subject.get().strip()
        section = self.var_section.get().strip()
        if subject == "" or section == "":
            messagebox.showerror("Missing Info", "Please enter the Subject and select the Section before starting recognition.", parent=self.root)
            return

        # ---- Load the trained student embeddings (produced by Train Data) ----
        emb_path = os.path.join(BASE_DIR, "embeddings.pkl")
        if not os.path.exists(emb_path):
            messagebox.showerror("Error", "No trained model found. Run 'Train Data' first.", parent=self.root)
            return
        with open(emb_path, "rb") as f:
            payload = pickle.load(f)
        student_embeddings = payload.get("students", {})
        if not student_embeddings:
            messagebox.showerror("Error", "The trained model has no enrolled students. Capture faces and train again.", parent=self.root)
            return
        known_ids = list(student_embeddings.keys())
        known_matrix = np.stack([student_embeddings[i] for i in known_ids])  # (N, 128), unit-norm rows

        # ---- Cache student name/roll/section lookups once for this session
        # instead of opening a MySQL connection for every detected face in
        # every frame (the old per-frame query was the biggest hidden cost
        # in the original implementation). ----
        try:
            conn = mysql.connector.connect(user='root', password='itsmesim', host='localhost', database='face_recognizer', port=3306)
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, roll_no, section FROM student")
            student_lookup = {str(r[0]): (r[1], r[2], r[3]) for r in cursor.fetchall()}
            conn.close()
        except Exception:
            student_lookup = {}

        # Track which students get recognized during this session so we can
        # mark everyone else in the section Absent once the session ends.
        self.recognized_ids = set()

        faceCascade = cv2.CascadeClassifier(os.path.join(BASE_DIR, "haarcascade_frontalface_default.xml"))

        # Coarse cache of the last label produced for a face at roughly this
        # screen position, reused on frames where we skip the CNN call.
        last_labels = {}

        def identify(face_bgr):
            """Run the CNN on one cropped face and return (student_id, similarity)
            for the closest enrolled prototype, or (None, 0.0) on failure."""
            try:
                rep = DeepFace.represent(
                    img_path=face_bgr,
                    model_name=EMBEDDING_MODEL,
                    detector_backend="skip",
                    enforce_detection=False,
                )
                vec = np.array(rep[0]["embedding"], dtype=np.float64)
                norm = np.linalg.norm(vec)
                if norm == 0:
                    return None, 0.0
                vec = vec / norm
                sims = known_matrix @ vec  # cosine similarity against every enrolled prototype
                best_idx = int(np.argmax(sims))
                return known_ids[best_idx], float(sims[best_idx])
            except Exception:
                return None, 0.0

        def draw_boundary(img, classifier, scaleFactor, minNeighbors, color, do_recognize):
            gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            features = classifier.detectMultiScale(gray_img, scaleFactor, minNeighbors)
            coords = []
            for (x, y, w, h) in features:
                cv2.rectangle(img, (x, y), (x + w, y + h), color, 2)
                pos_key = (x // 20, y // 20)  # coarse bucket so a slowly-moving face reuses its last label

                if do_recognize:
                    face_crop = img[y:y + h, x:x + w]  # colour crop, matches training data
                    sid, sim = identify(face_crop)
                    if sid is not None and sim > SIMILARITY_THRESHOLD:
                        name, roll_no, student_section = student_lookup.get(str(sid), ("Unknown", "Unknown", None))
                    else:
                        sid, name, roll_no, student_section = None, "Unknown", "Unknown", None
                    last_labels[pos_key] = (sid, name, roll_no, student_section)
                else:
                    sid, name, roll_no, student_section = last_labels.get(pos_key, (None, "Detecting...", "", None))

                if sid is not None and name != "Unknown" and student_section == section:
                    # Only mark present if the recognized student is
                    # actually registered in the section this session is
                    # being taken for.
                    cv2.putText(img, f"Name: {name}", (x, y - 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                    cv2.putText(img, f"Roll: {roll_no}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                    self.recognized_ids.add(str(sid))
                    self.mark_attendance(str(sid), roll_no, name, subject, section)
                    cv2.putText(img, "Sent for review", (x, y + h + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 200, 255), 2)
                elif sid is not None and name != "Unknown" and student_section != section:
                    # Recognized, but belongs to a different section — do
                    # NOT mark attendance for this session.
                    cv2.putText(img, f"Name: {name}", (x, y - 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 140, 255), 2)
                    cv2.putText(img, f"Not in Section {section} (belongs to {student_section})",
                               (x, y + h + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 140, 255), 2)
                elif name == "Detecting...":
                    cv2.putText(img, "Detecting...", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 200, 0), 2)
                else:
                    cv2.putText(img, "Unknown Face", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

                coords = [x, y, w, h]
            return coords

        def recognize(img, do_recognize):
            draw_boundary(img, faceCascade, 1.1, 10, (255, 0, 0), do_recognize)
            return img

        cap = cv2.VideoCapture(0)  # Use webcam
        frame_count = 0
        while True:
            ret, img = cap.read()
            if not ret:
                break
            frame_count += 1
            do_recognize = (frame_count % RECOGNIZE_EVERY_N_FRAMES == 0)
            img = recognize(img, do_recognize)
            cv2.putText(img, f"Subject: {subject}  |  Section: {section}", (15, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
            cv2.imshow("Face Recognition", img)

            key = cv2.waitKey(1) & 0xFF
            if key == 13 or key == 27:  # Enter or Escape to exit
                break
            # Also exit if the window's X button was clicked
            if cv2.getWindowProperty("Face Recognition", cv2.WND_PROP_VISIBLE) < 1:
                break

        cap.release()
        cv2.destroyAllWindows()

        # Session over: mark everyone else in this section Absent for this subject.
        self.finalize_absentees(subject, section, self.recognized_ids)
        messagebox.showinfo(
            "Session Complete",
            f"Recognition session ended for {subject} (Section {section}).\n"
            f"{len(self.recognized_ids)} student(s) recognized and marked Present.\n"
            "Everyone else in this section has been queued as Absent.\n\n"
            "Go to Attendance → Refresh & Save to Database to finalize.",
            parent=self.root
        )


if __name__ == "__main__":
    root = Tk()
    obj = Face_Recognition(root)
    root.mainloop()
