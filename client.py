import datetime as dt
import json
import sys
from typing import cast

import matplotlib.pyplot as plt
import pandas as pd
import Pyro5.api
from PyQt5 import QtCore, QtWidgets


class MainWindow(QtWidgets.QWidget):
    def __init__(self, data_provider: Pyro5.api.Proxy):
        super().__init__()
        self.data_provider = data_provider
        self.initUI()
        self.update_price()

    def initUI(self):
        self.label = QtWidgets.QLabel("Price: ", self)
        self.button = QtWidgets.QPushButton("Get Ticks", self)
        self.button.clicked.connect(self.get_ticks)
        self.text_area = QtWidgets.QTextEdit(self)
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.button)
        layout.addWidget(self.text_area)
        self.setLayout(layout)
        # Set up a timer to update the price every 0.2 seconds
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_price)
        self.timer.start(200)  # 200 milliseconds

    def update_price(self):
        # Fetch the current price from the DataProvider
        bid, ask = cast(tuple[int, int], self.data_provider.get_current_price())
        self.label.setText(f"Bid: {bid:.2f}, Ask: {ask:.2f}")

    def get_ticks(self):
        # Fetch ticks from the DataProvider
        json_data = self.data_provider.get_ticks()
        ticks = pd.read_json(json_data, orient="records")
        plt.plot(ticks["timestamp"], ticks["bid"])
        plt.savefig(f"{int(dt.datetime.now().timestamp() * 1000)}.png")
        plt.clf()
        self.text_area.clear()
        ticks["timestamp"] = ticks["timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S")

        self.text_area.append(ticks.to_string(index=False))


def main():
    # Connect to the DataProvider via Pyro5
    data_provider = Pyro5.api.Proxy("PYRONAME:example.dataprovider")
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow(data_provider)
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
