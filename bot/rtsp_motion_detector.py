import cv2
import csv
import os
import time
import json
import logging
import io
import shutil
import asyncio
from concurrent.futures import ThreadPoolExecutor
from ultralytics import YOLO
from bot.config import (
    ADMIN_ID, MOTION_FRAME_SKIP, MOTION_COOLDOWN_SECONDS,
    MOTION_RESIZE_WIDTH, MOTION_RESIZE_HEIGHT, MOTION_SENSITIVITY,
    MOTION_MIN_AREA, MOTION_RECOGNITION_DELAY_SEC, YOLO_CONF_THRESHOLD,
    YOLO_TARGET_CLASSES, MOTION_SAVE_FRAMES,
    RECONNECT_INITIAL_DELAY, RECONNECT_MAX_DELAY, HEALTH_TIMEOUT
)

# ===================== НАСТРОЙКИ =====================
OUTPUT_FILE = "rtsp_motions_log.csv"
FRAMES_DIR = "rtsp_motion_frames"
YOLO_MODEL = "yolov8n.pt"

# Логгер
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[logging.StreamHandler()]
)

os.makedirs(FRAMES_DIR, exist_ok=True)

# Пул потоков для асинхронной обработки кадров
frame_executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="motion_detector")

# Глобальный список активных задач камер
active_camera_tasks = []


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
                    asyncio.create_task(bot.send_message(chat_id=ADMIN_ID, text=e))
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


# ===================== Оптимизированная детекция движения =====================
def detect_motion_optimized(frame1, frame2):
    """Оптимизированная детекция движения с уменьшением кадра"""
    # Уменьшаем кадры для ускорения обработки
    small1 = cv2.resize(frame1, (MOTION_RESIZE_WIDTH, MOTION_RESIZE_HEIGHT))
    small2 = cv2.resize(frame2, (MOTION_RESIZE_WIDTH, MOTION_RESIZE_HEIGHT))

    # Детекция движения
    diff = cv2.absdiff(small1, small2)
    gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    _, thresh = cv2.threshold(blur, MOTION_SENSITIVITY, 255, cv2.THRESH_BINARY)
    dilated = cv2.dilate(thresh, None, iterations=3)
    contours, _ = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # Проверяем наличие движения с учетом масштаба
    scale_factor = (frame1.shape[1] / MOTION_RESIZE_WIDTH) * (frame1.shape[0] / MOTION_RESIZE_HEIGHT)
    adjusted_min_area = MOTION_MIN_AREA / scale_factor

    return any(cv2.contourArea(c) >= adjusted_min_area for c in contours)


async def process_yolo_async(frame):
    """Асинхронная обработка YOLO"""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(frame_executor, lambda: model(frame, verbose=False)[0])


class MotionDetector:
    def __init__(self, camera_name):
        self.camera_name = camera_name
        self.frame_counter = 0
        self.last_trigger_time = 0.0
        self.last_motion_notification = 0.0

    def should_process_frame(self):
        """Проверка, нужно ли обрабатывать текущий кадр"""
        self.frame_counter += 1
        return self.frame_counter % MOTION_FRAME_SKIP == 0

    def can_send_notification(self):
        """Проверка cooldown для уведомлений"""
        current_time = time.time()
        return (current_time - self.last_motion_notification) >= MOTION_COOLDOWN_SECONDS

    def update_notification_time(self):
        """Обновление времени последнего уведомления"""
        self.last_motion_notification = time.time()


# ===================== Основная функция =====================
async def run_rtsp_detector(bot, enabled_flag: callable, send_alert_func=None):
    """Основная точка входа с оптимизациями - запускает все камеры параллельно"""
    check_dependencies(bot)

    import pathlib
    camera_file = pathlib.Path(__file__).parent / "cameras.json"
    logging.info(f"camera_file: {camera_file}")

    with open(camera_file, "r", encoding="utf-8") as c:
        cameras = json.load(c)
    if not cameras:
        logging.error("❌ cameras.json пустой.")
        return

    logging.info(f"cameras: {cameras}")
    logging.info(f"🔍 Найдено {len(cameras)} камер. Запуск анализа с оптимизациями...")
    logging.info(f"⚡ Настройки: анализ каждого {MOTION_FRAME_SKIP}-го кадра, "
                 f"cooldown {MOTION_COOLDOWN_SECONDS}s, размер {MOTION_RESIZE_WIDTH}x{MOTION_RESIZE_HEIGHT}")

    # Создаем задачи для всех камер параллельно
    global active_camera_tasks
    active_camera_tasks = []

    try:
        for name, url in cameras.items():
            task = asyncio.create_task(
                detect_motion_and_objects_optimized(bot, name, url, enabled_flag, send_alert_func),
                name=f"camera_{name}"
            )
            active_camera_tasks.append(task)
            logging.info(f"🚀 Запускаю задачу для камеры {name}")

        # Ждем завершения всех задач (или их отмены)
        await asyncio.gather(*active_camera_tasks, return_exceptions=True)

    except Exception as e:
        logging.error(f"Ошибка в run_rtsp_detector: {e}")
    finally:
        # Отменяем все активные задачи при завершении
        for task in active_camera_tasks:
            if not task.done():
                task.cancel()
        active_camera_tasks.clear()
        logging.info("🔚 Все камеры остановлены")


# async def detect_motion_and_objects_optimized(bot, camera_name, rtsp_url, enabled_flag, send_alert_func=None):
#     """Оптимизированная детекция движения и объектов"""
#     logging.info(f"▶️ Подключаюсь к {camera_name} ({rtsp_url})...")
#     cap = cv2.VideoCapture(rtsp_url, cv2.CAP_FFMPEG)
#
#     if not cap.isOpened():
#         logging.error(f"❌ Не удалось подключиться к {camera_name}")
#         return
#
#     logging.info(f"✅ Соединение с {camera_name} установлено")
#
#     ret, frame1 = cap.read()
#     ret2, frame2 = cap.read()
#     if not ret or not ret2:
#         logging.error(f"❌ Не удалось прочитать начальные кадры {camera_name}")
#         cap.release()
#         return
#
#     # Создаем детектор для данной камеры
#     detector = MotionDetector(camera_name)
#
#     try:
#         while True:
#             # Проверяем состояние флага
#             if not enabled_flag():
#                 logging.info(f"⏹ Останавливаю {camera_name}, освобождаю поток")
#                 break
#
#             # Читаем следующий кадр
#             if not cap.grab():
#                 logging.warning(f"⚠️ grab() вернул False для {camera_name}")
#                 break
#             ok, frame2 = cap.retrieve()
#             if not ok:
#                 logging.warning(f"⚠️ retrieve() вернул False для {camera_name}")
#                 break
#
#             # Перестраховка: Убедитесь, что frame2 не пустой
#             if frame2 is None or frame2.size == 0:
#                 logging.warning(f"⚠️ Получен пустой кадр для {camera_name}")
#                 continue
#
#             # Пропускаем кадры для снижения нагрузки
#             if not detector.should_process_frame():
#                 frame1 = frame2
#                 continue
#
#             # Оптимизированная детекция движения
#             motion_detected = detect_motion_optimized(frame1, frame2)
#
#             if motion_detected and detector.can_send_notification():
#                 logging.info(f"🚨 Движение зафиксировано на {camera_name}")
#
#                 # Асинхронная обработка YOLO
#                 try:
#                     results = await process_yolo_async(frame2)
#                     object_detected = False
#
#                     for box in results.boxes:
#                         cls_id = int(box.cls[0])
#                         class_name = results.names[cls_id]
#                         conf = float(box.conf[0])
#
#                         if class_name in YOLO_TARGET_CLASSES and conf >= YOLO_CONF_THRESHOLD:
#                             current_time = time.time()
#                             if (current_time - detector.last_trigger_time) >= MOTION_RECOGNITION_DELAY_SEC:
#                                 ts = now_ts()
#                                 logging.info(f"✅ {camera_name}: {class_name} ({conf:.2f}), {ts}")
#
#                                 _, buf = cv2.imencode(".jpg", frame2)
#                                 image_bytes = io.BytesIO(buf)
#
#                                 caption = f"{camera_name}: {class_name} ({conf:.2f}) {ts}"
#
#                                 # Используем функцию с cooldown если передана, иначе обычную отправку
#                                 if send_alert_func:
#                                     await send_alert_func(bot, ADMIN_ID, image_bytes, caption)
#                                 else:
#                                     await bot.send_photo(chat_id=ADMIN_ID, photo=image_bytes, caption=caption)
#
#                                 if MOTION_SAVE_FRAMES:
#                                     fname = f"{camera_name}_{ts.replace(':', '-')}_{class_name}.jpg"
#                                     cv2.imwrite(os.path.join(date_dir(), fname), frame2)
#
#                                 with open(OUTPUT_FILE, "a", newline="", encoding="utf-8") as f:
#                                     csv.writer(f).writerow([camera_name, ts, class_name, f"{conf:.2f}"])
#
#                                 detector.last_trigger_time = current_time
#                                 detector.update_notification_time()
#                                 object_detected = True
#                                 break
#                         else:
#                             logging.info(
#                                 f"YOLO не подтвердил: {class_name} ({conf:.2f}), "
#                                 f"порог {YOLO_CONF_THRESHOLD}"
#                             )
#
#                     # Если не нашли объекты, но движение есть - просто обновляем время cooldown
#                     if not object_detected:
#                         detector.update_notification_time()
#
#                 except Exception as e:
#                     logging.error(f"Ошибка YOLO обработки для {camera_name}: {e}")
#
#             frame1 = frame2
#
#             # Небольшая пауза чтобы не нагружать CPU слишком сильно
#             await asyncio.sleep(0.05)
#
#     except asyncio.CancelledError:
#         logging.info(f"🛑 Задача камеры {camera_name} отменена")
#         raise
#     except Exception as e:
#         logging.exception(f"Ошибка при обработке {camera_name}: {e}")
#     finally:
#         cap.release()
#         logging.info(f"🔚 Поток {camera_name} завершён")
#         # Уведомляем о завершении
#         try:
#             await bot.send_message(chat_id=ADMIN_ID, text=f"⏹ {camera_name}: поток остановлен")
#         except Exception:
#             pass

async def detect_motion_and_objects_optimized(bot, camera_name, rtsp_url, enabled_flag, send_alert_func=None):
    """Оптимизированная детекция движения и объектов с reconnect"""
    logging.info(f"▶️ Запуск мониторинга для {camera_name} ({rtsp_url})...")

    retry_delay = RECONNECT_INITIAL_DELAY  # Начальная задержка retry
    last_frame_time = time.time()  # Для health check

    while enabled_flag():  # Внешний loop для retry
        cap = cv2.VideoCapture(rtsp_url, cv2.CAP_FFMPEG)

        if not cap.isOpened():
            logging.error(f"❌ Не удалось подключиться к {camera_name}. Retry через {retry_delay}s...")
            await asyncio.sleep(retry_delay)
            retry_delay = min(retry_delay * 2, RECONNECT_MAX_DELAY)  # Exponential backoff
            continue

        logging.info(f"✅ Соединение с {camera_name} установлено")
        retry_delay = RECONNECT_INITIAL_DELAY  # Сброс delay при успехе

        ret, frame1 = cap.read()
        ret2, frame2 = cap.read()
        if not ret or not ret2:
            logging.error(f"❌ Не удалось прочитать начальные кадры {camera_name}")
            cap.release()
            continue

        detector = MotionDetector(camera_name)
        last_frame_time = time.time()

        try:
            while enabled_flag() and cap.isOpened():
                if not cap.grab():
                    logging.warning(f"⚠️ grab() вернул False для {camera_name}")
                    break

                ok, frame2 = cap.retrieve()
                if not ok:
                    logging.warning(f"⚠️ retrieve() вернул False для {camera_name}")
                    break

                if frame2 is None or frame2.size == 0:
                    logging.warning(f"⚠️ Получен пустой кадр для {camera_name}")
                    continue

                # Обновляем timestamp успешного кадра
                last_frame_time = time.time()

                # Health check: если кадры не обновляются > HEALTH_TIMEOUT, break для reconnect
                if time.time() - last_frame_time > HEALTH_TIMEOUT:
                    logging.warning(f"⚠️ Нет новых кадров >{HEALTH_TIMEOUT}s для {camera_name}. Reconnect...")
                    break

                # Пропускаем кадры для снижения нагрузки
                if not detector.should_process_frame():
                    frame1 = frame2
                    continue

                # Оптимизированная детекция движения
                motion_detected = detect_motion_optimized(frame1, frame2)

                if motion_detected and detector.can_send_notification():
                    logging.info(f"🚨 Движение зафиксировано на {camera_name}")

                    # Асинхронная обработка YOLO
                    try:
                        results = await process_yolo_async(frame2)
                        object_detected = False

                        # Добавьте логирование всех обнаруженных объектов
                        if results.boxes:
                            logging.info(f"YOLO обнаружил {len(results.boxes)} объектов")
                            for box in results.boxes:
                                cls_id = int(box.cls[0])
                                class_name = results.names[cls_id]
                                conf = float(box.conf[0])
                                logging.info(f"Обнаружен объект: {class_name} ({conf:.2f})")

                        for box in results.boxes:
                            cls_id = int(box.cls[0])
                            class_name = results.names[cls_id]
                            conf = float(box.conf[0])

                            if class_name in YOLO_TARGET_CLASSES and conf >= YOLO_CONF_THRESHOLD:
                                current_time = time.time()
                                if (current_time - detector.last_trigger_time) >= MOTION_RECOGNITION_DELAY_SEC:
                                    ts = now_ts()
                                    logging.info(f"✅ {camera_name}: {class_name} ({conf:.2f}), {ts}")

                                    _, buf = cv2.imencode(".jpg", frame2)
                                    image_bytes = io.BytesIO(buf)

                                    caption = f"{camera_name}: {class_name} ({conf:.2f}) {ts}"

                                    # Используем функцию с cooldown если передана, иначе обычную отправку
                                    if send_alert_func:
                                        await send_alert_func(bot, ADMIN_ID, image_bytes, caption)
                                    else:
                                        await bot.send_photo(chat_id=ADMIN_ID, photo=image_bytes, caption=caption)

                                    if MOTION_SAVE_FRAMES:
                                        fname = f"{camera_name}_{ts.replace(':', '-')}_{class_name}.jpg"
                                        cv2.imwrite(os.path.join(date_dir(), fname), frame2)

                                    with open(OUTPUT_FILE, "a", newline="", encoding="utf-8") as a:
                                        csv.writer(a).writerow([camera_name, ts, class_name, f"{conf:.2f}"])

                                    detector.last_trigger_time = current_time
                                    detector.update_notification_time()
                                    object_detected = True
                                    break
                            else:
                                logging.info(
                                    f"YOLO не подтвердил: {class_name} ({conf:.2f}), "
                                    f"порог {YOLO_CONF_THRESHOLD}"
                                )

                        # Если не нашли объекты, но движение есть - просто обновляем время cooldown
                        if not object_detected:
                            detector.update_notification_time()

                    except Exception as e:
                        logging.error(f"Ошибка YOLO обработки для {camera_name}: {e}")

                frame1 = frame2

                # Небольшая пауза чтобы не нагружать CPU слишком сильно
                await asyncio.sleep(0.05)

        except asyncio.CancelledError:
            logging.info(f"🛑 Задача камеры {camera_name} отменена")
            raise
        except Exception as e:
            logging.exception(f"Ошибка при обработке {camera_name}: {e}")

        finally:
            cap.release()
            logging.info(f"🔌 Соединение с {camera_name} закрыто. Если флаг активен — retry.")
            # Уведомление админу об обрыве (с cooldown, чтобы не спамить)
            try:
                await bot.send_message(chat_id=ADMIN_ID,
                                       text=f"⚠️ Обрыв соединения с {camera_name}. Пытаюсь reconnect...")
            except Exception:
                pass

        # Задержка перед retry, если не отмена
        if enabled_flag():
            await asyncio.sleep(retry_delay)
            retry_delay = min(retry_delay * 2, RECONNECT_MAX_DELAY)

    logging.info(f"🔚 Мониторинг {camera_name} завершён")
    try:
        await bot.send_message(chat_id=ADMIN_ID, text=f"⏹ {camera_name}: поток остановлен")
    except Exception:
        pass