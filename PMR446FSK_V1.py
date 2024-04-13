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

class MyMplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super().__init__(fig)
        self.setParent(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.updateGeometry()
        self.figure.subplots_adjust(bottom=0.2)

class RecievedSignal(MyMplCanvas):
    def __init__(self, recievedText, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.recievedText = recievedText
        self.axes.set_yscale("log")
        self.axes.set_ylim(100, 100000000)
        self.axes.set_ylabel("Mag")
        self.axes.set_xlim(0, 3000)
        self.axes.set_xlabel("Hz")
        self.CHUNK = 4096
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 44100
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=self.FORMAT, channels=self.CHANNELS, rate=self.RATE, input=True, frames_per_buffer=self.CHUNK)
        x = np.arange(0, self.CHUNK)
        self.line, = self.axes.plot(x, np.random.rand(self.CHUNK))
        self.dominant_frequencies = [0] * 10
        self.frequency_dict = {char: 300 + ord(char) * 10 for char in map(chr, range(128))}
        timer = QtCore.QTimer(self)
        timer.timeout.connect(self.update_figure)
        timer.start(1)

    def update_figure(self):
        if self.stream.is_active():
            data = self.stream.read(self.CHUNK)
        audio_data = np.frombuffer(data, dtype=np.int16)
        frequencies = np.fft.rfftfreq(self.CHUNK, 1./self.RATE)
        mask = frequencies <= 3000
        frequencies = frequencies[mask]
        magnitudes = np.abs(np.fft.rfft(audio_data))[mask]
        dominant_frequency_index = np.argmax(magnitudes)
        dominant_frequency = frequencies[dominant_frequency_index]
        if len(self.dominant_frequencies) >= 10:
            self.dominant_frequencies.pop(0)
            self.dominant_frequencies.append(dominant_frequency)
        if all(round(frequency, 1) == round(self.dominant_frequencies[0], 1) for frequency in self.dominant_frequencies) and max(self.dominant_frequencies) > 0:
            closest_char = min(self.frequency_dict.keys(), key=lambda char: abs(self.frequency_dict[char] - dominant_frequency))
            current_text = self.recievedText.toPlainText()
            updated_text = current_text + closest_char
            self.recievedText.setPlainText(updated_text)
            self.dominant_frequencies = [0] * len(self.dominant_frequencies)
        self.line.set_xdata(frequencies)
        self.line.set_ydata(magnitudes)
        self.draw()

class SendSignalThread(QThread):
    frequency_played = pyqtSignal(float)
    def __init__(self, send_signal):
        super().__init__()
        self.send_signal = send_signal
        self.sample_rate = 44100
        self.buffer_size = 1024 
        self.text = "" 

    def send_text(self, text):
        self.text = text

    def run(self):
        frequencies = [300 + ord(char) * 10 for char in self.text]
        frequencies.append(400)
        for frequency in frequencies:
            self.plot_sound(frequency)
            duration = 1
            samples = np.sin(2 * np.pi * frequency * np.arange(duration * self.sample_rate) / self.sample_rate)
            sd.play(samples, self.sample_rate, blocksize=self.buffer_size)
            sd.wait()

    def plot_sound(self, frequency):
        QMetaObject.invokeMethod(self.send_signal, "plot_sound", Qt.QueuedConnection, Q_ARG(float, frequency))   

class SendSignal(MyMplCanvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sample_rate = 44100
        self.axes.set_ylabel("Mag")
        self.axes.set_xlabel("Hz")
        self.axes.set_xlim(0, 1600)
        self.line, = self.axes.plot([], [])

    @pyqtSlot(float)
    def plot_sound(self, frequency):
        duration = 1.0
        samples = np.sin(2 * np.pi * frequency * np.arange(duration * self.sample_rate) / self.sample_rate)
        freq = np.fft.fftfreq(len(samples), 1/self.sample_rate)
        spectrum = np.abs(np.fft.fft(samples))
        self.line.set_data(freq, spectrum)
        self.axes.relim()
        self.axes.autoscale_view()
        self.draw()

class ApplicationWindow(QMainWindow):
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
        send_button.clicked.connect(self.send_text_method)
        recieved_signal = RecievedSignal(recieved_text, self.main_widget, width=5, height=6, dpi=100)
        self.send_signal = SendSignal(self.main_widget, width=5, height=6, dpi=100)
        self.send_signal_thread = SendSignalThread(self.send_signal)
        recieved_signal_label = QLabel("Received Signal", self.main_widget)
        send_signal_label = QLabel("Send Signal", self.main_widget)
        recieved_text_label = QLabel("Received Text", self.main_widget)
        send_text_label = QLabel("Send Text", self.main_widget)
        grid_layout.addWidget(recieved_signal_label, 0, 0)
        grid_layout.addWidget(recieved_signal, 1, 0)
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

    def send_text_method(self):
        text = self.send_text.toPlainText()
        self.send_signal_thread.send_text(text)
        self.send_signal_thread.start()
        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        text_with_time = current_time + " " + text
        current_text = self.read_only_sent.toPlainText()
        updated_text = current_text + "\n" + text_with_time
        self.read_only_sent.setPlainText(updated_text)
        self.send_text.clear()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    aw = ApplicationWindow()
    aw.setWindowTitle("PMR446FSK")
    aw.show()
    sys.exit(app.exec_())