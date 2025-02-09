from typing import List

import openai


class OpenAIService:
    def __init__(self, api_key: str):
        openai.api_key = api_key
        self.conversation_prompt = """
        You are an HR assistant chatbot for Neputune Smart Automation. You need to collect the following information from job applicants:
        1. Name
        2. Mobile number
        3. Email ID
        4. Post applied for
        5. 10th Board marks and percentage
        6. Parents annual income
        7. Category
        8. Religion
        9. Major interests and hobbies
        10. Future goals (5 years)
        11. Additional information
        12. Response to scenario: handling after-hours work request with prior commitments

        Generate natural, conversational questions to collect this information.
        Be professional but friendly in tone.
        Validate responses appropriately.
        """

    async def generate_next_question(self, conversation_history: List[dict]) -> str:
        try:
            messages = [{"role": "system", "content": self.conversation_prompt}]

            # Add conversation history
            for message in conversation_history:
                messages.append({
                    "role": "user" if message["type"] == "user" else "assistant",
                    "content": message["text"]
                })

            response = await openai.ChatCompletion.acreate(
                model="gpt-4o",
                messages=messages,
                max_tokens=150,
                temperature=0.7
            )

            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"Error generating question: {str(e)}")
