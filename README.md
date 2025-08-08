# Insurance Claim System - HackRX 6.0

This project consists of a **FastAPI backend** for an AI-powered insurance document analysis system built for the Bajaj-HackRX 6.0 competition.

## 🚀 Setup Instructions

### 📥 Clone the Repository

```bash
git clone https://github.com/AnshAggr1303/Bajaj-HackRX-6.0
cd Bajaj-HackRX-6.0
```

### 🛠 Backend Setup (Python 3.11 required)

1. **Navigate to the backend directory:**
   ```bash
   cd backend
   ```

2. **Create and activate a Python 3.12 virtual environment:**
   ```bash
   python3.12 -m venv hackrx_env
   source hackrx_env/bin/activate  # On Windows: hackrx_env\Scripts\activate
   ```

3. **Install the dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Create a `.env` file in the `backend/` folder with the following content:**
   ```env
   GEMINI_API_KEY=your_api_key
   API_TOKEN=your_token
   LOG_LEVEL=INFO
   ```

5. **Run the backend server:**
   ```bash
   python -m app.main
   ```
   
   Or alternatively:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

## 🧪 Testing the API

### Health Check
```bash
curl http://localhost:8000/health
```

### Main HackRX Endpoint
```bash
curl -X POST "http://localhost:8000/hackrx/run" \
  -H "Authorization: Bearer de76f5235c90aed44bb592ab29e6649d9bb023277d2a45b20640fdcf40031d91" \
  -H "Content-Type: application/json" \
  -d '{
    "documents": "https://example.com/test.pdf",
    "questions": ["What is this document about?", "What are the key terms?"]
  }'
```

### Testing Authentication
Test without authentication (should fail):
```bash
curl -X POST "http://localhost:8000/hackrx/run" \
  -H "Content-Type: application/json" \
  -d '{
    "documents": "https://example.com/test.pdf",
    "questions": ["What is this document about?"]
  }'
```

## 🔧 Configuration

### Environment Variables
- `GEMINI_API_KEY`: Your Google Gemini API key for document analysis
- `API_TOKEN`: Bearer token for API authentication (default provided)
- `LOG_LEVEL`: Logging level (INFO, DEBUG, WARNING, ERROR)

### API Authentication
All requests to `/hackrx/run` require a Bearer token in the Authorization header:
```
Authorization: Bearer de76f5235c90aed44bb592ab29e6649d9bb023277d2a45b20640fdcf40031d91
```

## 📚 API Endpoints

| Endpoint | Method | Auth Required | Description |
|----------|--------|---------------|-------------|
| `/` | GET | No | Root endpoint |
| `/health` | GET | No | Health check |
| `/hackrx/run` | POST | Yes | Main document analysis endpoint |

## 🏗️ System Architecture

- **Document Processing**: Supports PDF, DOCX, and email files
- **Text Extraction**: Advanced PDF table extraction with pdfplumber
- **Embeddings**: sentence-transformers/all-MiniLM-L6-v2 model
- **Vector Storage**: In-memory vector store for fast processing
- **LLM Integration**: Google Gemini 2.0 Flash for question answering
- **Authentication**: Bearer token-based security

## 📝 Request/Response Format

### Request Body
```json
{
  "documents": "https://example.com/document.pdf",
  "questions": [
    "What is the coverage amount?",
    "What are the exclusions?",
    "When does the policy expire?"
  ]
}
```

### Response Body
```json
{
  "answers": [
    "The coverage amount is $100,000 as specified in section 2.1.",
    "Exclusions include natural disasters and pre-existing conditions.",
    "The policy expires on December 31, 2024."
  ]
}
```

## 📋 Requirements

- Python 3.11+
- Internet connection (for document download and AI processing)
- Valid Gemini API key

## 🚀 Deployment Ready

This system is designed for easy deployment with:
- In-memory vector storage (no external database required)
- Lightweight embedding model
- Async processing for better performance
- Comprehensive error handling and logging

## 📞 Support

For issues or questions related to this HackRX 6.0 submission, please check the repository issues or contact the development team.
