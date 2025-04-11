# Quick Start Guide - Prof Noor WhatsApp Bot

## Step 1: Install Required Software
1. Install Docker: https://docs.docker.com/get-docker/
2. Install ngrok: https://ngrok.com/download

## Step 2: Set Up WhatsApp Cloud API
1. Go to https://developers.facebook.com/
2. Create a Meta Developer account if you haven't already
3. Create a WhatsApp Business App
4. Get your WhatsApp API Key

## Step 3: Configure the Bot
1. Open the `.env` file and add your WhatsApp API key:
```
WHATSAPP_API_KEY=your_api_key_here
REDIS_URL=redis://redis:6379
```

## Step 4: Run the Bot
1. Open a terminal in the whatsapp_bot directory
2. Start the containers:
```bash
docker-compose up --build
```
You should see logs indicating both the FastAPI app and Redis are running.

## Step 5: Expose the Bot to Internet
1. Open a new terminal
2. Run ngrok:
```bash
ngrok http 8000
```
3. Copy the HTTPS URL provided by ngrok (looks like: https://xxxx-xx-xx-xx-xx.ngrok.io)

## Step 6: Configure Webhook
1. Go to your WhatsApp Cloud API settings
2. Set up webhook URL: [your ngrok URL]/webhook
   Example: https://xxxx-xx-xx-xx-xx.ngrok.io/webhook
3. Configure webhook to receive messages

## Step 7: Test the Bot
1. Send a message in Darija to your WhatsApp bot number
2. The bot should respond with a processed message

## Useful Commands
- Start in background: `docker-compose up -d --build`
- Stop the bot: `docker-compose down`
- View logs: `docker-compose logs -f`
- Restart: `docker-compose restart`

## Troubleshooting
- If port 8000 is in use: `docker-compose down && docker-compose up --build`
- Check logs: `docker-compose logs`
- Redis issues: `docker-compose restart redis`
