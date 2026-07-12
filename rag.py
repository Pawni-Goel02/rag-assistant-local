from text_extract import TextExtractor
from chunking import TextChunker
from embeddings import EmbeddingGenerator
from vector_store import VectorStore
from llm import LLM
from memory import Memory

class RAG:

    def __init__(self):
        self.store = VectorStore()
        self.memory = Memory()

    def _unique_sources(self, metadatas):

        seen = set()
        unique = []

        for source in metadatas:

            key = (
                source["source"],
                source["page"]
            )

            if key not in seen:
                seen.add(key)
                unique.append(source)

        return unique
    
    def rewrite_question(self, question):
        question_lower = question.lower()

        pronouns = [
            " it ",
            " this ",
            " that ",
            " them ",
            " these ",
            " those ",
            " they ",
            " compare "
        ]

        if not any(word in f" {question_lower} " for word in pronouns):
            return question

        history = self.memory.history()

        if not history:
            return question

        messages = [

            {
                "role": "system",
                "content":
                """
    You rewrite follow-up questions into standalone questions.

    Use the conversation history to replace words like:

    - it
    - this
    - that
    - them
    - these

    with their actual meaning.

    Rules:

    - Only output the rewritten question. Nothing else.
    - Do NOT answer the question, explain it, or add any information.
    - If the question is already standalone, return it exactly as written.
    - Keep it as a single short question, not a sentence with reasoning.

    Examples:

    History: user asked "what is positive skewness", assistant explained it.
    Follow-up: "what is negative skewness?"
    Rewritten: what is negative skewness?

    History: user asked about positive skewness, then negative skewness.
    Follow-up: "compare them"
    Rewritten: Compare positive skewness and negative skewness

    History: user asked about positive skewness, then negative skewness.
    Follow-up: "compare these two"
    Rewritten: Compare positive skewness and negative skewness
                """
            }

        ]

        messages.extend(history)

        messages.append(
            {
                "role": "user",
                "content":
        f"""
        Conversation history above.

        Rewrite the following follow-up question into a standalone question.

        If the question is already standalone,
        return it exactly as written.

        Do NOT answer the question.

        Question:
        {question}
        """
            }
        )

        rewritten = LLM.ask(messages).strip()

        # Guard: a real rewritten question is short and single-sentence.
        # If the model ignored instructions and produced an explanation
        # instead of a rewrite, fall back to the original question rather
        # than polluting retrieval and chat history with an answer.
        looks_like_an_answer = (
            len(rewritten) > len(question) * 4
            or rewritten.count(".") > 1
            or rewritten.count("\n") > 1
        )

        if looks_like_an_answer:
            return question

        return rewritten

    def index_document(self, file_path):

        pages = TextExtractor.extract(file_path)

        chunks = TextChunker.chunk_pages(pages)

        embeddings = [
            EmbeddingGenerator.generate(chunk["text"])
            for chunk in chunks
        ]

        self.store.add_chunks(
            chunks,
            embeddings
        )

        return len(chunks)

    def ask(self, question, k=3):

        embedding = EmbeddingGenerator.generate(question)

        results = self.store.search(
            embedding,
            k
        )

        unique_sources = self._unique_sources(
            results["metadatas"][0]
        )

        context = "\n\n".join(
            results["documents"][0]
        )

        prompt = f"""
You are a helpful AI assistant.

Answer ONLY using the context below.

If the answer is not present in the context, say:

"I couldn't find that information in the uploaded documents."

Context:

{context}

Question:

{question}
"""

        answer = LLM.ask(prompt)

        return {
            "answer": answer,
            "sources": unique_sources
        }

    def stream(self, question, k=3):

        rewritten_question = self.rewrite_question(
            question
        )

        print("Original:", question)
        print("Rewritten:", rewritten_question)

        embedding = EmbeddingGenerator.generate(
            rewritten_question
        )

        results = self.store.search(
            embedding,
            k
        )

        unique_sources = self._unique_sources(
            results["metadatas"][0]
        )

        context = "\n\n".join(
            results["documents"][0]
        )

        messages = [

            {
                "role": "system",
                "content": (
                    "You are a helpful AI assistant. "
                    "Answer ONLY using the retrieved context whenever possible. "
                    "If the answer is not in the context, clearly say so."
                )
            }

        ]

        messages.extend(
            self.memory.history()
        )

        messages.append(
            {
                "role": "user",
                "content":
                    f"""
        Context:

        {context}

        Question:

        {rewritten_question}
        """
            }
        )

        answer = ""
        print(messages)

        for token in LLM.stream(messages):

            answer += token

            yield {
                "type": "token",
                "data": token
            }

        self.memory.add_user(question)

        self.memory.add_assistant(answer)

        yield {
            "type": "sources",
            "data": unique_sources
        }