from ollama import chat


class LLM:

    MODEL = "qwen3:8b"

    @staticmethod
    def ask(prompt: str):

        response = chat(
            model=LLM.MODEL,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        return response["message"]["content"]