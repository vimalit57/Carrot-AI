# ─── vision/face_recognition.py ──────────────────────────
import os
import cv2
from config import FACE_TOLERANCE, KNOWN_FACES_DIR, CAM_INDEX

try:
    import face_recognition as fr
    FR_AVAILABLE = True
except ImportError:
    FR_AVAILABLE = False
    print(" face_recognition not installed. Run: pip install face_recognition")


def load_known_faces() -> tuple[list, list]:
    """
    Load all known face encodings from assets/known_faces/.
    Each image filename (without extension) is used as the person's name.
    """
    encodings, names = [], []
    if not os.path.exists(KNOWN_FACES_DIR):
        os.makedirs(KNOWN_FACES_DIR)
        return encodings, names

    for filename in os.listdir(KNOWN_FACES_DIR):
        if filename.lower().endswith((".jpg", ".jpeg", ".png")):
            path = os.path.join(KNOWN_FACES_DIR, filename)
            image = fr.load_image_file(path)
            enc = fr.face_encodings(image)
            if enc:
                encodings.append(enc[0])
                names.append(os.path.splitext(filename)[0])

    print(f"Loaded {len(names)} known faces: {names}")
    return encodings, names


def recognize_from_camera(display=True) -> str:
    """
    Open webcam, detect and identify faces in real time.
    Press Q to quit. Returns a summary string.
    """
    if not FR_AVAILABLE:
        return "face_recognition library not installed."

    known_encodings, known_names = load_known_faces()
    cap = cv2.VideoCapture(CAM_INDEX)

    if not cap.isOpened():
        return "Could not open webcam."

    recognized = set()

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small   = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

        face_locations = fr.face_locations(rgb_small)
        face_encodings = fr.face_encodings(rgb_small, face_locations)

        for encoding, location in zip(face_encodings, face_locations):
            name = "Unknown"
            if known_encodings:
                matches   = fr.compare_faces(known_encodings, encoding,
                                             tolerance=FACE_TOLERANCE)
                distances = fr.face_distance(known_encodings, encoding)
                best_idx  = distances.argmin() if len(distances) > 0 else -1
                if best_idx >= 0 and matches[best_idx]:
                    name = known_names[best_idx]

            recognized.add(name)

            if display:
                top, right, bottom, left = [v * 4 for v in location]
                color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)
                cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
                cv2.putText(frame, name, (left, top - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

        if display:
            cv2.imshow("Face Recognition — Press Q to quit", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    cap.release()
    cv2.destroyAllWindows()

    if recognized:
        people = [n for n in recognized if n != "Unknown"]
        unknowns = [n for n in recognized if n == "Unknown"]
        parts = []
        if people:
            parts.append(f"I recognized: {', '.join(people)}")
        if unknowns:
            parts.append(f"{len(unknowns)} unknown face(s) detected")
        return ". ".join(parts) + "."
    return "No faces detected."


def register_face(name: str) -> str:
    """
    Capture a photo from webcam and save it as a known face.
    """
    if not FR_AVAILABLE:
        return "face_recognition library not installed."

    cap = cv2.VideoCapture(CAM_INDEX)
    if not cap.isOpened():
        return "Could not open webcam."

    print(f" Capturing face for: {name}. Press SPACE to capture.")
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        cv2.imshow("Register Face — Press SPACE", frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord(" "):
            os.makedirs(KNOWN_FACES_DIR, exist_ok=True)
            path = os.path.join(KNOWN_FACES_DIR, f"{name}.jpg")
            cv2.imwrite(path, frame)
            cap.release()
            cv2.destroyAllWindows()
            return f"Face registered for {name}!"
        elif key == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()
    return "Face registration cancelled."
