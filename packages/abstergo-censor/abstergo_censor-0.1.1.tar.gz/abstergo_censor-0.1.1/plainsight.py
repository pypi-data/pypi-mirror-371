import cv2
import argparse
import os
from pathlib import Path

def detector(cascade_name):
    path = cv2.data.haarcascades + cascade_name
    return cv2.CascadeClassifier(path)

face_cascade = detector("haarcascade_frontalface_default.xml")
plate_cascade = detector("haarcascade_russian_plate_number.xml")

def blur_regions(img, rects, k=25):
    h, w = img.shape[:2]
    for (x,y,wid,ht) in rects:
        x0, y0 = max(0,x), max(0,y)
        x1, y1 = min(w, x+wid), min(h, y+ht)
        roi = img[y0:y1, x0:x1]
        if roi.size == 0: 
            continue
        # pixelate blur
        roi = cv2.GaussianBlur(roi, (k|1, k|1), 0)
        img[y0:y1, x0:x1] = roi
    return img

def process_image(path, out, use_plates=False, scale=1.2, min_neighbors=5, strength=25, show=False):
    img = cv2.imread(path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=scale, minNeighbors=min_neighbors, minSize=(24,24))
    rects = list(faces)
    if use_plates:
        plates = plate_cascade.detectMultiScale(gray, scaleFactor=scale, minNeighbors=5, minSize=(30,10))
        rects += list(plates)
    out_img = blur_regions(img, rects, strength)
    cv2.imwrite(out, out_img)
    if show:
        cv2.imshow("PlainSight", out_img); cv2.waitKey(0); cv2.destroyAllWindows()

def process_video(path, out, use_plates=False, scale=1.2, strength=25, show=False):
    cap = cv2.VideoCapture(path)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    writer = cv2.VideoWriter(out, fourcc, fps, (w,h))
    while True:
        ret, frame = cap.read()
        if not ret: break
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=scale, minNeighbors=5, minSize=(24,24))
        plates = plate_cascade.detectMultiScale(gray, scaleFactor=scale, minNeighbors=5, minSize=(30,10)) if use_plates else []
        rects = list(faces) + list(plates)
        frame = blur_regions(frame, rects, strength)
        if show:
            cv2.imshow("PlainSight", frame)
            if cv2.waitKey(1) & 0xFF == 27:
                show = False
                cv2.destroyAllWindows()
        writer.write(frame)
    cap.release(); writer.release()

def main():
    ap = argparse.ArgumentParser(description="PlainSight: blur faces/plates in images & videos")
    ap.add_argument("input")
    ap.add_argument("--out", required=True)
    ap.add_argument("--plates", action="store_true")
    ap.add_argument("--strength", type=int, default=25)
    ap.add_argument("--scale", type=float, default=1.2)
    ap.add_argument("--show", action="store_true")
    args = ap.parse_args()

    src = args.input
    out = args.out
    ext = os.path.splitext(src)[1].lower()
    if ext in [".jpg",".jpeg",".png",".bmp",".webp"]:
        process_image(src, out, use_plates=args.plates, scale=args.scale, strength=args.strength, show=args.show)
    else:
        process_video(src, out, use_plates=args.plates, scale=args.scale, strength=args.strength, show=args.show)

if __name__ == "__main__":
    main()
