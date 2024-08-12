from dotenv import load_dotenv
import os

load_dotenv()

import ollama


OLLAMA_MODEL = os.getenv("OLLAMA_MODEL")


class LLM_engine:
    def __init__(self):
        self.model_name = OLLAMA_MODEL

    def forward(self, system_message, user_message, stream=False):
        response = ollama.chat(
            model=self.model_name,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message},
            ],
            options={
                "num_predict": 1024,
                "temperature": 0.3,
                "top_p": 0.9,
                "top_k": 40,
                "num_ctx": 8192,
            },
            stream=stream,
        )

        if stream:
            return response

        return response["message"]["content"]
