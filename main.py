import random
import threading
import asyncio
import sys
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import uvicorn
from contextlib import asynccontextmanager

from functions import (
    auto_greeting, speak, ask_ollama, take_command, 
    opening_webs, opening_apps, get_weather, get_user_name
)
from connection_manager import manager

def voice_assistant_loop():
    """Runs the voice assistant logic in a separate thread."""
    print("Voice Assistant Loop Started")
    
    # Initial greeting in the thread
    try:
        user_name = get_user_name()
        auto_greeting(user_name)
    except Exception as e:
        print(f"Error in greeting: {e}")

    while True:
        try:
            rec = take_command()
            
            if rec is None:
                continue
            
            print(f"You said: {rec}")
            
            # Broadcast the recognized text
            manager.broadcast_sync({"status": "recognized", "text": rec})

            if any(word in rec for word in ["exit", "quit", "bye", "goodbye", "stop", "see you later", "bye bye", "see you", "I gotta go", "I have to go now"]):
                speak(random.choice(["Goodbye!", "See you later!", "Take care!"]))
                # Ideally, we should stop the server too, but for now just break the loop
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
            manager.broadcast_sync({"status": "processing_llm"})
            response = ask_ollama(rec)
            print(f"Assistant: {response}")
            speak(response)
            
        except Exception as e:
            print(f"Error in voice loop: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    loop = asyncio.get_running_loop()
    manager.set_loop(loop)
    
    # Start the voice assistant in a background thread
    thread = threading.Thread(target=voice_assistant_loop, daemon=True)
    thread.start()
    
    yield
    
    # Shutdown logic if needed

app = FastAPI(lifespan=lifespan)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive and handle any incoming messages if needed
            data = await websocket.receive_text()
            # We don't really expect input from frontend yet, but we could handle it
    except WebSocketDisconnect:
        manager.disconnect(websocket)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)