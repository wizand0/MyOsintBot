# rtsp_motion_detector.py
import cv2
import csv
import os
import time
import json
import logging
import io
import shutil
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
    handlers=[logging.StreamHandler()]
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

# ===================== Проверка зависимостей =====================
def check_dependencies(bot=None):
    """Проверяем наличие ffmpeg и поддержку в OpenCV"""
    errors = []
    if shutil.which("ffmpeg") is None:
        errors.append("❌ ffmpeg не найден в контейнере")

    build_info = cv2.getBuildInformation()
    if "FFMPEG" not in build_info:
        errors.append("❌ OpenCV собран без поддержки ffmpeg")

    if errors:
        for e in errors:
            logging.error(e)
        if bot:
            for e in errors:
                try:
                    bot.loop.create_task(bot.send_message(chat_id=ADMIN_ID, text=e))
                except Exception:
                    pass
    else:
        logging.info("✅ ffmpeg и OpenCV в порядке")

# ===================== YOLO =====================
logging.info("📦 Загружаю модель YOLOv8...")
model = YOLO(YOLO_MODEL)

if not os.path.exists(OUTPUT_FILE):
    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow(["camera", "timestamp", "class", "confidence"])

# ===================== Основная функция =====================
async def run_rtsp_detector(bot, enabled_flag: callable):
    """Основная точка входа"""
    check_dependencies(bot)

    with open("cameras.json", "r", encoding="utf-8") as c:
        cameras = json.load(c)
    if not cameras:
        logging.error("❌ cameras.json пустой.")
        return

    logging.info(f"🔍 Найдено {len(cameras)} камер. Запуск анализа...")

    for name, url in cameras.items():
        await detect_motion_and_objects(bot, name, url, enabled_flag)


async def detect_motion_and_objects(bot, camera_name, rtsp_url, enabled_flag):
    logging.info(f"▶️ Подключаюсь к {camera_name} ({rtsp_url})...")
    cap = cv2.VideoCapture(rtsp_url, cv2.CAP_FFMPEG)
    if not cap.isOpened():
        logging.error(f"❌ Не удалось подключиться к {camera_name}")
        return

    logging.info(f"✅ Соединение с {camera_name} установлено")

    ret, frame1 = cap.read()
    ret2, frame2 = cap.read()
    if not ret or not ret2:
        logging.error(f"❌ Не удалось прочитать начальные кадры {camera_name}")
        cap.release()
        return

    last_trigger_time = 0.0
    frame_count = 0

    try:
        while True:
            if not enabled_flag():
                logging.info(f"⏹ Останавливаю {camera_name}, освобождаю поток")
                cap.release()
                await bot.send_message(chat_id=ADMIN_ID, text=f"⏹ {camera_name}: поток остановлен")
                break

            if frame_count % PLAYBACK_SPEED != 0:
                frame1 = frame2
                if not cap.grab():
                    logging.warning(f"⚠️ grab() вернул False для {camera_name}")
                    break
                ok, frame2 = cap.retrieve()
                if not ok:
                    logging.warning(f"⚠️ retrieve() вернул False для {camera_name}")
                    break
                frame_count += 1
                continue

            # Анализ движения
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
                logging.info(f"🚨 Движение зафиксировано на {camera_name}")
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

    except Exception as e:
        logging.exception(f"Ошибка при обработке {camera_name}: {e}")
    finally:
        cap.release()
        logging.info(f"🔚 Поток {camera_name} завершён")
