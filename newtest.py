import tkinter as tk
import tkinter.messagebox as messagebox
import speech_recognition as sr
import threading
import pyaudio
import wave
import os
import platform
import re
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize

def preprocess_data(sent):
    lower_case = sent.lower()
    tokenize_data = word_tokenize(lower_case)
    stop_word=set(stopwords.words('english'))
    filter_data = [word for word in tokenize_data if word not in stop_word ]
    lemmatizer = WordNetLemmatizer()
    data = [lemmatizer.lemmatize(word) for word in filter_data] 
    preprocessed_text=" ".join(data)
    return preprocessed_text

    


class SpeechToTextApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Speech to text converter")

        self.record_button = tk.Button(self, text="Start Recording", command=self.start_recording)
        self.record_button.pack(pady=20)

        self.stop_button = tk.Button(self, text="Stop Recording", command=self.stop_recording, state=tk.DISABLED)
        self.stop_button.pack(pady=20)

        self.play_button = tk.Button(self, text="Play Recording", command=self.play_recording, state=tk.DISABLED)
        self.play_button.pack(pady=20)

        self.convert_button = tk.Button(self, text="Convert Recording", command=self.convert_audio_to_text, state=tk.DISABLED)
        self.convert_button.pack(pady=20)

        self.audio_file_path = "recorded_audio.wav"
        self.recording = False

    def start_recording(self):
        self.frames = []  # Clear previous recordings
        self.recording = True
        self.record_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.play_button.config(state=tk.DISABLED)
        self.convert_button.config(state=tk.DISABLED)

        self.audio = pyaudio.PyAudio()#it helps in interacting with input/output devices
        self.stream = self.audio.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, frames_per_buffer=1024)

        self.recording_thread = threading.Thread(target=self.record)
        self.recording_thread.start()

    def record(self):
        while self.recording:
            data = self.stream.read(1024)
            self.frames.append(data)

    def stop_recording(self):
        self.recording = False
        self.stream.stop_stream()
        self.stream.close()
        self.audio.terminate()

        wf = wave.open(self.audio_file_path, 'wb')
        wf.setnchannels(1)
        wf.setsampwidth(self.audio.get_sample_size(pyaudio.paInt16))
        wf.setframerate(44100)
        wf.writeframes(b"".join(self.frames))
        wf.close()

        self.record_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.play_button.config(state=tk.NORMAL)
        self.convert_button.config(state=tk.NORMAL)

    def play_recording(self):
        try:
            if platform.system() == "Windows":
                os.system(f"start {self.audio_file_path}")
            elif platform.system() == "Darwin":  # macOS
                os.system(f"open {self.audio_file_path}")
            else:  # Linux
                os.system(f"aplay {self.audio_file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not play the audio file: {e}")

    def convert_audio_to_text(self):
        r = sr.Recognizer()
        try:
            with sr.AudioFile(self.audio_file_path) as source:
                audio_data = r.record(source)
                try:
                    text = r.recognize_google(audio_data)
                    messagebox.showinfo("Speech to text", text)
                except sr.UnknownValueError:
                    messagebox.showwarning("Speech to text", "Could not understand the audio")
                except sr.RequestError as e:
                    messagebox.showerror("Speech to text", f"Error occurred: {e}")
        except FileNotFoundError:
            messagebox.showerror("Error", "Audio file not found. Please record first.")

if __name__ == "__main__":
    app = SpeechToTextApp()
    app.mainloop()
