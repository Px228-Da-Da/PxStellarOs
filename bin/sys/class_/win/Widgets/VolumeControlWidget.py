import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "bin")))
from dependencies import *


class VolumeControlWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.pulse = None  # Для Linux
        self.volume = None  # Для Windows
        self.init_audio()
        self.init_ui()

    def init_audio(self):
        """Инициализация аудио-интерфейса с обработкой ошибок"""
        try:
            if platform.system() == "Windows":
                from ctypes import cast, POINTER
                from comtypes import CLSCTX_ALL
                from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
                
                devices = AudioUtilities.GetSpeakers()
                interface = devices.Activate(
                    IAudioEndpointVolume._iid_, 
                    CLSCTX_ALL, 
                    None
                )
                self.volume = cast(interface, POINTER(IAudioEndpointVolume))
            else:
                # Инициализация PulseAudio для Linux
                self.pulse = pulsectl.Pulse('volume-control')
        except Exception as e:
            print(f"Audio initialization error: {e}")
            self.volume = None
            self.pulse = None

    def init_ui(self):
        """Инициализация интерфейса"""
        self.setWindowTitle("Громкость")
        self.resize(350, 100)
        self.setStyleSheet("""
            QWidget {
                background-color: rgba(30, 30, 30, 0.9);
                color: white;
                border-radius: 8px;
            }
            QSlider::groove:horizontal {
                border: 1px solid #999999;
                height: 6px;
                background: rgba(255, 255, 255, 0.2);
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: #4bcfff;
                border: 1px solid #5c5c5c;
                width: 16px;
                margin: -5px 0;
                border-radius: 8px;
            }
            QSlider::sub-page:horizontal {
                background: #4bcfff;
            }
            QLabel {
                color: white;
                font-size: 14px;
            }
        """)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 150))
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        self.title_label = QLabel("Громкость")
        self.title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.title_label)

        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.valueChanged.connect(self.set_system_volume)
        main_layout.addWidget(self.volume_slider)

        self.volume_label = QLabel("100%")
        self.volume_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.volume_label)

        self.update_volume()

    def get_current_volume(self):
        """Получает текущую громкость в зависимости от ОС"""
        try:
            if platform.system() == "Windows":
                if self.volume:
                    return self.volume.GetMasterVolumeLevelScalar() * 100
            else:
                if self.pulse:
                    sink = self.pulse.get_sink_by_name(self.pulse.server_info().default_sink_name)
                    return sink.volume.value_flat * 100
        except Exception as e:
            print(f"Get volume error: {e}")
        return 100  # Значение по умолчанию

    def update_volume(self):
        """Обновляет ползунок текущей громкостью"""
        try:
            current_volume = self.get_current_volume()
            volume_percent = int(current_volume)
            self.volume_slider.setValue(volume_percent)
            self.volume_label.setText(f"{volume_percent}%")
        except Exception as e:
            print(f"Volume update error: {e}")

    def set_system_volume(self, value):
        """Устанавливает системную громкость"""
        try:
            volume_level = value / 100.0
            if platform.system() == "Windows":
                if self.volume:
                    self.volume.SetMasterVolumeLevelScalar(volume_level, None)
            else:
                if self.pulse:
                    sink = self.pulse.get_sink_by_name(self.pulse.server_info().default_sink_name)
                    self.pulse.volume_set_all_chans(sink, volume_level)
            
            self.volume_label.setText(f"{value}%")
        except Exception as e:
            print(f"Volume set error: {e}")

    def closeEvent(self, event):
        """Очистка ресурсов при закрытии"""
        if platform.system() != "Windows" and self.pulse:
            self.pulse.close()
        super().closeEvent(event)

    def __del__(self):
        """Деструктор для дополнительной очистки"""
        if platform.system() == "Windows" and self.volume:
            self.volume.Release()
            self.volume = None
        elif self.pulse:
            self.pulse.close()
            self.pulse = None