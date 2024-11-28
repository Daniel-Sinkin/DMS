import random
import sys
import time
from enum import Enum, auto
from typing import Callable, Optional

from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtWidgets import QButtonGroup, QCheckBox, QLabel, QPushButton


def format_time(seconds: int | float) -> str:
    seconds = int(seconds)
    hours = seconds // (60 * 60)
    seconds -= hours * 60 * 60

    minutes = seconds // 60
    seconds -= minutes * 60

    return f"{hours:02}:{minutes:02}:{seconds:02}"


class TimerState(Enum):
    IS_INACTIVE = auto()
    IS_ACTIVE = auto()
    IS_PAUSED = auto()


class MyWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.timer_is_active: bool = False
        self.times: list[int] = []
        self.time_current_start: Optional[float] = None

        self.timer_state: TimerState = TimerState.IS_INACTIVE

        # Creates a Button
        self.start_button = QtWidgets.QPushButton("Start")
        self.pause_button = QtWidgets.QPushButton("Pause")
        self.stop_button = QtWidgets.QPushButton("Stop")

        self._buttons: list[QtWidgets.QPushButton] = [
            self.start_button,
            self.pause_button,
            self.stop_button,
        ]
        self._buttons_callbacks: list[Callable] = [
            self.start_button_callback,
            self.pause_button_callback,
            self.stop_button_callback,
        ]

        # Adds text Label
        self.timer_text = QtWidgets.QLabel(
            text=format_time(0), alignment=QtCore.Qt.AlignCenter
        )

        self.layout = QtWidgets.QVBoxLayout(self)

        self.button_layout = QtWidgets.QHBoxLayout()
        for btn in self._buttons:
            self.button_layout.addWidget(btn)

        self.layout.addWidget(self.timer_text)
        self.layout.addLayout(self.button_layout)

        self.start_button.clicked.connect(self.start_button_callback)
        self.pause_button.clicked.connect(self.pause_button_callback)
        self.stop_button.clicked.connect(self.stop_button_callback)

        self.update_timer = QtCore.QTimer(self)
        self.update_timer.timeout.connect(self.update)

    def get_time(self) -> int:
        return sum(self.times) + self.get_elapsed_time()

    def format_time(self) -> str:
        return format_time(self.get_time())

    def update(self) -> int:
        """General updating logic invoked every"""
        print("Update Invoked")
        self.timer_text.setText(self.format_time())

    def get_elapsed_time(self) -> int:
        if self.time_current_start is None:
            return 0
        return int(time.time() - self.time_current_start)

    @QtCore.Slot()
    def start_button_callback(self) -> None:
        self.timer_state = TimerState.IS_ACTIVE
        print("Timer Started")
        self.timer_is_active = True
        self.time_current_start = time.time()
        self.update_timer.start(200)

    @QtCore.Slot()
    def pause_button_callback(self) -> None:
        if self.timer_state == TimerState.IS_PAUSED:
            print("Pausing on paused")
            return
        self.timer_state = TimerState.IS_PAUSED
        print("Timer Paused")
        self.times.append(self.get_elapsed_time())
        self.timer_is_active = False
        self.update_timer.stop()

    @QtCore.Slot()
    def stop_button_callback(self) -> None:
        self.timer_state = TimerState.IS_INACTIVE
        print("Timer Stopped")
        self.timer_is_active = False
        self.update_timer.stop()
        with open("test.txt", "w") as file:
            file.write(
                f"Number of Chunks {len(self.times)} - Total Time = {self.get_time()}"
            )
        self.times = []
        self.time_current_start = None
        self.update()


def main() -> None:
    # QApplication takes in string arg list, maybe can omit?
    app = QtWidgets.QApplication([])

    widget = MyWidget()
    widget.resize(800, 600)
    # Prolly have to resize before showing, but could add it int the init logic, couldn't we?
    widget.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
