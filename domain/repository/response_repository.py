import os
from typing import List, Dict

import pandas as pd


class ResponseRepository:
    def __init__(self, csv_file: str):
        self.csv_file = csv_file
        self._initialize_csv()

    def _initialize_csv(self):
        if not os.path.exists(self.csv_file):
            columns = [
                'session_id', 'timestamp', 'question', 'response',
                'name', 'mobile', 'email', 'post', 'marks',
                'income', 'category', 'religion', 'hobbies',
                'future_goals', 'additional_info', 'scenario_response'
            ]
            df = pd.DataFrame(columns=columns)
            df.to_csv(self.csv_file, index=False)

    def store_response(self, user_response: 'UserResponse'):
        df = pd.read_csv(self.csv_file)

        # Create new response row
        new_row = {
            'session_id': user_response.session_id,
            'timestamp': pd.Timestamp.now(),
            'question': user_response.current_question,
            'response': user_response.text
        }

        # Update specific field based on current question
        field_mapping = {
            'name': 'name',
            'mobile': 'mobile',
            'email': 'email',
            # ... add other mappings
        }

        if user_response.current_question in field_mapping:
            new_row[field_mapping[user_response.current_question]] = user_response.text

        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        df.to_csv(self.csv_file, index=False)

    def get_conversation_history(self, session_id: str) -> List[Dict[str, str]]:
        df = pd.read_csv(self.csv_file)
        session_data = df[df['session_id'] == session_id].sort_values('timestamp')

        history = []
        for _, row in session_data.iterrows():
            if pd.notna(row['question']):
                history.append({
                    "type": "bot",
                    "text": row['question']
                })
            if pd.notna(row['response']):
                history.append({
                    "type": "user",
                    "text": row['response']
                })
        return history

    def get_all_responses(self) -> List[Dict]:
        df = pd.read_csv(self.csv_file)
        return df.to_dict('records')
