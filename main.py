import sys
from PySide6.QtWidgets import QApplication
from ui import MyApp
import functions

def main():
    app = QApplication(sys.argv)
    window = MyApp()
    window.show()

    window.auto_skill_button.clicked.connect(window.open_auto_skill_dialog)
    window.pushButton_5.clicked.connect(window.accept_window_title)
    window.pushButton.clicked.connect(lambda: functions.start_main_functionality(window.selected_model_path, window.window_title, window.model, window.text_break_time_edit, window.checkBox_2, window.checkBox_3, window.pause_event, window.text_break_event, window.skill_activation_interval, window.skill_keys))
    window.pushButton_2.clicked.connect(lambda: functions.stop_functionality(window.pause_event, window.text_break_event, window.skill_thread, window.main_thread, window.rotate_thread))  # Stop düğmesi için bağlantı yapıldı
    window.comboBox.currentIndexChanged.connect(window.update_window_title)
    window.timer.timeout.connect(lambda: functions.update_pid_list(window.pid_combobox))
    window.close_button.clicked.connect(window.close)
    window.minimize_button.clicked.connect(window.showMinimized)

    sys.exit(app.exec())

if __name__ == "__main__":
    main()