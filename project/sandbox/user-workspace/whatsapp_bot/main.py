from fastapi import FastAPI, Request, HTTPException, Response
from pydantic import BaseModel
from typing import Dict, Any, List
import redis
import os
from dotenv import load_dotenv
from transliteration import transliterate_to_latin, transliterate_to_arabic
import requests

# Load environment variables
load_dotenv()

# Get environment variables
VERIFY_TOKEN = os.getenv('VERIFY_TOKEN', 'default_verify_token')
WHATSAPP_API_KEY = os.getenv('WHATSAPP_API_KEY')

if not WHATSAPP_API_KEY:
    print("WARNING: WHATSAPP_API_KEY is not set. Responses will not be sent to WhatsApp.")

# WhatsApp API configuration
PHONE_NUMBER_ID = os.getenv('PHONE_NUMBER_ID')
WHATSAPP_API_URL = f"https://graph.facebook.com/v17.0/{PHONE_NUMBER_ID}/messages"
WHATSAPP_HEADERS = {
    "Authorization": f"Bearer {WHATSAPP_API_KEY}",
    "Content-Type": "application/json"
}

if not PHONE_NUMBER_ID:
    print("WARNING: PHONE_NUMBER_ID is not set. WhatsApp API calls will fail.")

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

@app.get("/test")
async def test_endpoint():
    """Test endpoint to verify the server is running"""
    return {"status": "ok", "message": "Server is running"}

@app.get("/check")
async def check_configuration():
    """Check if the WhatsApp configuration is complete."""
    status = {
        "api_key": "✓" if WHATSAPP_API_KEY else "✗",
        "phone_number_id": "✓" if PHONE_NUMBER_ID else "✗",
        "api_url": WHATSAPP_API_URL,
        "webhook_url": "https://your-ngrok-url/webhook"
    }
    
    if WHATSAPP_API_KEY and PHONE_NUMBER_ID:
        return {"status": "ok", "config": status}
    else:
        missing = []
        if not WHATSAPP_API_KEY:
            missing.append("WHATSAPP_API_KEY")
        if not PHONE_NUMBER_ID:
            missing.append("PHONE_NUMBER_ID")
        return {
            "status": "error",
            "message": f"Missing configuration: {', '.join(missing)}",
            "config": status
        }

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
        # Log complete request information
        print("\n=== Webhook Request ===")
        print("Method:", request.method)
        print("URL:", request.url)
        print("Headers:", dict(request.headers))
        
        # Get and log raw request body
        body = await request.json()
        print("\n=== Request Body ===")
        print(body)

        # Check if this is a WhatsApp message
        if body.get("object") == "whatsapp_business_account":
            changes = body.get("entry", [{}])[0].get("changes", [{}])[0]
            value = changes.get("value", {})
            
            print("Full webhook data structure:")
            print("- Entry:", body.get("entry"))
            print("- Changes:", changes)
            print("- Value:", value)
            
            if "messages" in value:
                message = value["messages"][0]
                print(f"Processing message:")
                print(f"- Type: {message.get('type')}")
                print(f"- From: {message.get('from')}")
                
                if message.get("type") == "text":
                    print(f"- Text content: {message['text'].get('body')}")
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
                    
                    # Prepare WhatsApp response
                    whatsapp_response = {
                        "messaging_product": "whatsapp",
                        "recipient_type": "individual",
                        "to": from_number,
                        "type": "text",
                        "text": {"body": arabic_response}
                    }

                    # Send response to WhatsApp API
                    if WHATSAPP_API_KEY:
                        try:
                            print("\n=== Sending to WhatsApp API ===")
                            print("URL:", WHATSAPP_API_URL)
                            print("Headers:", WHATSAPP_HEADERS)
                            print("Payload:", whatsapp_response)
                            
                            # Log request details
                            print("\n=== Sending to WhatsApp API ===")
                            print("URL:", WHATSAPP_API_URL)
                            print("Headers:", {k: '***' if k == 'Authorization' else v for k, v in WHATSAPP_HEADERS.items()})
                            print("Payload:", whatsapp_response)
                            
                            # Send request to WhatsApp API
                            response = requests.post(
                                WHATSAPP_API_URL,
                                headers=WHATSAPP_HEADERS,
                                json=whatsapp_response,
                                timeout=10
                            )
                            
                            # Log response details
                            print("\n=== WhatsApp API Response ===")
                            print(f"Status Code: {response.status_code}")
                            print(f"Response Headers: {dict(response.headers)}")
                            
                            try:
                                response_json = response.json()
                                print(f"Response Body: {response_json}")
                                
                                if response.status_code != 200:
                                    print(f"Error: Non-200 status code received")
                                    return {
                                        "status": "error",
                                        "message": f"WhatsApp API returned status {response.status_code}",
                                        "details": response_json
                                    }
                                    
                                return response_json
                            except Exception as e:
                                print(f"Failed to parse response: {str(e)}")
                                print(f"Raw response: {response.text}")
                                return {
                                    "status": "error",
                                    "message": "Failed to parse WhatsApp API response",
                                    "details": str(e)
                                }
                        except Exception as e:
                            print(f"Error sending to WhatsApp API: {e}")
                            return {"status": "error", "message": "Failed to send response to WhatsApp"}
                    else:
                        print("Skipping WhatsApp API call - no API key configured")
                        return whatsapp_response

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
