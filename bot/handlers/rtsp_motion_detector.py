# rtsp_motion_detector.py
import cv2
import csv
import os
import time
import json
import logging
import io
from ultralytics import YOLO
from bot.config import ADMIN_ID

# ===================== НАСТРОЙКИ =====================
SENSITIVITY = 25
MIN_AREA = 800
PLAYBACK_SPEED = 8
SAVE_FRAMES = True
RECOGNITION_DELAY_SEC = 4
OUTPUT_FILE = "rtsp_motions_log.csv"
FRAMES_DIR = "rtsp_motion_frames"
YOLO_MODEL = "yolov8n.pt"
CONF_THRESHOLD = 0.7
TARGET_CLASSES = ["person", "cat", "dog"]

# Логгер
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler("motion_debug.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

os.makedirs(FRAMES_DIR, exist_ok=True)

# ===================== Утилиты =====================
def now_ts():
    return time.strftime("%Y-%m-%d %H:%M:%S")

def date_dir():
    d = time.strftime("%Y%m%d")
    p = os.path.join(FRAMES_DIR, d)
    os.makedirs(p, exist_ok=True)
    return p

# ===================== YOLO =====================
logging.info("📦 Загружаю модель YOLOv8...")
model = YOLO(YOLO_MODEL)

if not os.path.exists(OUTPUT_FILE):
    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow(["camera", "timestamp", "class", "confidence"])

# ===================== Основная функция =====================
async def run_rtsp_detector(bot, enabled_flag: callable):
    """
    bot          - экземпляр telegram.Bot
    enabled_flag - функция/лямбда, которая возвращает True/False (вкл/выкл анализ)
    """

    with open("cameras.json", "r", encoding="utf-8") as c:
        cameras = json.load(c)
    if not cameras:
        logging.error("❌ cameras.json пустой.")
        return

    logging.info(f"🔍 Камер: {len(cameras)}. Запуск анализа...")

    for name, url in cameras.items():
        # каждая камера в отдельном потоке async не делаем — пойдём по очереди
        await detect_motion_and_objects(bot, name, url, enabled_flag)


async def detect_motion_and_objects(bot, camera_name, rtsp_url, enabled_flag):
    try:
        cap = cv2.VideoCapture(rtsp_url, cv2.CAP_FFMPEG)
        if not cap.isOpened():
            logging.error(f"❌ Не удалось подключиться к {camera_name}")
            return

        ret, frame1 = cap.read()
        ret2, frame2 = cap.read()
        if not ret or not ret2:
            cap.release()
            return

        last_trigger_time = 0.0
        frame_count = 0

        while True:
            if not enabled_flag():
                await bot.send_message(chat_id=ADMIN_ID, text="⏹ Детектор остановлен")
                break

            if frame_count % PLAYBACK_SPEED != 0:
                frame1 = frame2
                if not cap.grab():
                    break
                ok, frame2 = cap.retrieve()
                if not ok:
                    break
                frame_count += 1
                continue

            small1 = cv2.resize(frame1, (640, 360))
            small2 = cv2.resize(frame2, (640, 360))
            diff = cv2.absdiff(small1, small2)
            gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
            blur = cv2.GaussianBlur(gray, (5, 5), 0)
            _, thresh = cv2.threshold(blur, SENSITIVITY, 255, cv2.THRESH_BINARY)
            dilated = cv2.dilate(thresh, None, iterations=3)
            contours, _ = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            motion_detected = any(cv2.contourArea(c) >= MIN_AREA for c in contours)

            if motion_detected:
                results = model(frame2, verbose=False)[0]
                for box in results.boxes:
                    cls_id = int(box.cls[0])
                    class_name = results.names[cls_id]
                    conf = float(box.conf[0])

                    if class_name in TARGET_CLASSES and conf >= CONF_THRESHOLD:
                        now = time.time()
                        if (now - last_trigger_time) >= RECOGNITION_DELAY_SEC:
                            ts = now_ts()
                            logging.info(f"✅ {camera_name}: {class_name} ({conf:.2f}), {ts}")

                            # Отправляем кадр админу
                            _, buf = cv2.imencode(".jpg", frame2)
                            image_bytes = io.BytesIO(buf)
                            await bot.send_photo(
                                chat_id=ADMIN_ID,
                                photo=image_bytes,
                                caption=f"{camera_name}: {class_name} ({conf:.2f}) {ts}"
                            )

                            if SAVE_FRAMES:
                                fname = f"{camera_name}_{ts.replace(':', '-')}_{class_name}.jpg"
                                cv2.imwrite(os.path.join(date_dir(), fname), frame2)

                            with open(OUTPUT_FILE, "a", newline="", encoding="utf-8") as f:
                                csv.writer(f).writerow([camera_name, ts, class_name, f"{conf:.2f}"])

                            last_trigger_time = now
                        break

            frame1 = frame2
            if not cap.grab():
                break
            ok, frame2 = cap.retrieve()
            if not ok:
                break
            frame_count += 1

        cap.release()

    except Exception as e:
        logging.exception(f"Ошибка при обработке {camera_name}: {e}")
