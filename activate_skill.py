import time
from pynput.keyboard import Key, Controller
import threading

keyboard = Controller()
lock = threading.Lock()

def activate_skills(pause_event, text_break_event, skill_keys):
    """
    Skilleri açmak ve binekten inip tekrar binmek için belirli tuş kombinasyonlarını kullanır.
    """
    with lock:
        pause_event.set()  # Diğer işlemleri durdur
        print("Skiller açılıyor ve binekten inilip tekrar biniliyor...")
        
        # CTRL + G tuş kombinasyonu
        time.sleep(2)
        keyboard.press(Key.ctrl)
        keyboard.press('g')
        time.sleep(0.1)
        keyboard.release('g')
        keyboard.release(Key.ctrl)
        time.sleep(2)  # Kısa bir bekleme süresi

        # Skill tuşları
        for key in skill_keys:
            if key:  # Boş veya geçersiz tuşları atla
                try:
                    keyboard.press(key)
                    time.sleep(0.1)
                    keyboard.release(key)
                    time.sleep(2)  # Kısa bir bekleme süresi
                except ValueError as e:
                    print(f"Geçersiz tuş: {key} - Hata: {e}")

        # CTRL + G tuş kombinasyonu
        keyboard.press(Key.ctrl)
        keyboard.press('g')
        time.sleep(0.1)
        keyboard.release('g')
        keyboard.release(Key.ctrl)
        time.sleep(2)

        print("Skiller açıldı.")
        text_break_event.set()  # Metin kırma işlemini devam ettir
        pause_event.clear()  # Diğer işlemleri devam ettir

def activate_skills_periodically(interval, pause_event, text_break_event, skill_keys):
    """
    Belirli bir süre aralığında skilleri açmak ve binekten inip tekrar binmek için tuş kombinasyonlarını kullanır.
    """
    while True:
        if pause_event.is_set():
            break  # Durma olayı tetiklenmişse döngüden çık
        text_break_event.wait()  # Metin kırma işlemi devam ederken bekle
        activate_skills(pause_event, text_break_event, skill_keys)
        time.sleep(interval)  # Belirtilen süre kadar bekle