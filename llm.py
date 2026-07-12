from ollama import chat


class LLM:

    MODEL = "qwen3:8b"

    @staticmethod
    def ask(messages):

        response = chat(
            model=LLM.MODEL,
            messages=messages
        )

        return response["message"]["content"]
    

    @staticmethod
    def stream(messages):

        stream = chat(
            model=LLM.MODEL,
            messages=messages,
            stream=True
        )

        for chunk in stream:

            token = chunk["message"]["content"]

            if token.strip():
                yield token