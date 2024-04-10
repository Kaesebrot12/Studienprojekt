import pyaudio
import numpy as np
import matplotlib.pyplot as plt
import signal
import sys

def signal_handler(sig, frame):
    print('You pressed Ctrl+C!')
    stream.stop_stream()
    stream.close()
    p.terminate()
    sys.exit(0)
def close_handler(evt):
    print('Closing the plot...')
    stream.stop_stream()
    stream.close()
    p.terminate()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# Konfiguration der Audioaufnahme
CHUNK = 4096  # Anzahl der Frames pro Buffer (increased buffer size)
FORMAT = pyaudio.paInt16  # Audioformat
CHANNELS = 1  # Anzahl der Audiokanäle
RATE = 44100  # Abtastrate (Anzahl der Frames pro Sekunde)

# Initialisierung der PyAudio-Instanz
p = pyaudio.PyAudio()

# Öffnen des Audio-Streams für die Aufnahme des Audioausgangs
stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

# Erstellen des Plots
plt.ion()  # Interaktiver Modus für Live-Updates
fig, ax = plt.subplots()
fig.canvas.mpl_connect('close_event', close_handler)
x = np.arange(0, CHUNK)
line, = ax.plot(x, np.random.rand(CHUNK))

try:
    # Live-Visualisierung des Audioausgangs
    while True:
        # Aufnahme des Audioausgangs
        data = stream.read(CHUNK)
        audio_data = np.frombuffer(data, dtype=np.int16)
        
        # Anwendung der Fourier-Transformation
        frequencies = np.fft.rfftfreq(CHUNK, 1./RATE)
        mask = frequencies <= 3000  # Nur Frequenzen bis 22050 Hz anzeigen
        frequencies = frequencies[mask]
        magnitudes = np.abs(np.fft.rfft(audio_data))[mask]

        # Visualisierung der aufgenommenen Daten
        line.set_xdata(frequencies)
        line.set_ydata(magnitudes)
        ax.set_xlim([frequencies.min(), frequencies.max()])
        ax.set_ylim([magnitudes.min(), magnitudes.max()])
        fig.canvas.draw()
        fig.canvas.flush_events()

except KeyboardInterrupt:
    # Wenn das Programm durch Drücken von Ctrl+C unterbrochen wird, beenden wir die Schleife
    pass
finally:
    # Beenden des Audio-Streams und der PyAudio-Instanz
    stream.stop_stream()
    stream.close()
    p.terminate()