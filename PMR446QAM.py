from asyncio import wait
import sys
import datetime
import numpy as np
import pyaudio
import sounddevice as sd
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QSizePolicy, QGridLayout, QTextEdit, QLabel, QPushButton
from PyQt5 import QtCore
from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot, QMetaObject, Qt, Q_ARG
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class staticPlot(FigureCanvas):
  def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super().__init__(fig)
        self.setParent(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.updateGeometry()
        self.figure.subplots_adjust(bottom=0.2)


class RecievedSignal(staticPlot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args,**kwargs)
        self.axes.set_yscale("log")
        self.axes.set_ylim(100, 100000000)
        self.axes.set_ylabel("Mag")
        self.axes.set_xlim(0, 3000)
        self.axes.set_xlabel("Hz")
        self.line, = self.axes.plot([], [])
        
    @pyqtSlot(np.ndarray)
    def update_data(self, spectrum):
        self.line.set_xdata(np.arange(len(spectrum))) 
        self.line.set_ydata(spectrum)
        self.draw()

class SendSignal(staticPlot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args,**kwargs)
        self.axes.set_yscale("log")
        self.axes.set_ylim(100, 100000000)
        self.axes.set_ylabel("Mag")
        self.axes.set_xlim(0, 3000)
        self.axes.set_xlabel("Hz")
        self.x_data = np.linspace(0, 3000, 1024)  # Erstellen Sie x-Daten der gleichen Länge wie die y-Daten
        self.line, = self.axes.plot(self.x_data, np.zeros_like(self.x_data))  # Initialisieren Sie die y-Daten mit Nullen der gleichen Länge wie die x-Daten


class ThreadSendSignal(QThread):
    frequency_played = pyqtSignal(float)

class ThreadRecieveSignal(QThread):
    spectrum_recieved = pyqtSignal(np.ndarray)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.running = True

    def run(self):
        RATE = 44100
        CHUNK = 1024
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paFloat32, channels=1, rate=RATE, input=True, frames_per_buffer=CHUNK)

        while self.running:
            if stream.get_read_available() >= CHUNK:  # Überprüfen, ob genug Daten zum Lesen vorhanden sind
                data = np.frombuffer(stream.read(CHUNK), dtype=np.float32)
                spectrum = np.fft.fftfreq(len(data))
                self.spectrum_recieved.emit(spectrum)
               
          

        stream.stop_stream()
        stream.close()
        p.terminate()

    def stop(self):
        self.running = False


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.main_widget = QWidget(self)
        grid_layout = QGridLayout(self.main_widget)
        recieved_text = QTextEdit(self.main_widget)
        recieved_text.setReadOnly(True)
        self.read_only_sent = QTextEdit(self.main_widget)
        self.read_only_sent.setReadOnly(True)
        self.send_text = QTextEdit(self.main_widget)
        send_button = QPushButton('Send', self.main_widget)
      #  send_button.clicked.connect(self.send_text_method)
        self.recieved_signal = RecievedSignal(self.main_widget, width=5, height=6, dpi=100)
        self.threadRecieveSignal = ThreadRecieveSignal()
        self.threadRecieveSignal.spectrum_recieved.connect(self.recieved_signal.update_data)
        self.threadRecieveSignal.start()
        self.send_signal = SendSignal(self.main_widget, width=5, height=6, dpi=100)
#self.send_signal_thread = SendSignalThread(self.send_signal)
        recieved_signal_label = QLabel("Received Signal", self.main_widget)
        send_signal_label = QLabel("Send Signal", self.main_widget)
        recieved_text_label = QLabel("Received Text", self.main_widget)
        send_text_label = QLabel("Send Text", self.main_widget)
        grid_layout.addWidget(recieved_signal_label, 0, 0)
        grid_layout.addWidget(self.recieved_signal, 1, 0)
        grid_layout.addWidget(send_signal_label, 2, 0)
        grid_layout.addWidget(self.send_signal, 3, 0)
        grid_layout.addWidget(recieved_text_label, 0, 1)
        grid_layout.addWidget(recieved_text, 1, 1)
        grid_layout.addWidget(send_text_label, 2, 1)
        grid_layout.addWidget(self.send_text, 4, 1)
        grid_layout.addWidget(send_button, 5, 1)
        grid_layout.addWidget(self.read_only_sent, 3, 1) 
        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)

    def closeEvent(self, event):
        # Beenden Sie den Thread, wenn das Fenster geschlossen wird
        self.threadRecieveSignal.stop()
        event.accept()
if __name__ == '__main__':
    app = QApplication(sys.argv)
    aw = MainWindow()
    aw.setWindowTitle("PMR446QAM")
    aw.show()
    sys.exit(app.exec_())

