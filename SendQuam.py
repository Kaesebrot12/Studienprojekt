import tkinter as tk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import sounddevice as sd
import threading
from mod_Quam import qam_modulate

# Set the sample rate and buffer size
sample_rate = 44100
buffer_size = 1024

# Funktion zum Visualisieren des Tons im Frequenzbereich
def plot_sound(signal):
    freq = np.fft.fftfreq(len(signal), 1/sample_rate)
    spectrum = np.abs(np.fft.fft(signal))
    ax.clear()
    ax.plot(freq, spectrum)
    ax.set_xlabel('Frequency (Hz)')
    ax.set_ylabel('Magnitude')
    ax.set_xlim([0, 5000])
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