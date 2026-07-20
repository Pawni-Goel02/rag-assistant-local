import textwrap
from url_extract import URLExtractor
from text_extract import TextExtractor
from chunking import TextChunker
from embeddings import EmbeddingGenerator
from vector_store import VectorStore
from llm import LLM
from memory import Memory
import re


class RAG:

    NOT_FOUND_MESSAGE = (
        "I couldn't find that information in the uploaded documents."
    )

    def __init__(self):
        self.store = VectorStore()
        self.memory = Memory()

    def _retrieve(self, question, k):
        """
        Safely embed + search for a question.

        Returns (context, unique_sources, has_results).
        has_results is False if the store is empty, the query
        failed, or no chunks matched - callers should treat that
        as "nothing found" instead of calling the LLM.
        """

        try:
            embedding = EmbeddingGenerator.generate(question)

            results = self.store.search(
                embedding,
                k
            )

            documents = results.get("documents") or []
            metadatas = results.get("metadatas") or []

            documents = documents[0] if documents else []
            metadatas = metadatas[0] if metadatas else []

        except Exception as error:
            print("Retrieval error:", error)
            return "", [], False

        if not documents:
            return "", [], False

        unique_sources = self._unique_sources(metadatas)

        context = "\n\n".join(documents)
        if not context:
            return "",[],False

        return context, unique_sources, True

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
        words = re.findall(r"\b\w+\b", question_lower)

        if not any(word in f" {question_lower} " for word in pronouns):
            return question

        history = self.memory.history()

        if not history:
            return question

        system_prompt = textwrap.dedent(
            """
            You rewrite follow-up questions into standalone questions.

            Use the conversation history to replace words like:

            - it
            - this
            - that
            - them
            - these
            - those
            - they

            with their actual meaning. If the question asks to "compare"
            two or more things discussed earlier, rewrite it to name
            those things explicitly.

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
        ).strip()

        messages = [
            {
                "role": "system",
                "content": system_prompt
            }
        ]

        messages.extend(history)

        user_prompt = textwrap.dedent(
            f"""
            Conversation history above.

            Rewrite the following follow-up question into a standalone question.

            If the question is already standalone,
            return it exactly as written.

            Do NOT answer the question.

            Question:
            {question}
            """
        ).strip()

        messages.append(
            {
                "role": "user",
                "content": user_prompt
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

        if not chunks:
            return 0   # let the caller (app.py) decide how to report this

        embeddings = [
            EmbeddingGenerator.generate(chunk["text"])
            for chunk in chunks
        ]

        self.store.add_chunks(chunks, embeddings)
        return len(chunks)

    def ask(self, question, k=3):

        context, unique_sources, has_results = self._retrieve(
            question,
            k
        )

        if not has_results:
            return {
                "answer": self.NOT_FOUND_MESSAGE,
                "sources": []
            }

        prompt = textwrap.dedent(
            f"""
            You are a retrieval-augmented AI assistant.

            You MUST answer ONLY using the provided Context.

            If the Context is empty or does not contain the answer, reply exactly:

            "I couldn't find that information in the uploaded documents."

            Do not use your own knowledge.
            Do not guess.
            Do not answer from memory.

            Context:

            {context}

            Question:

            {question}
            """
        ).strip()

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

        context, unique_sources, has_results = self._retrieve(
            rewritten_question,
            k
        )

        if not has_results:

            yield {
                "type": "token",
                "data": self.NOT_FOUND_MESSAGE
            }

            self.memory.add_user(question)
            self.memory.add_assistant(self.NOT_FOUND_MESSAGE)

            yield {
                "type": "sources",
                "data": []
            }

            return

        system_prompt = textwrap.dedent(
            """
            You are a retrieval-augmented AI assistant.

            You MUST answer ONLY using the provided Context.

            If the Context is empty or does not contain the answer, reply exactly:

            "I couldn't find that information in the uploaded documents."

            Do not use your own knowledge.
            Do not guess.
            Do not answer from memory.
            """
        ).strip()

        messages = [
            {
                "role": "system",
                "content": system_prompt
            }
        ]

        messages.extend(
            self.memory.history()
        )

        user_prompt = textwrap.dedent(
            f"""
            Context:

            {context}

            Question:

            {rewritten_question}
            """
        ).strip()

        messages.append(
            {
                "role": "user",
                "content": user_prompt
            }
        )

        answer = ""

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

    def clear_documents(self):
        self.store.clear()

    def list_documents(self):
        return self.store.list_documents()
    
    def index_url(self, url):

        pages = URLExtractor.extract(url)

        chunks = TextChunker.chunk_pages(pages)

        embeddings = [
            EmbeddingGenerator.generate(
                chunk["text"]
            )
            for chunk in chunks
        ]

        self.store.add_chunks(
            chunks,
            embeddings
        )

        return len(chunks)