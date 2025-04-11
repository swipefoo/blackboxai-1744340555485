# Prof Noor - WhatsApp Bot

## Docker Setup Instructions

1. **Prerequisites**:
   Make sure you have the following installed:
   - Docker
   - Docker Compose

2. **Configure Environment Variables**:
   Update the `.env` file with your WhatsApp Cloud API key:
   ```env
   WHATSAPP_API_KEY=your_api_key_here
   REDIS_URL=redis://redis:6379
   ```

3. **Build and Run with Docker**:
   ```bash
   # Build and start the containers
   docker-compose up --build

   # To run in detached mode
   docker-compose up -d --build
   ```

4. **Stop the Application**:
   ```bash
   docker-compose down
   ```

5. **Expose Local Server with ngrok**:
   Install ngrok if you haven't already. Then run:
   ```bash
   ngrok http 8000
   ```
   This will provide you with a public URL that you can use to configure the WhatsApp Cloud API webhook.

6. **Configure WhatsApp Cloud API**:
   Use the ngrok URL to set up your webhook in the WhatsApp Cloud API settings.

## Usage
Send a message in Darija to the bot, and it will respond with the processed message.

## Note
Make sure to handle the TinyLlama model integration as per your requirements.
