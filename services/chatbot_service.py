from domain.models.schema import UserResponse, ChatResponse
from domain.repository.response_repository import ResponseRepository
from services.openai_service import OpenAIService


class ChatbotService:
    def __init__(self, openai_service: OpenAIService, response_repo: ResponseRepository):
        self.openai_service = openai_service
        self.response_repo = response_repo

    async def process_response(self, user_response: UserResponse) -> ChatResponse:
        # Get conversation history
        conversation_history = self.response_repo.get_conversation_history(user_response.session_id)

        # Add user's response to history
        if user_response.text:
            conversation_history.append({
                "type": "user",
                "text": user_response.text
            })

            # Store the response
            self.response_repo.store_response(user_response)

        # Generate next question
        next_question = await self.openai_service.generate_next_question(conversation_history)

        # Add bot's question to history
        conversation_history.append({
            "type": "bot",
            "text": next_question
        })

        return ChatResponse(
            text=next_question,
            conversation_history=conversation_history
        )
