# HR Chatbot Application

A sophisticated HR chatbot application built with FastAPI and OpenAI, designed to collect and manage job application information through an interactive conversation interface.

## 🌟 Features

- Interactive chatbot interface powered by OpenAI GPT-3.5
- Clean architecture with Repository-Service pattern
- Automatic question generation based on context
- CSV storage for application responses
- Session-based conversation tracking
- Real-time response validation
- RESTful API endpoints
- CORS support
- Environment-based configuration

## 🏗️ Architecture

The application follows a clean architecture pattern with three main layers:

### Repository Layer
- Handles data persistence
- Manages CSV file operations
- Implements data access patterns

### Service Layer
- Contains business logic
- Manages OpenAI integration
- Handles conversation flow
- Processes user responses

### API Layer
- Exposes REST endpoints
- Handles request/response formatting
- Manages error handling
- Implements input validation

## 📁 Project Structure

```
hr-chatbot/
├── app/
│   ├── main.py
│   ├── services/
│   │   ├── chatbot_service.py
│   │   └── openai_service.py
│   ├── repositories/
│   │   └── response_repository.py
│   └── models/
│       └── schemas.py
├── .env
├── requirements.txt
└── README.md
```

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- OpenAI API key
- Git (for version control)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/hr-chatbot.git
cd hr-chatbot
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory:
```env
OPENAI_API_KEY=your_openai_api_key_here
```

### Running the Application

1. Start the FastAPI server:
```bash
uvicorn app.main:app --reload
```

2. Access the API documentation at `http://localhost:8000/docs`

## 🔌 API Endpoints

### POST /api/chat
Process user responses and generate next questions.

Request body:
```json
{
    "session_id": "string",
    "text": "string",
    "current_question": "string"
}
```

Response:
```json
{
    "text": "string",
    "conversation_history": [
        {
            "type": "string",
            "text": "string"
        }
    ]
}
```

### GET /api/responses
Retrieve all stored responses.

Response:
```json
[
    {
        "session_id": "string",
        "timestamp": "string",
        "question": "string",
        "response": "string",
        ...
    }
]
```

## 💾 Data Storage

Responses are stored in a CSV file with the following structure:

- session_id: Unique identifier for each conversation
- timestamp: When the response was recorded
- question: Current question being answered
- response: User's response
- Additional fields for specific form data (name, email, etc.)

## 🔐 Security Considerations

1. Environment Variables
   - Keep the OpenAI API key secure in the `.env` file
   - Never commit the `.env` file to version control

2. Input Validation
   - All user inputs are validated before processing
   - Sensitive data is handled with care

3. Error Handling
   - Comprehensive error handling for API requests
   - Secure error messages that don't expose sensitive information

## 🔄 Development Workflow

1. Create a new branch for each feature/fix
2. Write tests for new functionality
3. Submit pull requests for review
4. Merge after approval

## 🧪 Testing

Run tests using pytest:
```bash
pytest
```

## 📝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Submit a pull request

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.

## ✨ Future Enhancements

- [ ] Add authentication and authorization
- [ ] Implement database storage option
- [ ] Add more sophisticated response validation
- [ ] Implement rate limiting
- [ ] Add export functionality for responses
- [ ] Implement conversation analytics
- [ ] Add user management system
- [ ] Implement webhook notifications

## 🤝 Support

For support, please open an issue in the GitHub repository or contact the maintainers directly.

## 🙏 Acknowledgments

- OpenAI for their powerful GPT models
- FastAPI for the excellent web framework
- All contributors who help improve this project

---

Made with ❤️ by [MichaelSpeed]
