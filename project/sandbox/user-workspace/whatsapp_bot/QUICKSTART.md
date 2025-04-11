# Quick Start Guide - Prof Noor WhatsApp Bot

## 1. Prerequisites
- Docker and Docker Compose installed
- ngrok installed (for local development)
- WhatsApp Business API credentials

## 2. First-Time Setup

1. **Set Environment Variables**
   Create a `.env` file in the project root:
   ```env
   WHATSAPP_API_KEY=your_api_key_here
   REDIS_URL=redis://redis:6379
   ```

2. **Build and Start Services**
   ```bash
   # Build and start containers
   docker-compose up --build -d

   # Verify services are running
   docker-compose ps
   ```

3. **Expose the API**
   ```bash
   ngrok http 8000
   ```
   Copy the HTTPS URL provided by ngrok.

## 3. WhatsApp API Configuration

1. Go to [WhatsApp Cloud API Dashboard](https://developers.facebook.com/apps/)
2. Set webhook URL: `https://your-ngrok-url/webhook`
3. Configure webhook to receive messages

## 4. Testing the Bot

1. Send a message to your WhatsApp business number
2. Check logs for any issues:
   ```bash
   docker-compose logs -f web
   ```

## 5. Common Commands

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f

# Restart specific service
docker-compose restart web

# Check service status
docker-compose ps
```

## 6. Troubleshooting

### Services Won't Start
```bash
# Remove all containers and volumes
docker-compose down -v

# Rebuild and start
docker-compose up --build -d
```

### Redis Connection Issues
```bash
# Check Redis logs
docker-compose logs redis

# Restart Redis
docker-compose restart redis
```

### API Not Responding
1. Check if containers are running:
   ```bash
   docker-compose ps
   ```
2. Verify logs:
   ```bash
   docker-compose logs web
   ```
3. Ensure ports are available:
   ```bash
   # Check port usage
   sudo lsof -i :8000
   sudo lsof -i :6379
   ```

## 7. Development Tips

- Use `docker-compose logs -f` to monitor logs in real-time
- Check Redis data:
  ```bash
  docker-compose exec redis redis-cli
  ```
- Access FastAPI docs: `http://localhost:8000/docs`
