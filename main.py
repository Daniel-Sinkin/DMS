import random
import sys

from PySide6 import QtCore, QtGui, QtWidgets


class MyWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.hello = ["Hallo Welt", "Hei maailma", "Hola Mundo", "Privet Mir"]

        # Creates a Button
        self.button = QtWidgets.QPushButton("Click me!")

        # Adds text Label
        self.text = QtWidgets.QLabel("Hello World", alignment=QtCore.Qt.AlignCenter)

        # Creates a box layout? Is self.layout a magic variable?
        # IIRC box is autoplacement
        self.layout = QtWidgets.QVBoxLayout(self)
        # Adds the text label to the layout, placed by BoxLayout logic
        self.layout.addWidget(self.text)
        # Adds the button to the layout
        self.layout.addWidget(self.button)

        # button has a magic clicked callback that invokes the function "magic"
        # I guess QtCore.Slot makes it into a suitable callback target?
        self.button.clicked.connect(self.magic)

    def make_me_smaller(self) -> None:
        curr_size = self.size()
        if curr_size.width() > 100 and curr_size.height() > 100:
            self.resize(curr_size - QtCore.QSize(20, 20))

    @QtCore.Slot()
    def magic(self) -> None:
        # Side effect of changing the text
        self.text.setText(random.choice(self.hello))
        self.make_me_smaller()


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
