# Prof Noor - WhatsApp Bot

A WhatsApp bot that handles Arabic/Darija messages with transliteration support and integration with TinyLlama model.

## Features

- Arabic/Latin transliteration support
- Redis-based message caching
- Docker containerization
- Health checks for services
- Error handling and logging
- WhatsApp Cloud API integration

## Prerequisites

- Docker and Docker Compose
- WhatsApp Business API credentials
- Python 3.9+

## Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd whatsapp_bot
   ```

2. **Configure Environment Variables**
   Create a `.env` file:
   ```env
   WHATSAPP_API_KEY=your_api_key_here
   REDIS_URL=redis://redis:6379
   ```

3. **Build and Run**
   ```bash
   docker-compose up --build
   ```

4. **Expose Local Server**
   ```bash
   ngrok http 8000
   ```

## API Endpoints

### POST /webhook
Handles incoming WhatsApp messages

**Request Body:**
```json
{
    "text": "Your message here"
}
```

**Response:**
```json
{
    "response": "Processed message",
    "status": "success"
}
```

## Architecture

- **FastAPI**: Web framework for handling requests
- **Redis**: Message caching and rate limiting
- **Docker**: Containerization and service orchestration
- **TinyLlama**: Text processing (placeholder)

## Development

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run Tests**
   ```bash
   pytest
   ```

3. **Local Development**
   ```bash
   uvicorn main:app --reload
   ```

## Transliteration Support

The bot supports bidirectional transliteration between Arabic and Latin scripts:

- Arabic → Latin: Converts Arabic text to Latin characters
- Latin → Arabic: Converts Latin text back to Arabic script

## Docker Services

- **web**: FastAPI application (port 8000)
- **redis**: Message cache (port 6379)

## Troubleshooting

1. **Redis Connection Issues**
   - Check Redis container status: `docker-compose ps`
   - Verify Redis logs: `docker-compose logs redis`

2. **API Not Responding**
   - Check web container logs: `docker-compose logs web`
   - Verify environment variables are set correctly

3. **Container Health Checks**
   - Monitor service health: `docker-compose ps`
   - Check individual service logs: `docker-compose logs [service]`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
