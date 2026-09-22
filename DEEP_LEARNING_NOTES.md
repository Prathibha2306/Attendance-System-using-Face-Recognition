# Conversion to a deep learning recognition engine

This project originally used classical computer vision for both stages of
face recognition: Haar cascades for detection, and an LBPH (Local Binary
Patterns Histogram) classifier for recognition. LBPH has no neural network
and learns nothing through gradient descent — it computes hand-designed
texture histograms and compares them by distance.

The recognition stage has been replaced with a pretrained convolutional
neural network. Detection is unchanged (Haar cascades still locate faces in
each frame; that part of the pipeline was never claimed to be deep learning
and does not need to be for this to be a legitimate CNN-based project).

## What changed, file by file

| File | Before | After |
|---|---|---|
| `student.py` | Saved grayscale face crops | Saves colour face crops (the CNN needs RGB, not grayscale — grayscale detection still finds the face location) |
| `train.py` | Fit `cv2.face.LBPHFaceRecognizer_create()` on all captured images, wrote `clf.xml` | Runs every captured image through a pretrained FaceNet CNN (via the `deepface` library) to get a 128-d embedding, averages each student's embeddings into one L2-normalised prototype vector, writes `embeddings.pkl` |
| `face_recognition.py` | `clf.predict()` returned a distance, converted to a 0–100 "confidence", thresholded at 77 | Computes a live face's CNN embedding, compares by cosine similarity against every stored prototype, accepts the best match above `SIMILARITY_THRESHOLD = 0.65` |
| `requirements.txt` | opencv-python, opencv-contrib-python, numpy, pillow, mysql-connector-python, tkcalendar | adds `deepface` and `tf-keras` (deepface pulls in TensorFlow as its backend) |

Nothing else changed. The GUI, the MySQL schema, the pending-attendance
review queue, the absentee logic, and CSV export are all untouched — this
was the point of keeping recognition isolated to two files in the first
place.

## Why FaceNet via `deepface`, specifically

`deepface` wraps several pretrained face embedding models (FaceNet,
ArcFace, VGG-Face, and others) behind one `DeepFace.represent()` call, so
it needed no custom model-loading code. FaceNet was chosen because its
128-dimensional embedding is small and fast to store and compare, and
because it is the model discussed in Section 6 of the accompanying book
chapter, so the code now matches what the chapter argues for.

## Two things that follow directly from this change

**No more retraining on enrolment.** The old LBPH pipeline had to reprocess
every image of every student whenever anyone new enrolled, because
`clf.train()` fits on the whole dataset at once. The new pipeline computes
one embedding for the new student's images and appends it to
`embeddings.pkl` — every other student's stored embedding is untouched.
(The current `train.py` still reprocesses everyone for simplicity; adding
incremental enrolment is a small, well-scoped extension, not a redesign.)

**A new threshold, tuned the same honest way as the old one.** The old
project accepted a match when its 0–100 confidence score exceeded 77, a
number arrived at by watching the live overlay rather than derived
analytically. `SIMILARITY_THRESHOLD = 0.65` plays the same role for cosine
similarity and needs the same kind of on-site tuning for a new camera or
room — this is not a weakness specific to LBPH, it is a property of every
threshold-based acceptance rule in this class of system, and the book
chapter's discussion of that trade-off (Section 5) still applies unchanged.

## Verified before shipping

The full pipeline — extracting an embedding, averaging per-student
prototypes, saving `embeddings.pkl`, then loading it back and identifying a
held-out query image by cosine similarity — was run end-to-end and
confirmed to pick the correct enrolled identity with a clear similarity
margin over the wrong one. The GUI itself could not be exercised in this
environment (no display/Tkinter available here), so test that part on your
own Windows machine before your demo — capture, train, and recognise with
two or three real enrolled students, the same way you would have tested
the original LBPH version.

## What to change in your report and book chapter

Everywhere the old text says LBPH, Haar-Cascade-plus-LBPH, or "classical,
hand-engineered features" as the *recognition* method, it should now say
FaceNet embeddings via a pretrained CNN. Everywhere Section 6 of the book
chapter describes the FaceNet migration as *future work*, it is now
*implemented work*, and the corresponding results section should report
what you actually observe when you test it (expect a real accuracy figure
to require GPU-optional but slower-than-LBPH inference, and to be more
robust to pose and lighting than the old system was — but measure it
rather than assume it).
