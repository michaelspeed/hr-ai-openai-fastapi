import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from domain.models.schema import ChatResponse, UserResponse
from domain.repository.response_repository import ResponseRepository
from services.chatbot_service import ChatbotService
from services.openai_service import OpenAIService

load_dotenv()

app = FastAPI(title="HR Chatbot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
response_repo = ResponseRepository("responses.csv")
openai_service = OpenAIService(api_key=os.getenv("OPENAI_API_KEY"))
chatbot_service = ChatbotService(openai_service, response_repo)

@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(user_response: UserResponse):
    try:
        response = await chatbot_service.process_response(user_response)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/responses")
async def get_responses():
    try:
        return response_repo.get_all_responses()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
