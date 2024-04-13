import tkinter as tk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import sounddevice as sd
import threading
#test
# Set the sample rate and buffer size
sample_rate = 44100
buffer_size = 1024

# Funktion zum Abspielen des Tons
def play_sound(frequency):
    duration = 1.0  # seconds
    samples = np.sin(2 * np.pi * frequency * np.arange(duration * sample_rate) / sample_rate)
    sd.play(samples, sample_rate, blocksize=buffer_size)
    sd.wait()

# Funktion zum Visualisieren des Tons im Frequenzbereich
def plot_sound(frequency):
    duration = 1.0  # seconds
    samples = np.sin(2 * np.pi * frequency * np.arange(duration * sample_rate) / sample_rate)
    freq = np.fft.fftfreq(len(samples), 1/sample_rate)
    spectrum = np.abs(np.fft.fft(samples))
    ax.clear()
    ax.plot(freq, spectrum)
    ax.set_xlabel('Frequency (Hz)')
    ax.set_ylabel('Magnitude')
    ax.set_xlim([0, 1600])
    canvas.draw()

# Funktion zum Abspielen und Visualisieren eines Tons
def play_and_visualize():
    for frequency in frequencies:
        play_sound(frequency)
        window.after(10, plot_sound, frequency)  # Call plot_sound from the main thread

# Set the buffer size for sounddevice
sd.default.samplerate = sample_rate
sd.default.blocksize = buffer_size

# Create a GUI window
window = tk.Tk()

# Create a text input field
text_input = tk.Entry(window)
text_input.pack()

# Create a matplotlib figure and add it to the tkinter GUI
fig = Figure(figsize=(5, 4), dpi=100)
ax = fig.add_subplot(111)
canvas = FigureCanvasTkAgg(fig, master=window)
canvas.draw()
canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

# Function to handle button click event
def process_text():
    text = text_input.get()
    global frequencies
    frequencies = [300 + ord(char) * 10 for char in text]
    threading.Thread(target=play_and_visualize).start()

# Create a button to process the text
process_button = tk.Button(window, text="Process Text", command=process_text)
process_button.pack()

# Start the GUI event loop
window.mainloop()