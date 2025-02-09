from typing import List, Dict

from pydantic import BaseModel


class UserResponse(BaseModel):
    session_id: str
    text: str
    current_question: str

class ChatResponse(BaseModel):
    text: str
    conversation_history: List[Dict[str, str]]
