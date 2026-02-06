import cv2
import subprocess

VIDEO = "10.mp4"
RTSP_URL = "rtsp://localhost:8554/cam1"

cap = cv2.VideoCapture(VIDEO)

width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

FFMPEG = r"C:\ffmpeg\bin\ffmpeg.exe"

cmd = [
    FFMPEG,
    "-re",
    "-f", "rawvideo",
    "-pix_fmt", "bgr24",
    "-s", f"{width}x{height}",
    "-r", "30",
    "-i", "-",

    "-c:v", "libx264",
    "-profile:v", "baseline",
    "-level", "3.0",
    "-preset", "fast",
    "-tune", "zerolatency",
    "-crf", "20",
    "-pix_fmt", "yuv420p",
    "-movflags", "+faststart",

    "-rtsp_transport", "tcp",
    "-f", "rtsp",
    RTSP_URL
]

proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)

while True:
    ret, frame = cap.read()
    if not ret:
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        continue
    proc.stdin.write(frame.tobytes())
