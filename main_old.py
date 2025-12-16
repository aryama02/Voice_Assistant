import random
from functions import (
    auto_greeting, speak, ask_ollama, take_command, 
    opening_webs, opening_apps, get_weather, get_user_name
)

def main():
    print(" Voice Assistant Starting...")
    user_name = get_user_name()
    auto_greeting(user_name)
    
    while True:
        rec = take_command()
        
        if rec is None:
            continue
        
        print(f"You said: {rec}")
        

        if any(word in rec for word in ["exit", "quit", "bye", "goodbye", "stop", "see you later", "bye bye", "see you", "I gotta go", "I have to go now"]):
            speak(random.choice(["Goodbye!", "See you later!", "Take care!"]))
            break
        
        # Open commands (apps/websites)
        open_triggers = ["open", "launch", "start", "run"]
        if any(trigger in rec for trigger in open_triggers):
            # Extract app/site name
            app_or_site = rec
            for trigger in open_triggers:
                app_or_site = app_or_site.replace(trigger, "")
            app_or_site = app_or_site.replace("please", "").replace("can you", "").replace("could you", "").strip()
            
            # Try website first, then app
            if opening_webs(app_or_site):
                speak(random.choice([f"Opening {app_or_site}", "On it", "Sure"]))
            elif opening_apps(app_or_site):
                speak(f"Opening {app_or_site}")
            else:
                speak(f"I couldn't find {app_or_site}")
            continue
        
        # Weather command
        if "weather" in rec:
            speak("Let me check that for you")
            
            if " in " in rec:
                city = rec.split(" in ", 1)[1].strip()
                weather_result = get_weather(city)
            else:
                weather_result = get_weather()
            
            speak(weather_result)
            continue
        
        # Everything else goes to Ollama
        response = ask_ollama(rec)
        print(f"Assistant: {response}")
        speak(response)

if __name__ == "__main__":
    main()