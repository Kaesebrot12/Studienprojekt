import tkinter as tk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import sounddevice as sd
import threading

# Set the sample rate and buffer size
sample_rate = 44100
buffer_size = 1024

# Funktion zur QAM-Modulation
def qam_modulate(data, carrier_freq, sample_rate):
    # Convert data to bits
    bits = ''.join(format(ord(i), '08b') for i in data)

    # Group bits into symbols
    n = 4  # 4 bits per symbol for 16-QAM
    symbols = [bits[i:i+n] for i in range(0, len(bits), n)]

    # Convert symbols to complex numbers
    constellation = np.array([-3-3j, -3-1j, -3+3j, -3+1j, -1-3j, -1-1j, -1+3j, -1+1j, 3-3j, 3-1j, 3+3j, 3+1j, 1-3j, 1-1j, 1+3j, 1+1j])
    points = [constellation[int(symbol, 2)] for symbol in symbols]

    # Modulate the signal
    t = np.arange(0, len(points) / carrier_freq, 1 / sample_rate)
    signal = np.concatenate([np.real(point) * np.cos(2 * np.pi * carrier_freq * t[i:i+int(sample_rate/carrier_freq)]) - np.imag(point) * np.sin(2 * np.pi * carrier_freq * t[i:i+int(sample_rate/carrier_freq)]) for i, point in enumerate(points)])

    return signal

# Funktion zum Visualisieren des Tons im Frequenzbereich
def plot_sound(signal):
    freq = np.fft.fftfreq(len(signal), 1/sample_rate)
    spectrum = np.abs(np.fft.fft(signal))
    ax.clear()
    ax.plot(freq, spectrum)
    ax.set_xlabel('Frequency (Hz)')
    ax.set_ylabel('Magnitude')
    ax.set_xlim([0, 9000])
    canvas.draw()

# Funktion zum Abspielen und Visualisieren eines Tons
def play_and_visualize(signal):
    sd.play(signal, sample_rate, blocksize=buffer_size)  # Play the signal
    sd.wait()
    window.after(10, plot_sound, signal)  # Call plot_sound from the main thread

# Set the buffer size for sounddevice
sd.default.samplerate = sample_rate
sd.default.blocksize = buffer_size

# Create a GUI window
window = tk.Tk()

# Create a text input field
text_input = tk.Entry(window)
text_input.pack()

# Create a button to start the modulation
modulate_button = tk.Button(window, text="Modulate and Play", command=lambda: threading.Thread(target=play_and_visualize, args=(qam_modulate(text_input.get(), 1500, sample_rate),)).start())
modulate_button.pack()

def start_thread(signal):
    thread = threading.Thread(target=play_and_visualize, args=(signal,))
    thread.daemon = True
    thread.start()

# Create a canvas for the plot
fig = Figure(figsize=(5, 4), dpi=100)
ax = fig.add_subplot(111)
canvas = FigureCanvasTkAgg(fig, master=window)
canvas.draw()
canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

# Run the GUI
window.mainloop()