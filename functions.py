import datetime
import pyttsx3
import webbrowser
import ollama
import os 
import requests
import speech_recognition as sr

def speak(text):
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[1].id) #changing index changes voices but ony 0 and 1 are working here
    engine.say(text)
    engine.runAndWait()

def take_command():
    r = sr.Recognizer()
    r.pause_threshold = 1.0
    with sr.Microphone() as src:
        print("Say something")
        audio = r.listen(src)
    try:
        print("Recognizing.....")
        rec = r.recognize_google(audio)
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
        return None
    except sr.RequestError as e:
        print(
            "Could not request results from Google Speech Recognition service; {0}".format(
                e
            )
        )
        return None
    return rec.lower()


def auto_greeting(name="user"):
    hour = int(datetime.datetime.now().hour)
    

    if 5 <= hour < 12:
        greet = f"Goodmorning, {name} !"
    elif 12 <= 18:
        greet = f"Good afternoon, {name}!"
    elif 18 <= 22:
        greet = f"Good Evening, {name}!"
    else:
        greet = f"Hello {name} how can I help you at this hour?"

    print(greet)
    speak(greet)
    speak("I'm your AI assistant. What can I do for you today")

def ask_ollama(question):
    try:
        response = ollama.chat(model="deepseek-r1:8b", messages=[
        {"role": "system",
          
        "content": (
            "You are a concious smart voice assistant."
            "Always respond in short one or two short sentences"
            "Never include Asterisks (*) or markdown, or formatting when you respond. "
            "If user asks a complex question answer shortly first then, ask if they need a longer answer."
            "If someone asks you who created you answer should be: Aryy is my creator he is a sopohomore at Luther College Decorah Iowa " ),
        },
        {"role": "user", "content": question},
    ])

        options={
                "temperature": 0.4,  # less creativity = more focused
                "num_predict": 80,   # limits length of response
            },


        return response.get('message', {}).get('content', "Sorry, I didn’t get that.")

    except Exception as e:
        print(f"Ollama error: {e}")
        return "I ran into an issue connecting to the model."

def opening_webs(query):

    if "open youtube" in query:
        webbrowser.open("www.youtube.com")

    if "open facebook" in query:
        webbrowser.open("www.facebook.com")

    if "open twitch" in query:
        webbrowser.open("www.twitch.com")


def opening_apps(query):
    if "open spotify" in query: 
        os.startfile(r"C:\Users\aryan\AppData\Local\Microsoft\WindowsApps\Spotify.exe")
    if "open vscode" in query:   
        os.startfile(r"C:\Users\aryan\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Visual Studio Code")
    if "open chrome" in query:
        os.startfile(r"C:\Program Files\Google\Chrome\Application")


def get_weather(location=None):
    if location is None:
        location = input("Which city would you like to check ").strip().lower()
    else:
        location = location.strip().lower()

    api_key = "c8836ab3e8ba388b48992becda34199a"
    base_url = f"http://api.weatherstack.com/current?access_key={api_key}&query={location}"

    params = {
        'access_key': api_key,
        'query': location,
        'units': 'm'
    }

    try:
        response = requests.get(base_url, params=params)
        weather_data = response.json()
        if 'error' in weather_data:
            return "Sorry, I couldn't find that city."
        else:
            current_data = weather_data['current']
            location_data = weather_data['location']
            city_name = location_data['name']
            region = location_data['region']
            temp = current_data['temperature']
            humidity = current_data['humidity']
            wind_speed = current_data['wind_speed']
            condition = current_data['weather_descriptions'][0]
        
            output = (
                f"Currently in {city_name}, {region}, it is {condition}. "
                f"The temperature is {temp} degrees with humidity at {humidity} percent. "
                f"Wind speeds are around {wind_speed} kilometers per hour."
            )
            return output
    except Exception as e:
        return f"An error occurred: {e}"    








