# AI Document Generator - Backend

This is the backend service for an AI-powered document and presentation generator. It provides APIs for document creation, editing, and AI-assisted content generation.

## Features

- User Authentication and Authorization
- AI Document Generation using OpenAI GPT-4o
- AI Presentation Generator 
- Language Detection and Translation
- Voice-to-Text Conversion
- PDF, Word, and Markdown Export
- MongoDB Database Integration

## Tech Stack

- FastAPI: Modern, fast web framework for building APIs
- Motor: Asynchronous MongoDB driver
- OpenAI API: For AI content generation
- JWT: For secure authentication
- ReportLab & python-docx: For document export

## Setup Instructions

### Prerequisites

- Python 3.11 or newer
- MongoDB
- OpenAI API key

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/ai-document-generator-backend.git
   cd ai-document-generator-backend
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Create a `.env` file with the following variables:
   ```
   PORT=8000
   HOST=0.0.0.0
   MONGODB_URL=mongodb://localhost:27017
   DATABASE_NAME=ai_document_generator
   SECRET_KEY=your_secret_key_here
   ACCESS_TOKEN_EXPIRE_MINUTES=60
   OPENAI_API_KEY=your_openai_api_key
   ```

5. Start the server:
   ```
   uvicorn app:app --reload
   ```

### Docker Deployment

1. Build the Docker image:
   ```
   docker build -t ai-document-generator-backend .
   ```

2. Run the container:
   ```
   docker run -p 8000:8000 --env-file .env ai-document-generator-backend
   ```

## API Documentation

Once the server is running, you can access the API documentation at:
- http://localhost:8000/docs (Swagger UI)
- http://localhost:8000/redoc (ReDoc)

## API Endpoints

### Authentication
- `POST /token` - Get an access token
- `POST /users` - Register a new user

### Documents
- `POST /documents` - Create a new document
- `GET /documents` - List user's documents
- `GET /documents/{document_id}` - Get a specific document
- `PUT /documents/{document_id}` - Update a document
- `DELETE /documents/{document_id}` - Delete a document
- `POST /documents/{document_id}/export` - Export a document (PDF, DOCX, MD)
- `POST /documents/{document_id}/apply-theme` - Apply a theme to a document

### AI Processing
- `POST /ai/generate` - Generate content using AI
- `POST /ai/detect-language` - Detect text language
- `POST /ai/translate` - Translate text
- `POST /ai/speech-to-text` - Convert speech to text

## Folder Structure

```
ai-document-generator-backend/
│
├── app.py                  # Main application entry point
├── auth.py                 # Authentication module
├── database.py             # Database configuration
├── models.py               # Data models
│
├── routers/                # API route handlers
│   ├── documents.py        # Document-related endpoints
│   └── ai.py               # AI processing endpoints
│
├── exports/                # Generated document exports
├── .env                    # Environment variables
├── requirements.txt        # Project dependencies
└── Dockerfile              # Docker configuration
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request