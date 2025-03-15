import threading
import time
import psutil
from pywinauto import Application
from capture_screen import capture_window_by_pid, get_hwnd_by_pid
from yolo_detection import detect_objects, draw_detections, get_closest_detection_center, load_model
from mouse_events import move_mouse, click_mouse
from metinstones_break import text_break
from rotate_screen import rotate_screen_periodically, check_and_rotate_screen
from activate_skill import activate_skills_periodically, activate_skills
from captcha_solver import capture_captcha_and_solve
from auto_pickup import auto_pickup

def update_pid_list(pid_combobox):
    current_pid = pid_combobox.currentText()
    pid_combobox.clear()
    pid_combobox.addItem("Select PID")
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            if proc.info['name'] and proc.info['pid']:
                hwnd = get_hwnd_by_pid(proc.info['pid'])
                if hwnd:
                    pid_combobox.addItem(f"{proc.info['name']} ({proc.info['pid']})", proc.info['pid'])
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

    index = pid_combobox.findText(current_pid)
    if index != -1:
        pid_combobox.setCurrentIndex(index)

def update_window_title(pid_combobox, window_title):
    selected_pid = pid_combobox.currentData()
    if selected_pid:
        window_title = int(selected_pid)
        print(f"Selected PID: {window_title}")
    else:
        print("Lütfen bir pencere seçin.")
    return window_title

def focus_and_move_window(window_title):
    if window_title and window_title != "Select PID":
        try:
            app = Application().connect(process=window_title)
            window = app.top_window()
            window.set_focus()
            window.move_window(0, 0)
        except Exception as e:
            print(f"Pencere taşınamadı: {e}")
    else:
        print("Lütfen bir pencere seçin.")

def start_main_functionality(selected_model_path, window_title, model, text_break_time_edit, checkBox_2, checkBox_3, pause_event, text_break_event, skill_activation_interval, skill_keys):
    if selected_model_path is None:
        print("Model path is not selected.")
        return

    model = load_model(selected_model_path)        

    if not window_title or window_title == "Select PID":
        print("Lütfen bir pencere seçin.")
        return

    try:
        text_break_time = int(text_break_time_edit.text())
    except ValueError:
        print("Geçerli bir metin kırma süresi girin.")
        return

    print(f"Başlatılıyor: window_title={window_title}, text_break_time={text_break_time}")

    captcha_check_interval = 0.1


    if checkBox_2.isChecked():
        skill_thread = threading.Thread(
            target=activate_skills_periodically,
            args=(skill_activation_interval, pause_event, text_break_event, skill_keys),
            daemon=True
        )
        skill_thread.start()
    else:
        skill_thread = None

    rotate_thread = threading.Thread(target=rotate_screen_periodically, daemon=True)
    rotate_thread.start()

    main_thread = threading.Thread(target=main_loop, args=(window_title, model, text_break_time, text_break_event, checkBox_2, pause_event, captcha_check_interval, checkBox_3, capture_window_by_pid, move_mouse, click_mouse), daemon=True)
    main_thread.start()

    return skill_thread, rotate_thread, main_thread

def main_loop(window_title, model, text_break_time, text_break_event, checkBox_2, pause_event, captcha_check_interval, checkBox_3, capture_window, move_mouse, click_mouse):
    while not pause_event.is_set():
        try:
            print(f"Ekran görüntüsü alınıyor... PID: {window_title}")
            image = capture_window(window_title)
            if image is None:
                print(f"PID {window_title} için ekran görüntüsü alınamadı.")
                continue

            print("Nesne tespiti yapılıyor...")
            results = detect_objects(image, model)

            num_detections = sum(1 for result in results for box in result.boxes if model.names[int(box.cls[0])] != 'none')
            print(f"{num_detections} nesne tespit edildi.")

            if num_detections > 0:
                print("Tespit edilen nesneler çiziliyor...")
                image_with_detections = draw_detections(image, results, model)

                print("Ekranın ortasına en yakın nesne bulunuyor...")
                closest_center = get_closest_detection_center(image, results, model)

                if closest_center:
                    print(f"Fare {closest_center} koordinatlarına hareket ettiriliyor...")
                    move_mouse(closest_center[0], closest_center[1])

                    print("Fare tıklanıyor...")
                    click_mouse()

                    text_break_event.clear()
                    text_break(text_break_time)
                    text_break_event.set()

                    if checkBox_2.isChecked():
                        auto_pickup()
                else:
                    print("Ekranın ortasına yakın nesne bulunamadı.")

            check_and_rotate_screen(results, model)

        except Exception as e:
            print(f"Hata: {e}")

        if checkBox_3.isChecked() and text_break_event.is_set():
            success = capture_captcha_and_solve(window_title, capture_window, move_mouse, click_mouse)
            if not success:
                print("CAPTCHA bulunamadı, normal işleme devam ediliyor...")

        time.sleep(captcha_check_interval)

def stop_functionality(pause_event, text_break_event, skill_thread, main_thread, rotate_thread):
    pause_event.set()
    text_break_event.clear()
    if skill_thread is not None and skill_thread.is_alive():
        skill_thread.join()  # İş parçacığını durdurmak için bekle
    if main_thread is not None and main_thread.is_alive():
        main_thread.join()  # İş parçacığını durdurmak için bekle
    if rotate_thread is not None and rotate_thread.is_alive():
        rotate_thread.join()  # İş parçacığını durdurmak için bekle
    pause_event.clear()
    text_break_event.set()