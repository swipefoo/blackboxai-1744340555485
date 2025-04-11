from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List
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

class WhatsAppMessage(BaseModel):
    object: str
    entry: List[Dict[str, Any]]

class WhatsAppResponse(BaseModel):
    messaging_product: str = "whatsapp"
    to: str
    type: str = "text"
    text: Dict[str, str]

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

        if not all([mode, token, challenge]):
            raise HTTPException(status_code=400, detail="Missing required parameters")

        if mode == "subscribe" and token == VERIFY_TOKEN:
            return challenge  # Return challenge as-is, no conversion needed
        else:
            raise HTTPException(status_code=403, detail="Invalid verify token")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/webhook")
async def handle_message(request: Request):
    """
    Handle incoming messages from WhatsApp
    """
    try:
        # Get raw request body
        body = await request.json()
        print(f"Received raw webhook data: {body}")

        # Check if this is a status update
        if body.get("object") == "whatsapp_business_account":
            messages = body.get("entry", [])[0].get("changes", [])[0].get("value", {}).get("messages", [])
            
            if messages:
                message = messages[0]  # Get the first message
                if message.get("type") == "text":
                    # Get message details
                    text = message["text"]["body"]
                    from_number = message["from"]
                    print(f"Message from {from_number}: {text}")

                    # Transliterate the message to Latin
                    latin_text = transliterate_to_latin(text)
                    print(f"Transliterated text: {latin_text}")

                    # Store the original message in Redis with TTL of 1 hour
                    message_key = f"message:{latin_text}"
                    redis_client.setex(message_key, 3600, text)
                    
                    # Mock TinyLlama response for testing
                    try:
                        response = requests.post("http://localhost:8000/tinylama", json={"text": latin_text})
                        generated_text = response.json().get("generated_text", "")
                    except:
                        # Fallback response if TinyLlama service is not available
                        generated_text = f"I received your message: {latin_text}"
                    print(f"Generated response: {generated_text}")
                    
                    # Transliterate the response back to Arabic
                    arabic_response = transliterate_to_arabic(generated_text)
                    print(f"Arabic response: {arabic_response}")
                    
                    # Create WhatsApp response
                    whatsapp_response = WhatsAppResponse(
                        to=from_number,
                        text={"body": arabic_response}
                    )
                    
                    return whatsapp_response.dict()

        # If no message was processed, return success
        return {"status": "success", "message": "No text message to process"}
    except redis.RedisError as e:
        print(f"Redis error: {str(e)}")
        return WhatsAppResponse(
            to=from_number,
            text={"body": "Sorry, there was an error processing your message. Please try again later."}
        ).dict()
    except requests.RequestException as e:
        print(f"Request error: {str(e)}")
        return WhatsAppResponse(
            to=from_number,
            text={"body": "Sorry, the service is temporarily unavailable. Please try again later."}
        ).dict()
    except Exception as e:
        print(f"Internal error: {str(e)}")
        return WhatsAppResponse(
            to=from_number if 'from_number' in locals() else "unknown",
            text={"body": "An unexpected error occurred. Please try again later."}
        ).dict()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
