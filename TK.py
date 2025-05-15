import tkinter as tk
from tkinter import Label, Button
import threading
import BE  # Import backend script
import morse_code

# Create GUI window
root = tk.Tk()
root.title("Eye Blink Morse Code Detector")
root.geometry("600x400")

stop_event = threading.Event()  
morse_label = Label(root, text="Morse Code: ", font=("Arial", 14))
morse_label.pack(pady=10)
translated_label = Label(root, text="Translated Text: ", font=("Arial", 14))
translated_label.pack(pady=10)

def run_detection():
    stop_event.clear()
    def detection_thread():
        detected_morse = BE.run_morse_detection(stop_event)
        translated_text = morse_code.from_morse(detected_morse)
        morse_label.config(text=f"Morse Code: {detected_morse}")
        translated_label.config(text=f"Translated Text: {translated_text}")

    thread = threading.Thread(target=detection_thread, daemon=True)
    thread.start()

def stop_detection():
    stop_event.set()

Button(root, text="Start Detection", command=run_detection).pack(pady=5)

root.mainloop()
