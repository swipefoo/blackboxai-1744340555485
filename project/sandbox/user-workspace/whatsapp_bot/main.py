from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
import redis
import os
from dotenv import load_dotenv
from transliteration import transliterate_to_latin, transliterate_to_arabic
import requests

# Load environment variables
load_dotenv()

# Get webhook verify token from environment variable
VERIFY_TOKEN = os.getenv('VERIFY_TOKEN', 'default_verify_token')

app = FastAPI()

# Initialize Redis using environment variable
redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')
redis_client = redis.from_url(redis_url)

class Message(BaseModel):
    text: str

@app.get("/")
@app.get("/webhook")
async def verify_webhook(request: Request):
    """
    Handle webhook verification from Meta/WhatsApp
    """
    try:
        mode = request.query_params.get("hub.mode")
        token = request.query_params.get("hub.verify_token")
        challenge = request.query_params.get("hub.challenge")

        if mode == "subscribe" and token == VERIFY_TOKEN:
            if challenge:
                return int(challenge)
            return "WEBHOOK_VERIFIED"
        else:
            raise HTTPException(status_code=403, detail="Invalid verify token")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/webhook")
async def handle_message(message: Message):
    try:
        # Transliterate the incoming message to Latin
        latin_text = transliterate_to_latin(message.text)
        
        # Store the original message in Redis with TTL of 1 hour
        message_key = f"message:{latin_text}"
        redis_client.setex(message_key, 3600, message.text)
        
        # Call TinyLlama model for processing (placeholder URL)
        response = requests.post("http://localhost:8000/tinylama", json={"text": latin_text})
        generated_text = response.json().get("generated_text", "")
        
        # Transliterate the response back to Arabic
        arabic_response = transliterate_to_arabic(generated_text)
        
        return {"response": arabic_response, "status": "success"}
    except redis.RedisError as e:
        return {"response": "Error with message storage", "status": "error", "detail": str(e)}
    except requests.RequestException as e:
        return {"response": "Error processing message", "status": "error", "detail": str(e)}
    except Exception as e:
        return {"response": "Internal server error", "status": "error", "detail": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
