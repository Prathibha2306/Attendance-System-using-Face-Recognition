from tkinter import *
from PIL import Image, ImageTk
import os, cv2, numpy as np, pickle
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
from tkinter import messagebox

# ============================================================================
# DEEP LEARNING RECOGNITION ENGINE
# ----------------------------------------------------------------------------
# This module used to fit an LBPH classifier (a classical, hand-engineered-
# feature method with no neural network involved). It now uses a pretrained
# convolutional neural network -- FaceNet, via the `deepface` library -- to
# turn every captured face image into a 128-dimensional embedding vector.
#
# "Training" here does not mean gradient descent on our own data: the CNN's
# weights are frozen and were trained by its original authors on a very large
# face dataset. What this module does is inference-only feature extraction:
# it runs each of a student's captured images through the frozen network,
# averages the resulting vectors into one L2-normalised prototype per
# student, and stores those prototypes in embeddings.pkl. Recognition
# (face_recognition.py) compares a live face's embedding against these
# prototypes using cosine similarity -- there is no classifier to retrain
# when a new student enrols, only one more vector to add.
# ============================================================================
from deepface import DeepFace

EMBEDDING_MODEL = "Facenet"  # 128-d embeddings. ArcFace / VGG-Face also work via deepface.


class Train:

    def __init__(self, root):
        self.root = root
        self.root.state("zoomed")
        self.root.title("Attendance Management System - Train Data")

        # Fit to the actual screen size
        self.screen_w = self.root.winfo_screenwidth()
        self.screen_h = self.root.winfo_screenheight()
        self.root.geometry(f"{self.screen_w}x{self.screen_h}+0+0")
        body_h = self.screen_h - 130

        # ===== HEADER IMAGE =====
        header_path = os.path.join(BASE_DIR, "data_img", "app_banner.png")
        if not os.path.exists(header_path):
            messagebox.showerror("Error", f"Header image not found at:\n{header_path}", parent=self.root)
            return

        header = Image.open(header_path)
        header = header.resize((self.screen_w, 130), Image.LANCZOS)
        self.header_img = ImageTk.PhotoImage(header)
        Label(self.root, image=self.header_img).place(x=0, y=0, width=self.screen_w, height=130)

        # ===== BACKGROUND IMAGE =====
        bg_path = os.path.join(BASE_DIR, "data_img", "app_bg.png")
        if not os.path.exists(bg_path):
            messagebox.showerror("Error", f"Background image not found at:\n{bg_path}", parent=self.root)
            return

        bg = Image.open(bg_path)
        bg = bg.resize((self.screen_w, body_h), Image.LANCZOS)
        self.bg_img = ImageTk.PhotoImage(bg)
        bg_label = Label(self.root, image=self.bg_img)
        bg_label.place(x=0, y=130, width=self.screen_w, height=body_h)

        # ===== TITLE =====
        Label(bg_label,
              text="TRAIN FACE DATA (CNN EMBEDDINGS)",
              font=("Verdana", 22, "bold"),
              bg="navyblue",
              fg="white").place(x=0, y=0, relwidth=1, height=50)

        # ===== TRAIN BUTTON =====
        btn_x = (self.screen_w // 2) - 150
        btn_y = (body_h // 2) - 30
        Button(bg_label,
               text="EXTRACT EMBEDDINGS",
               command=self.train_classifier,
               font=("Tahoma", 16, "bold"),
               bg="white",
               fg="navyblue",
               cursor="hand2").place(x=btn_x, y=btn_y, width=300, height=60)

        # ===== FORCE RETRAIN TOGGLE =====
        # By default, training is incremental: students already present in
        # embeddings.pkl are skipped entirely, and only newly-captured
        # students are processed and merged in. Check this to ignore that
        # and reprocess everyone from scratch (e.g. after re-capturing an
        # existing student's photos).
        self.force_retrain = BooleanVar(value=False)
        Checkbutton(bg_label, text="Force retrain ALL students (ignore existing embeddings)",
                   variable=self.force_retrain, font=("Verdana", 10, "bold"),
                   bg="white", fg="navyblue").place(x=btn_x - 60, y=btn_y - 35, width=420, height=25)

        # ===== PROGRESS LABEL (shown during training instead of native
        # OpenCV preview windows, which can steal window focus on Windows) =====
        self.progress_lbl = Label(bg_label, text="", font=("Verdana", 12, "bold"), bg="white", fg="navyblue")
        self.progress_lbl.place(x=btn_x - 50, y=btn_y + 75, width=400, height=30)

    # ===== TRAINING FUNCTION (now: embedding extraction) =====
    def train_classifier(self):
        data_dir = os.path.join(BASE_DIR, "Faces_img")

        if not os.path.exists(data_dir):
            messagebox.showerror("Error", f"Data folder not found:\n{data_dir}", parent=self.root)
            return

        # Same filename convention as before: user.<student_id>.<sample_no>.jpg
        image_paths = [os.path.join(data_dir, f) for f in os.listdir(data_dir) if f.startswith("user.")]
        if len(image_paths) == 0:
            messagebox.showerror("Error", "No valid face images found! Use filenames like user.<id>.<imageno>.jpg", parent=self.root)
            return

        # Group every captured sample by student ID.
        # NOTE: unlike the old LBPH engine (which required OpenCV's
        # cv2.face.LBPHFaceRecognizer_create().train() integer-only labels),
        # this CNN-embedding pipeline just uses a Python dict keyed by
        # student ID, so alphanumeric IDs (e.g. college roll numbers like
        # "4SF23CS154") work fine — no int() conversion needed or wanted.
        per_student = {}
        for image_path in image_paths:
            filename = os.path.split(image_path)[1]  # e.g. user.4SF23CS154.2.jpg
            parts = filename.split('.')
            if len(parts) < 3:
                continue  # skip any incorrectly named files
            sid = parts[1]
            per_student.setdefault(sid, []).append(image_path)

        # ---- Load whatever is already trained, so we can skip it ----
        out_path = os.path.join(BASE_DIR, "embeddings.pkl")
        existing_embeddings = {}
        if os.path.exists(out_path) and not self.force_retrain.get():
            try:
                with open(out_path, "rb") as f:
                    payload = pickle.load(f)
                existing_embeddings = payload.get("students", {})
            except Exception:
                existing_embeddings = {}  # corrupt/unreadable file — fall back to full retrain

        if self.force_retrain.get():
            students_to_process = per_student
        else:
            students_to_process = {sid: paths for sid, paths in per_student.items() if sid not in existing_embeddings}

        already_trained_count = len(per_student) - len(students_to_process)

        if not students_to_process:
            messagebox.showinfo(
                "Nothing New",
                f"All {len(per_student)} student(s) in Faces_img are already trained.\n"
                "Nothing to do. Capture faces for a new student first, or check "
                "'Force retrain ALL' to rebuild everyone from scratch.",
                parent=self.root
            )
            return

        new_embeddings = {}
        images_used = 0
        images_skipped = 0
        last_error = None

        try:
            total_students = len(students_to_process)
            done_students = 0
            for sid, paths in students_to_process.items():
                vectors = []
                for image_path in paths:
                    img = cv2.imread(image_path)  # colour crop saved by student.py
                    if img is None:
                        images_skipped += 1
                        continue

                    try:
                        # detector_backend="skip": the image is already a
                        # tight face crop from the Haar cascade in
                        # student.py, so we do not want DeepFace to run its
                        # own (heavier) detector on top of it.
                        rep = DeepFace.represent(
                            img_path=img,
                            model_name=EMBEDDING_MODEL,
                            detector_backend="skip",
                            enforce_detection=False,
                        )
                        vec = np.array(rep[0]["embedding"], dtype=np.float64)
                        norm = np.linalg.norm(vec)
                        if norm > 0:
                            vectors.append(vec / norm)  # unit-normalise
                            images_used += 1
                        else:
                            images_skipped += 1
                    except Exception as img_err:
                        images_skipped += 1
                        last_error = f"{type(img_err).__name__}: {img_err}"
                        print(f"[Train] Failed on {image_path}: {last_error}")  # visible in the terminal

                if vectors:
                    # One prototype embedding per student: the mean of all
                    # their normalised sample embeddings, renormalised.
                    proto = np.mean(vectors, axis=0)
                    proto = proto / np.linalg.norm(proto)
                    new_embeddings[sid] = proto

                # Update progress in the Tkinter window itself (no native
                # OpenCV preview windows — those can steal window focus)
                done_students += 1
                self.progress_lbl.config(text=f"Processed new student {done_students} of {total_students}...")
                self.root.update_idletasks()

            if not new_embeddings:
                detail = f"\n\nLast error seen:\n{last_error}" if last_error else ""
                messagebox.showerror(
                    "Error",
                    "No usable face embeddings were produced from the new student(s).\n"
                    f"Images attempted: {images_used + images_skipped}, all failed.{detail}\n\n"
                    "Check the terminal window behind this one for the full list of errors, "
                    "or see console output for details.",
                    parent=self.root
                )
                return

            # Merge: previously trained students are untouched, new ones are added.
            all_embeddings = {**existing_embeddings, **new_embeddings}

            with open(out_path, "wb") as f:
                pickle.dump({"model": EMBEDDING_MODEL, "students": all_embeddings}, f)

            self.progress_lbl.config(text="")
            msg = (
                f"Training Completed Successfully!\n\n"
                f"Model: {EMBEDDING_MODEL} (pretrained CNN, via deepface)\n"
                f"Newly trained: {len(new_embeddings)}\n"
                f"Already trained (skipped): {already_trained_count}\n"
                f"Total students now enrolled: {len(all_embeddings)}\n"
                f"Images used: {images_used}"
            )
            if images_skipped:
                msg += f"\nImages skipped (no usable embedding): {images_skipped}"
            messagebox.showinfo("Success", msg, parent=self.root)

        except Exception as e:
            self.progress_lbl.config(text="")
            messagebox.showerror("Error", f"Training Failed!\n{str(e)}", parent=self.root)


if __name__ == "__main__":
    root = Tk()
    Train(root)
    root.mainloop()
