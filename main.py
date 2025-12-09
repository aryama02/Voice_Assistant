import pyttsx3
import wikipedia as wiki
from functions import auto_greeting, speak, opening_webs, ask_ollama, opening_apps, get_weather, take_command
import ollama
import os 

def main():
    model= "deepseek-r1:8b"
    auto_greeting("Aryan")
    while True:
        rec = take_command().lower()
        print(rec)
        if rec is None:
            continue
        if rec:
            opening_webs(rec)
            opening_apps(rec)
        

        if "weather" in rec:
            speak("Let me check the weather for you")
        
            if "in" in rec:
                city = rec.split("in", 1)[1].strip()
                weather_result = get_weather(city)
            else:
                weather_result = get_weather()
            print("Weather:", weather_result)
            speak(weather_result)
            continue

        if "from wikipedia" in rec:
            speak("searching wikipedia. please wait...")
            rec = rec.replace("wikipedia", "")
            result = wiki.summary(rec, sentences=2)
            speak(result)
        
        response = ask_ollama(rec)
        print("Ollama says:", response)
        speak(response)

        


if __name__ == "__main__":
    main()
