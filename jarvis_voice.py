import speech_recognition as sr
import pyttsx3
import datetime
import os
import webbrowser

engine = pyttsx3.init()
engine.setProperty("rate", 180)

def speak(text):
    print("JARVIS:", text)
    engine.say(text)
    engine.runAndWait()

recognizer = sr.Recognizer()

speak("Jarvis online")

while True:
    try:
        with sr.Microphone() as source:
            print("Listening...")

            recognizer.adjust_for_ambient_noise(source, duration=1)

            audio = recognizer.listen(source)

            command = recognizer.recognize_google(audio)
            command = command.lower()

            print("You said:", command)

            if "hello" in command:
                speak("Hello Unnati")

            elif "time" in command:
                current_time = datetime.datetime.now().strftime("%I:%M %p")
                speak(f"The time is {current_time}")

            elif "open youtube" in command:
                speak("Opening YouTube")
                webbrowser.open("https://www.youtube.com")

            elif "open google" in command:
                speak("Opening Google")
                webbrowser.open("https://www.google.com")

            elif "open calculator" in command:
                speak("Opening Calculator")
                os.system("calc")

            elif "open notepad" in command:
                speak("Opening Notepad")
                os.system("notepad")

            elif "open camera" in command:
                speak("Opening Camera")
                os.system("start microsoft.windows.camera:")
                
            elif "open spotify" in command:
                speak("Opening spotify")
                os.system("spotify")

            elif "exit" in command:
                speak("Goodbye")
                break

            else:
                speak("I did not understand that command")

    except Exception as e:
        print("Error:", e)
