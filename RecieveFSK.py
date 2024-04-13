import pyaudio
import numpy as np
import matplotlib.pyplot as plt
import signal
import sys
import warnings
import threading
import tkinter as tk
warnings.filterwarnings("ignore")



# Funktion zum Erstellen und Starten des Tkinter-Fensters
def create_window():
    window = tk.Tk()
    window.geometry("800x600")  # Setzt die Größe des Fensters auf 800x600 Pixel
    global text_var  # Damit die Variable auch außerhalb der Funktion verfügbar ist
    text_var = tk.StringVar()
    label = tk.Label(window, textvariable=text_var)
    label.pack()
    window.mainloop()

# Erstellen und Starten des Tkinter-Threads
tkinter_thread = threading.Thread(target=create_window)
tkinter_thread.start()


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

frequency_dict = {char: 300 + ord(char) * 10 for char in map(chr, range(128))}

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
dominant_frequencies = [0] * 10

try:
    # Live-Visualisierung des Audioausgangs
    while True:
        # Aufnahme des Audioausgangs
        if stream.is_active():
            data = stream.read(CHUNK)
        audio_data = np.frombuffer(data, dtype=np.int16)
        
        # Anwendung der Fourier-Transformation
        frequencies = np.fft.rfftfreq(CHUNK, 1./RATE)
        mask = frequencies <= 3000  # Nur Frequenzen bis 22050 Hz anzeigen
        frequencies = frequencies[mask]
        magnitudes = np.abs(np.fft.rfft(audio_data))[mask]
        # Finden der dominanten Frequenz
        dominant_frequency_index = np.argmax(magnitudes)
        dominant_frequency = frequencies[dominant_frequency_index]
        # Füge die dominante Frequenz zur Liste hinzu und entferne das erste Element, wenn die Liste voll ist
        if len(dominant_frequencies) >= 10:
            dominant_frequencies.pop(0)
        dominant_frequencies.append(dominant_frequency)
      

        if all(round(frequency, 1) == round(dominant_frequencies[0], 1) for frequency in dominant_frequencies)and max(dominant_frequencies) > 0:
            # Finde den Buchstaben mit der nächstgelegenen Frequenz im Dictionary
            closest_char = min(frequency_dict.keys(), key=lambda char: abs(frequency_dict[char] - dominant_frequency))
            print("Konstanter Ton: ", closest_char)
            current_text = text_var.get()
            new_text = closest_char
            text_var.set(current_text + new_text)
            dominant_frequencies = [0] * len(dominant_frequencies)  # Setze die Liste auf Null

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