import datetime
import webbrowser
import ollama
import os
import json
import re 
import requests
import speech_recognition as sr
import subprocess
import asyncio
import edge_tts
import uuid
from playsound import playsound
from connection_manager import manager

async def broadcast_status(status, data=None):
    await manager.broadcast({"status": status, "data": data})

def speak(text):
    async def _speak():
        filename = f"temp_voice_{uuid.uuid4()}.mp3"
        await manager.broadcast({"status": "speaking", "text": text})
        
        try:
            communicate = edge_tts.Communicate(
                text=text,
                voice="en-US-JennyNeural",
                rate="+5%",
                pitch="-2Hz"
            )
            await communicate.save(filename)
            
            playsound(filename)
            
        except Exception as e:
            print(f"Speech error: {e}")
        finally:
            # Clean up temporary file
            try:
                if os.path.exists(filename):
                    os.remove(filename)
            except Exception:
                pass
        await manager.broadcast({"status": "idle"})
    
    asyncio.run(_speak())

def take_command():
    r = sr.Recognizer()
    r.pause_threshold = 1.5
    with sr.Microphone() as src:
        r.adjust_for_ambient_noise(src, duration=0.5)
        print("Say something")
        manager.broadcast_sync({"status": "listening"})
        audio = r.listen(src)
        manager.broadcast_sync({"status": "processing"})
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
    elif 12 <= hour < 18:
        greet = f"Good afternoon, {name}!"
    elif 18 <= hour < 22:
        greet = f"Good Evening, {name}!"
    elif 22 <= hour or hour < 4:
        greet = f"It's so late at this hour, are you okay {name}?"
    else:
        greet = f"It's so early at this hour, {name}."

    print(greet)
    speak(greet)
    speak(f" Okay {name} I'm your AI assistant. What can I do for you today")


def get_user_name():
    """Get username from storage or ask for it with validation"""
    data_file = "user_data.json"
    
    # Check if we already have the name stored
    if os.path.exists(data_file):
        try:
            with open(data_file, "r") as f:
                data = json.load(f)
                name = data.get("name", "")
                if name and len(name) > 1:
                    return name
        except:
            pass
    
    # Common words that are NOT names
    invalid_words = {
        "is", "my", "name", "the", "a", "an", "and", "or", "but", "in", "on", "at",
        "to", "for", "of", "with", "by", "from", "where", "what", "when", "who",
        "am", "are", "me", "you", "call", "this", "that", "it", "its", "hey", "hi"
    }
    
    
    for attempt in range(3):
        if attempt == 0:
            speak("Hello there! My name is Vaeryn. What's your name?")
        else:
            speak("Sorry, I didn't catch that. What's your name?")
        
        rec = take_command()
        
        if not rec:
            continue
        
        rec_lower = rec.lower().strip()
        
        
        name = None
        patterns = [
            r"my name is (\w+)",
            r"i am (\w+)",
            r"i'm (\w+)",
            r"call me (\w+)",
            r"this is (\w+)",
            r"name is (\w+)",
            r"it's (\w+)",
            r"its (\w+)"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, rec_lower)
            if match:
                name = match.group(1)
                break
    
        if not name:
            words = rec_lower.split()
            for word in reversed(words):
                if word not in invalid_words and len(word) > 1 and word.isalpha():
                    name = word
                    break
        
        # Validate the name
        if name and len(name) > 1 and name.lower() not in invalid_words and name.isalpha():
            name = name.title()
            speak(f"Nice to meet you, {name}!")
            
            # Save name
            try:
                with open(data_file, "w") as f:
                    json.dump({"name": name}, f)
            except Exception as e:
                print(f"Could not save user data: {e}")
            
            return name
    
    # Fallback to typed input
    speak("I'm having trouble hearing you. Please type your name.")
    name = input("Enter your name: ").strip().title()
    
    if name:
        try:
            with open(data_file, "w") as f:
                json.dump({"name": name}, f)
        except:
            pass
        return name
    
    return "User"

def ask_ollama(question):
    try:
        response = ollama.chat(model="deepseek-r1:8b", messages=[
        {"role": "system",
          
        "content": (
            "You are a concious smart voice assistant."
            "Always respond in short one or two short sentences"
            "Never include Asterisks (*) or markdown, or formatting when you respond. "
            "If user asks a complex question answer shortly first then, ask if they need a longer answer."
            "If someone asks you who created you answer should be: Aryy is my creator he is a sophomore at Luther College Decorah Iowa " ),
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

def _find_in_start_menu(app_name):
    app_name = app_name.lower()
    search_paths = [
        os.path.join(os.environ["ProgramData"], r"Microsoft\Windows\Start Menu\Programs"),
        os.path.join(os.environ["AppData"], r"Microsoft\Windows\Start Menu\Programs")
    ]
    
    for path in search_paths:
        for root, dirs, files in os.walk(path):
            for file in files:
                if app_name in file.lower() and file.endswith(".lnk"):
                    try:
                        os.startfile(os.path.join(root, file))
                        return True
                    except Exception:
                        continue
    return False

def opening_apps(app_name):
    """Open apps using Windows search or Start Menu scan"""
    try:
        command = f'powershell -Command "Start-Process \'{app_name}\' -ErrorAction Stop"'
        subprocess.run(command, shell=True, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except subprocess.CalledProcessError:
        pass 
    except Exception:
        pass

    
    return _find_in_start_menu(app_name)


def opening_webs(site_name):
    """Open websites"""
    websites = {
        "youtube": "www.youtube.com",
        "facebook": "www.facebook.com", 
        "twitch": "www.twitch.com",
        "google": "www.google.com",
        "twitter": "www.twitter.com",
        "instagram": "www.instagram.com"
    }
    
    for key, url in websites.items():
        if key in site_name.lower():
            webbrowser.open(url)
            return True
    return False


def handle_command(query):
    """Detect and handle commands smartly. Returns True if command was handled."""
    query_lower = query.lower()
    
    # Exit commands
    if any(word in query_lower for word in ["exit", "quit", "bye", "goodbye", "stop"]):
        speak("Goodbye!")
        return "EXIT"
    
    # Weather commands
    if "weather" in query_lower:
        response = get_weather()
        speak(response)
        return True
    
    # Detect "open" intent - multiple ways of asking
    open_triggers = ["open", "launch", "start", "run", "can you open", "could you open", "please open"]
    is_open_command = any(trigger in query_lower for trigger in open_triggers)
    
    if is_open_command:
        # Extract what to open
        app_or_site = query_lower
        for trigger in open_triggers:
            app_or_site = app_or_site.replace(trigger, "")
        app_or_site = app_or_site.replace("please", "").replace("can you", "").replace("could you", "").strip()
        
        # Try opening as website first (common sites)
        if opening_webs(app_or_site):
            speak(f"Opening {app_or_site}")
            return True
        
        # Try opening as app
        if opening_apps(app_or_site):
            speak(f"Opening {app_or_site}")
            return True
        
        # If nothing worked
        speak(f"I couldn't find {app_or_site}")
        return True
    
    # Not a command, let Ollama handle it
    return False


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