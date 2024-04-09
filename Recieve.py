import pyaudio
import numpy as np
import matplotlib.pyplot as plt

# Konfiguration der Audioaufnahme
CHUNK = 1024  # Anzahl der Frames pro Buffer
FORMAT = pyaudio.paInt16  # Audioformat
CHANNELS = 1  # Anzahl der Audiokanäle
RATE = 44100  # Abtastrate (Anzahl der Frames pro Sekunde)

# Initialisierung der PyAudio-Instanz
p = pyaudio.PyAudio()

# Öffnen des Audio-Streams
stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

# Erstellen des Plots
plt.ion()  # Interaktiver Modus für Live-Updates
fig, ax = plt.subplots()
x = np.arange(0, CHUNK)
line, = ax.plot(x, np.random.rand(CHUNK))

# Live-Visualisierung des Audioausgangs
while True:
    data = stream.read(CHUNK)
    audio_data = np.frombuffer(data, dtype=np.int16)
    line.set_ydata(audio_data)
    fig.canvas.draw()
    fig.canvas.flush_events()

# Beenden des Audio-Streams und der PyAudio-Instanz
stream.stop_stream()
stream.close()
p.terminate()

