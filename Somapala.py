import pyttsx3
import speech_recognition as sr
import os
import pyautogui
import openai
import pywhatkit
import threading
import tkinter as tk
from itertools import cycle
import requests
import logging
import webbrowser
import cv2
from datetime import datetime, timedelta
from google.oauth2 import service_account
from googleapiclient.discovery import build
import smtplib
import imaplib
import email
import re
from textblob import TextBlob
import time

# Initialize the text-to-speech engine
engine = pyttsx3.init()
engine.setProperty("rate", 150)
engine.setProperty("volume", 1.0)

# OpenAI API key setup
openai.api_key = os.getenv('OPENAI_API_KEY')

# LibreTranslate API endpoint
libretranslate_endpoint = 'https://libretranslate.com'

# OpenWeatherMap API key
weather_api_key = 'your_openweathermap_api_key'

# Google Calendar API setup
SCOPES = ['https://www.googleapis.com/auth/calendar']
SERVICE_ACCOUNT_FILE = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
calendar_service = build('calendar', 'v3', credentials=credentials)

# Email configuration
EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
IMAP_SERVER = os.getenv('IMAP_SERVER', 'imap.gmail.com')

# Logging configuration
logging.basicConfig(filename='somapala.log', level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')

class SomapalaGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Somapala")
        self.geometry("400x400")
        self.label = tk.Label(self, text="Somapala is ready to assist you!", font=("Helvetica", 14))
        self.label.pack(pady=20)
        self.working_label = tk.Label(self, text="", font=("Helvetica", 12))
        self.working_label.pack(pady=20)
        self.animation_running = False

    def start_animation(self):
        if not self.animation_running:
            self.animation_running = True
            self.working_label.config(text="Somapala is working...")
            self._animate()

    def stop_animation(self):
        self.animation_running = False
        self.working_label.config(text="")

    def _animate(self):
        if self.animation_running:
            self.working_label.config(text="Somapala is working " + next(self.animation_cycle))
            self.after(300, self._animate)

    def set_animation_cycle(self, sequence):
        self.animation_cycle = cycle(sequence)

gui = SomapalaGUI()
gui.set_animation_cycle([".", "..", "...", "...."])

def speak(text, language='en'):
    """Speak out the given text in the specified language using SSML"""
    if language == 'en':
        ssml_text = f"<speak>{text}</speak>"
    else:
        ssml_text = f"<speak><lang xml:lang='es'>{text}</lang></speak>"
    engine.say(ssml_text)
    engine.runAndWait()

def translate_text(text, target_language):
    """Translate text to the target language using LibreTranslate API"""
    url = f"{libretranslate_endpoint}/translate"
    headers = {'Content-Type': 'application/json'}
    body = {
        'q': text,
        'source': 'auto',
        'target': target_language,
        'format': 'text'
    }
    try:
        response = requests.post(url, headers=headers, json=body)
        response.raise_for_status()
        result = response.json()
        return result['translatedText']
    except Exception as e:
        logging.error(f"Error during translation: {e}")
        return ""

def recognize_speech(audio_data):
    """Convert audio to text"""
    recognizer = sr.Recognizer()
    try:
        command = recognizer.recognize_google(audio_data).lower()
        logging.info(f"Recognized command: {command}")
        return command
    except sr.UnknownValueError:
        logging.error("Speech recognition failed: UnknownValueError")
        return ""
    except sr.RequestError:
        logging.error("Speech recognition failed: RequestError")
        return ""

def capture_audio(duration=5):
    """Capture audio from the system"""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        audio_data = recognizer.listen(source, phrase_time_limit=duration)
        return audio_data

def detect_whatsapp_call():
    """Detect an ongoing WhatsApp call (conceptual)"""
    # This function should detect the WhatsApp call screen using image recognition
    # Placeholder implementation using pyautogui to take screenshots
    while True:
        screenshot = pyautogui.screenshot()
        # Add logic to detect WhatsApp call screen
        # For now, we simulate with a sleep
        time.sleep(5)
        # If detected, return True
        return True

def translate_call():
    """Translate the ongoing call"""
    while True:
        audio_data = capture_audio()
        recognized_text = recognize_speech(audio_data)
        if recognized_text:
            if "translate to spanish" in recognized_text:
                target_language = 'es'
            elif "translate to english" in recognized_text:
                target_language = 'en'
            else:
                target_language = 'en' if detect_language(recognized_text) == 'es' else 'es'
            
            translated_text = translate_text(recognized_text, target_language)
            if translated_text:
                speak(translated_text, language=target_language)

def detect_language(text):
    """Detect the language of the text using LibreTranslate API"""
    url = f"{libretranslate_endpoint}/detect"
    headers = {'Content-Type': 'application/json'}
    body = {'q': text}
    try:
        response = requests.post(url, headers=headers, json=body)
        response.raise_for_status()
        result = response.json()
        return result[0]['language']
    except Exception as e:
        logging.error(f"Error detecting language: {e}")
        return ""

def get_weather(city):
    """Get weather information for a specified city using OpenWeatherMap API"""
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={weather_api_key}&units=metric"
    try:
        response = requests.get(url)
        response.raise_for_status()
        weather_data = response.json()
        description = weather_data['weather'][0]['description']
        temperature = weather_data['main']['temp']
        weather_info = f"The weather in {city} is {description} with a temperature of {temperature}°C."
        return weather_info
    except Exception as e:
        logging.error(f"Error fetching weather data: {e}")
        return "There was an error fetching the weather data."

def open_application(command):
    """Open common applications"""
    if "browser" in command:
        webbrowser.open("https://www.google.com")
        speak("Opening browser.")
    elif "notepad" in command:
        os.system("notepad")
        speak("Opening Notepad.")
    elif "calculator" in command:
        os.system("calc")
        speak("Opening Calculator.")
    elif "command prompt" in command or "terminal" in command:
        os.system("cmd")
        speak("Opening Command Prompt.")
    elif "chrome" in command:
        chrome_path = "C:/Program Files/Google/Chrome/Application/chrome.exe %s"
        webbrowser.get(chrome_path).open("https://www.google.com")
        speak("Opening Chrome browser.")
    elif "file explorer" in command:
        os.system("explorer")
        speak("Opening File Explorer.")
    elif "control panel" in command:
        os.system("control")
        speak("Opening Control Panel.")
    elif "task manager" in command:
        os.system("taskmgr")
        speak("Opening Task Manager.")
    else:
        speak("Application not recognized.")

def control_system(command):
    """Perform system-level operations"""
    if "shutdown" in command:
        speak("Shutting down your system.")
        os.system("shutdown /s /t 5")
    elif "restart" in command:
        speak("Restarting your system.")
        os.system("shutdown /r /t 5")
    elif "lock screen" in command:
        speak("Locking the screen.")
        os.system("rundll32.exe user32.dll,LockWorkStation")
    elif "log off" in command:
        speak("Logging off your system.")
        os.system("shutdown /l")
    elif "sleep" in command:
        speak("Putting the system to sleep.")
        os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
    elif "hibernate" in command:
        speak("Hibernating the system.")
        os.system("shutdown /h")
    elif "increase volume" in command:
        for _ in range(5):
            pyautogui.press("volumeup")
        speak("Volume increased.")
    elif "decrease volume" in command:
        for _ in range(5):
            pyautogui.press("volumedown")
        speak("Volume decreased.")
    elif "mute" in command:
        pyautogui.press("volumemute")
        speak("Muted the volume.")
    elif "brightness up" in command:
        pyautogui.hotkey('fn', 'brightnessup')
        speak("Increased brightness.")
    elif "brightness down" in command:
        pyautogui.hotkey('fn', 'brightnessdown')
        speak("Decreased brightness.")
    else:
        speak("System command not recognized.")

def search_web(command):
    """Perform a web search"""
    query = command.replace("search for", "").strip()
    speak(f"Searching for {query}.")
    webbrowser.open(f"https://www.google.com/search?q={query}")

def capture_photo():
    """Take a picture using the laptop's camera"""
    speak("Capturing photo.")
    camera = cv2.VideoCapture(0)
    ret, frame = camera.read()
    if ret:
        cv2.imwrite("captured_photo.jpg", frame)
        speak("Photo captured and saved.")
    camera.release()
    cv2.destroyAllWindows()

def get_chatgpt_response(prompt):
    """Fetch a response from OpenAI's ChatGPT"""
    response = openai.Chat.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    return response['choices'][0]['message']['content']

def play_song_on_youtube(command):
    """Search for a song on YouTube and play it"""
    song_name = command.replace("play", "").strip()
    speak(f"Playing {song_name} on YouTube.")
    pywhatkit.playonyt(song_name)

def schedule_task(task, time):
    """Schedule a task using Google Calendar"""
    event = {
        'summary': task,
        'start': {
            'dateTime': time.isoformat(),
            'timeZone': 'UTC',
        },
        'end': {
            'dateTime': (time + timedelta(hours=1)).isoformat(),
            'timeZone': 'UTC',
        },
    }
    try:
        event = calendar_service.events().insert(calendarId='primary', body=event).execute()
        speak(f"Task '{task}' scheduled for {time}.")
    except Exception as e:
        logging.error(f"Error scheduling task: {e}")
        speak("There was an error scheduling the task.")

def real_time_translation(target_language):
    """Translate speech to text in real-time"""
    speak(f"Real-time translation is now active. Speaking in {target_language}.")
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        while True:
            try:
                audio = recognizer.listen(source)
                command = recognizer.recognize_google(audio).lower()
                if command == "stop translation":
                    speak("Stopping real-time translation.")
                    break
                translated_text = translate_text(command, target_language)
                speak(translated_text)
                pyautogui.write(translated_text)
                pyautogui.press('enter')
            except sr.UnknownValueError:
                speak("Sorry, I didn't catch that. Please repeat.")
            except sr.RequestError:
                speak("Network error.")
                break

def authenticate_user():
    """Authenticate user based on voice sample"""
    recognizer = sr.Recognizer()
    speak("Please say your authentication phrase.")
    with sr.Microphone() as source:
        audio = recognizer.listen(source)
    
    # Save the recorded audio for comparison
    with open("current_voice_sample.wav", "wb") as f:
        f.write(audio.get_wav_data())
    
    # Compare the recorded audio with the predefined user's voice sample
    USER_VOICE_SAMPLE = "path/to/user_voice_sample.wav"
    user_command = recognize_speech("current_voice_sample.wav")
    predefined_command = recognize_speech(USER_VOICE_SAMPLE)
    
    if user_command == predefined_command:
        speak("Authentication successful.")
        return True
    else:
        speak("Authentication failed. Please try again.")
        return False

def sentiment_analysis(text):
    """Perform sentiment analysis on the given text"""
    blob = TextBlob(text)
    return blob.sentiment.polarity

def fetch_news():
    """Fetch the latest news headlines"""
    url = "https://newsapi.org/v2/top-headlines?country=us&apiKey=your_newsapi_key"
    try:
        response = requests.get(url)
        response.raise_for_status()
        news_data = response.json()
        headlines = [article['title'] for article in news_data['articles'][:5]]
        return headlines
    except Exception as e:
        logging.error(f"Error fetching news: {e}")
        return []

def read_emails():
    """Read the latest unread emails"""
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        mail.select("inbox")
        status, messages = mail.search(None, '(UNSEEN)')
        email_ids = messages[0].split()
        emails = []
        for email_id in email_ids[:5]:
            status, msg_data = mail.fetch(email_id, "(RFC822)")
            msg = email.message_from_bytes(msg_data[0][1])
            emails.append(f"From: {msg['from']}\nSubject: {msg['subject']}\n")
        mail.logout()
        return emails
    except Exception as e:
        logging.error(f"Error reading emails: {e}")
        return []

def send_email(to_address, subject, message):
    """Send an email"""
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            email_message = f"Subject: {subject}\n\n{message}"
            server.sendmail(EMAIL_ADDRESS, to_address, email_message)
            speak("Email sent successfully.")
    except Exception as e:
        logging.error(f"Error sending email: {e}")
        speak("There was an error sending the email.")

def process_audio():
    gui.start_animation()
    while True:
        audio_data = capture_audio()
        
        recognized_text = recognize_speech(audio_data)
        
        if recognized_text:
            detected_language = detect_language(recognized_text)
            print(f"Detected language: {detected_language}")
            
            if detected_language != 'en':
                translated_text = translate_text(recognized_text, 'en')
                print(f"Translated to English: {translated_text}")
                speak(translated_text)
                
                pyautogui.write(translated_text)
                pyautogui.press('enter')
            else:
                target_language = 'es'  
                translated_text = translate_text(recognized_text, target_language)
                print(f"Translated to {target_language}: {translated_text}")
                speak(translated_text)
            
            if "exit" in recognized_text or "stop" in recognized_text:
                speak("Goodbye!")
                gui.stop_animation()
                break  
            elif "translate to" in recognized_text:
                target_language = recognized_text.split("translate to")[1].strip()
                real_time_translation(target_language)
            elif "open" in recognized_text:
                open_application(recognized_text)
            elif any(keyword in recognized_text for keyword in ["shutdown", "restart", "volume", "lock screen", "log off", "sleep", "hibernate", "brightness"]):
                control_system(recognized_text)
            elif "search for" in recognized_text:
                search_web(recognized_text)
            elif "take a photo" in recognized_text:
                capture_photo()
            elif "play" in recognized_text:
                play_song_on_youtube(recognized_text)
            elif "weather in" in recognized_text:
                city = recognized_text.split("weather in")[1].strip()
                weather_info = get_weather(city)
                speak(weather_info)
            elif "schedule task" in recognized_text:
                match = re.search(r'schedule task (.*?) at (.*?)$', recognized_text)
                if match:
                    task = match.group(1)
                    time_str = match.group(2)
                    time = datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S')
                    schedule_task(task, time)
            elif "read emails" in recognized_text:
                emails = read_emails()
                for email in emails:
                    speak(email)
            elif "send email" in recognized_text:
                speak("To whom do you want to send the email?")
                to_address = recognize_speech(capture_audio())
                speak("What is the subject of the email?")
                subject = recognize_speech(capture_audio())
                speak("What is the message?")
                message = recognize_speech(capture_audio())
                send_email(to_address, subject, message)
            elif "news" in recognized_text:
                headlines = fetch_news()
                for headline in headlines:
                    speak(headline)
            else:
                response = get_chatgpt_response(recognized_text)
                speak(response)
    gui.stop_animation()

def main():
    if detect_whatsapp_call():
        logging.info("WhatsApp call detected. Starting translation...")
        translate_call()
    else:
        audio_thread = threading.Thread(target=process_audio)
        audio_thread.start()
        gui.mainloop()

if __name__ == "__main__":
    main()