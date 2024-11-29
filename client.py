import sys
import time
from io import BytesIO, StringIO
from typing import cast

import matplotlib.pyplot as plt
import pandas as pd
import Pyro5.api
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import QPixmap


class MainWindow(QtWidgets.QWidget):
    def __init__(self, data_provider: Pyro5.api.Proxy):
        super().__init__()
        self.data_provider = data_provider
        self.initUI()
        self.update_price()

    def initUI(self):
        self.label = QtWidgets.QLabel("Price: ", self)
        self.table_widget = QtWidgets.QTableWidget(self)
        self.image_label = QtWidgets.QLabel(self)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.table_widget)
        layout.addWidget(self.image_label)
        self.setLayout(layout)

        self.price_timer = QtCore.QTimer()
        self.price_timer.timeout.connect(self.update_price)
        self.price_timer.start(100)

        self.ticks_timer = QtCore.QTimer()
        self.ticks_timer.timeout.connect(self.get_ticks)
        self.ticks_timer.start(100)

    def update_price(self):
        bid, ask = cast(tuple[int, int], self.data_provider.get_current_price())
        self.label.setText(f"Bid: {bid:.2f}, Ask: {ask:.2f}")

    def get_ticks(self):
        json_data: str = self.data_provider.get_ticks()

        json_io = StringIO(json_data)
        ticks = pd.read_json(json_io, orient="records")
        ticks["timestamp"] = pd.to_datetime(ticks["timestamp"])

        # Plot the data
        plt.figure(figsize=(8, 4))
        plt.plot(ticks["timestamp"], ticks["bid"], label="Bid Price")
        plt.plot(ticks["timestamp"], ticks["ask"], label="Ask Price")

        plt.gca().set_facecolor("#2f2f2f")
        plt.gcf().set_facecolor("#1f1f1f")
        plt.gca().spines["bottom"].set_color("white")
        plt.gca().spines["left"].set_color("white")
        plt.gca().spines["top"].set_color("white")
        plt.gca().spines["right"].set_color("white")
        plt.gca().xaxis.label.set_color("white")
        plt.gca().yaxis.label.set_color("white")
        plt.gca().tick_params(axis="x", colors="white")
        plt.gca().tick_params(axis="y", colors="white")
        plt.title("Bid Price Over Time", color="white")
        plt.xlabel("Timestamp", color="white")
        plt.ylabel("Price", color="white")
        plt.legend(facecolor="#2f2f2f", edgecolor="white", labelcolor="white")
        plt.ylim((95, 110))
        plt.tight_layout()

        # Save the figure to a buffer
        buf = BytesIO()
        plt.savefig(buf, format="png")
        buf.seek(0)
        plt.close()

        ticks["timestamp"] = ticks["timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S")

        self.table_widget.clear()
        self.table_widget.setRowCount(len(ticks))
        self.table_widget.setColumnCount(len(ticks.columns))
        self.table_widget.setHorizontalHeaderLabels(ticks.columns)

        for i, row in ticks.iterrows():
            for j, (column, value) in enumerate(row.items()):
                item = QtWidgets.QTableWidgetItem(str(value))
                self.table_widget.setItem(i, j, item)

        pixmap = QPixmap()
        pixmap.loadFromData(buf.getvalue())

        self.image_label.setPixmap(pixmap)
        self.image_label.setScaledContents(True)
        self.image_label.setFixedSize(800, 400)


def main():
    max_retries = 20
    retries = 0
    data_provider = None

    while retries < max_retries:
        try:
            data_provider = Pyro5.api.Proxy("PYRONAME:example.dataprovider")
            data_provider._pyroBind()
            break
        except Pyro5.errors.CommunicationError as e:
            data_provider = None
            print(
                f"Connection attempt {retries + 1} failed: {e}. Retrying in 3 seconds..."
            )
            retries += 1
            time.sleep(3.0)

    if data_provider is None:
        print("Failed to connect to the Pyro5 server after multiple retries. Exiting.")
        sys.exit(1)

    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow(data_provider)
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
