import sys, math, serial
from serial.tools import list_ports
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

STYLE = """
QWidget { background:#0e0e0e; color:#eaeaea; font-size:14px; }
QPushButton { background:#1b1b1b; border-radius:8px; padding:10px; }
QPushButton:hover { background:#2a2a2a; }
QComboBox { background:#1b1b1b; padding:6px; border-radius:6px; }
"""

class MotorView(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.setFixedSize(260, 260)
        self.setStyleSheet("border:none;")
        self.angle = 0

        s = QGraphicsScene(self)
        self.setScene(s)

        s.addEllipse(30, 30, 200, 200, QPen(QColor("#00e5ff"), 3))
        self.arm = s.addLine(130, 130, 130, 40, QPen(QColor("#00e5ff"), 4))

    def rotate(self, cw=True):
        self.angle += 6 if cw else -6
        r = math.radians(self.angle)
        self.arm.setLine(130, 130, 130 + 90*math.sin(r), 130 - 90*math.cos(r))


class App(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Stepper")
        self.setFixedSize(360, 520)
        self.setStyleSheet(STYLE)

        self.ser = None
        self.dir = True

        v = QVBoxLayout(self)
        self.box = QComboBox()
        v.addWidget(QLabel("Устройство"))
        v.addWidget(self.box)

        v.addWidget(self.btn("🔄 Обновить", self.scan))

        self.motor = MotorView()
        v.addWidget(self.motor, alignment=Qt.AlignmentFlag.AlignCenter)

        self.speed = QSlider(Qt.Orientation.Horizontal)
        self.speed.setRange(50, 300)
        v.addWidget(QLabel("Скорость"))
        v.addWidget(self.speed)

        h = QHBoxLayout()
        h.addWidget(self.btn("◀ CCW", lambda: self.start(False)))
        h.addWidget(self.btn("▶ CW", lambda: self.start(True)))
        v.addLayout(h)

        self.t = QTimer()
        self.t.timeout.connect(self.tick)

        self.scan()

    def btn(self, text, fn):
        b = QPushButton(text)
        b.clicked.connect(fn)
        return b

    def scan(self):
        self.box.clear()
        for p in list_ports.comports():
            self.box.addItem(p.device)

    def connect(self):
        if not self.ser and self.box.currentText():
            try:
                self.ser = serial.Serial(self.box.currentText(), 9600)
            except:
                pass

    def start(self, cw):
        self.dir = cw
        self.connect()
        self.t.start(30)

    def tick(self):
        self.motor.rotate(self.dir)
        if self.ser:
            try:
                self.ser.write(f"MOVE {'CW' if self.dir else 'CCW'} {self.speed.value()}\n".encode())
            except:
                pass


app = QApplication(sys.argv)
App().show()
sys.exit(app.exec())
