from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from openai import AzureOpenAI
from pydantic import BaseModel, Field
from typing import Dict, List, Optional
import openai
import json
from datetime import datetime
import os
from uuid import uuid4
import asyncio
from dataclasses import dataclass

# Initialize FastAPI app
app = FastAPI(title="HR Interview Bot API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for request/response validation
class InterviewQuestion(BaseModel):
    id: str
    question: str
    category: str
    weight: float

class CandidateResponse(BaseModel):
    session_id: str
    answer: str

class InterviewSession(BaseModel):
    session_id: str
    candidate_name: str
    current_question_index: int = 0
    conversation_history: List[Dict] = []
    completed: bool = False

class EvaluationResult(BaseModel):
    scores: Dict
    weighted_score: float
    recommendation: str
    summary: str

# In-memory session storage (replace with database in production)
interview_sessions: Dict[str, InterviewSession] = {}

class HRInterviewAPI:
    def __init__(self):
        self.questions = [
            InterviewQuestion(
                id="personal",
                question="Please introduce yourself and tell me about your educational background.",
                category="communication",
                weight=0.25
            ),
            InterviewQuestion(
                id="career",
                question="What post are you applying for and why did you choose this field?",
                category="future_vision",
                weight=0.2
            ),
            InterviewQuestion(
                id="hobbies",
                question="What are your major interests and hobbies? How do they relate to your career goals?",
                category="personality_fit",
                weight=0.25
            ),
            InterviewQuestion(
                id="future",
                question="Where do you see yourself after 5 years? What steps are you taking to achieve these goals?",
                category="future_vision",
                weight=0.2
            ),
            InterviewQuestion(
                id="conflict",
                question="If your superior stops you after 6pm when you have prior commitments, how would you handle this situation?",
                category="conflict_resolution",
                weight=0.3
            )
        ]

    async def evaluate_candidate(self, conversation_history: List[Dict]) -> Dict:
        """Evaluate the candidate based on their responses"""
        evaluation_prompt = self._generate_evaluation_prompt(conversation_history)

        try:
            client = AzureOpenAI(
                api_key=os.getenv("AZURE_OPENAI_API_KEY"),
                api_version="2024-10-21",
                azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
            )
            response = await client.chat.with_streaming_response.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": """You are an expert HR evaluator.
                         Analyze the interview responses and provide detailed scoring and feedback.
                         Be objective and thorough in your evaluation."""
                    },
                    {"role": "user", "content": evaluation_prompt}
                ]
            )

            evaluation = response.choices[0].message.content
            return self._parse_evaluation(evaluation)

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Evaluation error: {str(e)}")

    def _generate_evaluation_prompt(self, conversation_history: List[Dict]) -> str:
        return f"""
        Based on the following interview conversation, evaluate the candidate on these criteria:
        1. Communication Skills (25%): Assess clarity, articulation, and professional communication
        2. Future Vision (20%): Evaluate career goals and ambition
        3. Conflict Resolution (30%): Assess approach to handling conflicts and priorities
        4. Personality Fit (25%): Evaluate overall cultural fit and personality

        Conversation History:
        {json.dumps(conversation_history, indent=2)}

        Please provide:
        1. Scores for each criterion (0-10)
        2. Brief justification for each score
        3. Overall weighted score
        4. Final recommendation (Recommend/Consider/Do Not Recommend)

        Format your response as JSON with the following structure:
        {{
            "scores": {{
                "communication": {{"score": X, "justification": "..."}},
                "future_vision": {{"score": X, "justification": "..."}},
                "conflict_resolution": {{"score": X, "justification": "..."}},
                "personality_fit": {{"score": X, "justification": "..."}}
            }},
            "overall_score": X,
            "recommendation": "...",
            "summary": "..."
        }}
        """

    def _parse_evaluation(self, evaluation_text: str) -> Dict:
        try:
            evaluation = json.loads(evaluation_text)

            # Calculate weighted score
            weighted_score = 0
            weights = {
                "communication": 0.25,
                "future_vision": 0.20,
                "conflict_resolution": 0.30,
                "personality_fit": 0.25
            }

            for category, weight in weights.items():
                weighted_score += evaluation["scores"][category]["score"] * weight

            evaluation["weighted_score"] = round(weighted_score, 2)

            return evaluation

        except json.JSONDecodeError:
            raise HTTPException(status_code=500, detail="Error parsing evaluation response")

# Initialize the HR Interview API
hr_api = HRInterviewAPI()

# API Endpoints
@app.post("/interview/start")
async def start_interview(candidate_name: str):
    """Start a new interview session"""
    session_id = str(uuid4())
    session = InterviewSession(
        session_id=session_id,
        candidate_name=candidate_name,
        current_question_index=0,
        conversation_history=[],
        completed=False
    )
    interview_sessions[session_id] = session

    return {
        "session_id": session_id,
        "question": hr_api.questions[0].question,
        "question_number": 1,
        "total_questions": len(hr_api.questions)
    }

@app.post("/interview/answer")
async def submit_answer(response: CandidateResponse):
    """Submit an answer and get the next question"""
    session = interview_sessions.get(response.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Interview session not found")

    # Record the answer
    current_question = hr_api.questions[session.current_question_index]
    session.conversation_history.append({
        "question": current_question.question,
        "answer": response.answer,
        "category": current_question.category
    })

    # Move to next question
    session.current_question_index += 1

    # Check if interview is complete
    if session.current_question_index >= len(hr_api.questions):
        session.completed = True
        return {
            "completed": True,
            "message": "Interview completed. You can now request the evaluation."
        }

    # Return next question
    next_question = hr_api.questions[session.current_question_index]
    return {
        "completed": False,
        "question": next_question.question,
        "question_number": session.current_question_index + 1,
        "total_questions": len(hr_api.questions)
    }

@app.post("/interview/evaluate/{session_id}")
async def evaluate_interview(session_id: str):
    """Evaluate the completed interview"""
    session = interview_sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Interview session not found")

    if not session.completed:
        raise HTTPException(status_code=400, detail="Interview is not yet completed")

    evaluation = await hr_api.evaluate_candidate(session.conversation_history)

    # Save the evaluation result (implement your storage solution here)
    result = {
        "candidate_name": session.candidate_name,
        "date": datetime.now().isoformat(),
        "evaluation": evaluation,
        "conversation_history": session.conversation_history
    }

    return result

@app.get("/interview/status/{session_id}")
async def get_interview_status(session_id: str):
    """Get the current status of an interview session"""
    session = interview_sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Interview session not found")

    return {
        "candidate_name": session.candidate_name,
        "completed": session.completed,
        "current_question": session.current_question_index + 1 if not session.completed else len(hr_api.questions),
        "total_questions": len(hr_api.questions)
    }
