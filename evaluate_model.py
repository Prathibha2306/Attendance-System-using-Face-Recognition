"""
evaluate_model.py — Measures real accuracy/precision/recall/FAR for the
Smart Attendance System's face recognition engine, and produces a
confusion matrix and a threshold-sensitivity plot.

WHY THIS EXISTS
----------------
The recognizer in this project (train.py / face_recognition.py) does not
train a neural network from scratch — it uses a FROZEN, pretrained FaceNet
CNN purely for feature extraction (transfer learning), and only computes a
small per-student prototype vector on top of it. Because no gradient
descent happens on your own data, there is no "training accuracy/loss per
epoch" curve to produce — that concept doesn't apply here, and generating
one would misrepresent how the system works.

What DOES meaningfully exist, and what this script produces instead:
  1. A confusion matrix from real verification trials (who got recognized
     as whom).
  2. Accuracy / Precision / Recall / False Acceptance Rate, computed from
     TP/FP/FN/TN counts (fills in the table from your book chapter).
  3. A threshold-sensitivity plot — accuracy/precision/recall/FAR plotted
     against the similarity threshold (the one real tunable parameter in
     this architecture, playing the same "which setting gives the best
     trade-off" role that an epoch curve plays for a trained network).

REQUIRED FOLDER STRUCTURE — create this yourself before running:

    test_data/
        <student_id_1>/            e.g. 4SF23CS154/
            photo1.jpg              <- NEW photos of this student, taken
            photo2.jpg                 separately from the ones used to
            ...                         train (Faces_img/). Re-using the
                                        training photos would make the
                                        result artificially perfect.
        <student_id_2>/
            photo1.jpg
            ...
        unknown/
            photo1.jpg              <- photos of people who are NOT
            photo2.jpg                  enrolled at all (classmates who
            ...                          weren't registered, strangers,
                                         even a photo held up to the
                                         camera to test spoof rejection).

Aim for at least 8-10 photos per enrolled student and at least 15-20
"unknown" photos, taken under a few different lighting conditions/angles,
for a result that means something statistically.

USAGE
------
    python evaluate_model.py

Outputs (written next to this script):
    confusion_matrix.png
    threshold_sensitivity.png
    metrics_table.csv
    (and prints the filled-in metrics table to the terminal)
"""

import os
import pickle
import numpy as np
import cv2
import matplotlib.pyplot as plt
import seaborn as sns
import csv

from deepface import DeepFace

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEST_DIR = os.path.join(BASE_DIR, "test_data")
EMBEDDINGS_PATH = os.path.join(BASE_DIR, "embeddings.pkl")
CASCADE_PATH = os.path.join(BASE_DIR, "haarcascade_frontalface_default.xml")

EMBEDDING_MODEL = "Facenet"          # must match train.py / face_recognition.py
DEFAULT_THRESHOLD = 0.65             # must match face_recognition.py's SIMILARITY_THRESHOLD


def load_embeddings():
    with open(EMBEDDINGS_PATH, "rb") as f:
        payload = pickle.load(f)
    return payload["students"]  # {student_id: 128-d unit vector}


def crop_largest_face(img, face_cascade):
    """Mirrors the live pipeline: detect with Haar cascade, crop the
    largest detected face. Returns None if no face is found."""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)
    if len(faces) == 0:
        return None
    x, y, w, h = max(faces, key=lambda f: f[2] * f[3])  # largest box
    return img[y:y + h, x:x + w]


def embed_face(face_bgr):
    """Same call as train.py / face_recognition.py: detector_backend='skip'
    because we already cropped the face ourselves above."""
    rep = DeepFace.represent(
        img_path=face_bgr,
        model_name=EMBEDDING_MODEL,
        detector_backend="skip",
        enforce_detection=False,
    )
    vec = np.array(rep[0]["embedding"], dtype=np.float64)
    norm = np.linalg.norm(vec)
    if norm == 0:
        return None
    return vec / norm


def best_match(vec, students):
    """Returns (best_student_id, best_similarity) against every stored
    prototype, using cosine similarity (vectors are already unit-length,
    so this is just a dot product)."""
    best_id, best_sim = None, -1.0
    for sid, proto in students.items():
        sim = float(np.dot(vec, proto))
        if sim > best_sim:
            best_id, best_sim = sid, sim
    return best_id, best_sim


def main():
    if not os.path.exists(EMBEDDINGS_PATH):
        print(f"ERROR: {EMBEDDINGS_PATH} not found. Run Train Data first.")
        return
    if not os.path.exists(TEST_DIR):
        print(f"ERROR: {TEST_DIR} not found.\n\nCreate it with this structure "
              f"(see the docstring at the top of this file for details):\n"
              f"  test_data/<student_id>/*.jpg   (held-out genuine photos)\n"
              f"  test_data/unknown/*.jpg        (non-enrolled people)")
        return

    students = load_embeddings()
    face_cascade = cv2.CascadeClassifier(CASCADE_PATH)

    # ---- Run every test image through the exact live pipeline once,
    # recording its true label and the (predicted_id, similarity) result.
    # We vary the accept/reject threshold afterwards without re-running
    # the model, since that's expensive. ----
    results = []  # list of (true_label, predicted_id, similarity)
    skipped_no_face = 0

    for entry in sorted(os.listdir(TEST_DIR)):
        entry_path = os.path.join(TEST_DIR, entry)
        if not os.path.isdir(entry_path):
            continue
        true_label = "unknown" if entry.lower() == "unknown" else entry

        for fname in sorted(os.listdir(entry_path)):
            fpath = os.path.join(entry_path, fname)
            img = cv2.imread(fpath)
            if img is None:
                continue

            face = crop_largest_face(img, face_cascade)
            if face is None:
                skipped_no_face += 1
                print(f"  [skip] No face detected in {fpath}")
                continue

            vec = embed_face(face)
            if vec is None:
                skipped_no_face += 1
                continue

            pred_id, sim = best_match(vec, students)
            results.append((true_label, pred_id, sim))
            print(f"  {fname:30s} true={true_label:15s} predicted={pred_id!s:15s} sim={sim:.3f}")

    if not results:
        print("No usable test images were processed. Check test_data/ contents.")
        return

    # ---- Metrics at the model's actual configured threshold ----
    def compute_confusion(threshold):
        TP = FP = FN = TN = 0
        for true_label, pred_id, sim in results:
            accepted = sim > threshold
            if true_label == "unknown":
                if accepted:
                    FP += 1
                else:
                    TN += 1
            else:
                if accepted and pred_id == true_label:
                    TP += 1
                elif accepted and pred_id != true_label:
                    # misidentified as a different enrolled student —
                    # counted as a failure to correctly recognise the
                    # true student (FN), consistent with a strict
                    # verification-style evaluation.
                    FN += 1
                else:
                    FN += 1
        return TP, FP, FN, TN

    TP, FP, FN, TN = compute_confusion(DEFAULT_THRESHOLD)
    total = TP + FP + FN + TN
    accuracy = (TP + TN) / total if total else 0
    precision = TP / (TP + FP) if (TP + FP) else 0
    recall = TP / (TP + FN) if (TP + FN) else 0
    far = FP / (FP + TN) if (FP + TN) else 0

    print("\n" + "=" * 60)
    print(f"RESULTS AT THRESHOLD = {DEFAULT_THRESHOLD}")
    print("=" * 60)
    print(f"TP={TP}  FP={FP}  FN={FN}  TN={TN}   (total trials: {total})")
    if skipped_no_face:
        print(f"({skipped_no_face} image(s) skipped — no face detected)")
    print(f"{'Metric':<25}{'Formula':<20}{'Measured Result'}")
    print(f"{'Accuracy':<25}{'(TP+TN)/Total':<20}{accuracy:.3f}")
    print(f"{'Precision':<25}{'TP/(TP+FP)':<20}{precision:.3f}")
    print(f"{'Recall':<25}{'TP/(TP+FN)':<20}{recall:.3f}")
    print(f"{'False Acceptance Rate':<25}{'FP/(FP+TN)':<20}{far:.3f}")

    with open(os.path.join(BASE_DIR, "metrics_table.csv"), "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Metric", "Formula", "Measured Result"])
        writer.writerow(["Accuracy", "(TP+TN)/Total Trials", f"{accuracy:.3f}"])
        writer.writerow(["Precision", "TP/(TP+FP)", f"{precision:.3f}"])
        writer.writerow(["Recall", "TP/(TP+FN)", f"{recall:.3f}"])
        writer.writerow(["False Acceptance Rate", "FP/(FP+TN)", f"{far:.3f}"])
    print(f"\nSaved: metrics_table.csv")

    # ---- Confusion matrix (per-student, not just TP/FP/FN/TN) ----
    labels = sorted(students.keys()) + ["unknown"]
    label_index = {l: i for i, l in enumerate(labels)}
    matrix = np.zeros((len(labels), len(labels)), dtype=int)

    for true_label, pred_id, sim in results:
        accepted = sim > DEFAULT_THRESHOLD
        predicted_label = pred_id if accepted else "unknown"
        i = label_index.get(true_label, label_index["unknown"])
        j = label_index.get(predicted_label, label_index["unknown"])
        matrix[i, j] += 1

    plt.figure(figsize=(max(6, len(labels) * 0.7), max(5, len(labels) * 0.6)))
    sns.heatmap(matrix, annot=True, fmt="d", cmap="Blues",
                xticklabels=labels, yticklabels=labels, cbar=True)
    plt.xlabel("Predicted")
    plt.ylabel("True")
    plt.title(f"Confusion Matrix (threshold = {DEFAULT_THRESHOLD})")
    plt.tight_layout()
    plt.savefig(os.path.join(BASE_DIR, "confusion_matrix.png"), dpi=150)
    plt.close()
    print("Saved: confusion_matrix.png")

    # ---- Threshold-sensitivity plot (the correct analogue to an
    # accuracy/loss-vs-epoch curve for a similarity-threshold system) ----
    thresholds = np.arange(0.30, 0.91, 0.05)
    accs, precs, recs, fars = [], [], [], []
    for t in thresholds:
        tp, fp, fn, tn = compute_confusion(t)
        tot = tp + fp + fn + tn
        accs.append((tp + tn) / tot if tot else 0)
        precs.append(tp / (tp + fp) if (tp + fp) else 0)
        recs.append(tp / (tp + fn) if (tp + fn) else 0)
        fars.append(fp / (fp + tn) if (fp + tn) else 0)

    plt.figure(figsize=(8, 5.5))
    plt.plot(thresholds, accs, marker="o", label="Accuracy")
    plt.plot(thresholds, precs, marker="s", label="Precision")
    plt.plot(thresholds, recs, marker="^", label="Recall")
    plt.plot(thresholds, fars, marker="x", label="False Acceptance Rate")
    plt.axvline(DEFAULT_THRESHOLD, color="gray", linestyle="--",
               label=f"Current threshold ({DEFAULT_THRESHOLD})")
    plt.xlabel("Similarity Threshold")
    plt.ylabel("Score")
    plt.title("Threshold Sensitivity — Accuracy / Precision / Recall / FAR")
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(BASE_DIR, "threshold_sensitivity.png"), dpi=150)
    plt.close()
    print("Saved: threshold_sensitivity.png")


if __name__ == "__main__":
    main()
