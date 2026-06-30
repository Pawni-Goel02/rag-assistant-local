from pathlib import Path
import fitz  # PyMuPDF
from docx import Document
import re


class TextExtractor:

    @staticmethod
    def extract_pdf(file_path: Path):

        document = fitz.open(file_path)

        pages = []

        for page_number, page in enumerate(document, start=1):

            text = page.get_text("text")
            text = re.sub(r"\s+", " ", text).strip()

            pages.append(
                {
                    "source": file_path.name,
                    "page": page_number,
                    "text": text
                }
            )

        document.close()

        return pages


    @staticmethod
    def extract_docx(file_path: Path):

        doc = Document(file_path)

        text = "\n".join(
            paragraph.text
            for paragraph in doc.paragraphs
        )

        return [{
            "source": file_path.name,
            "page": 1,
            "text": text
        }]


    @staticmethod
    def extract_txt(file_path: Path):

        with open(
            file_path,
            "r",
            encoding="utf-8",
            errors="ignore"
        ) as file:

            text = file.read()

        return [{
            "source": file_path.name,
            "page": 1,
            "text": text
        }]


    @staticmethod
    def extract(file_path: Path):

        extension = file_path.suffix.lower()

        if extension == ".pdf":
            return TextExtractor.extract_pdf(file_path)

        if extension == ".docx":
            return TextExtractor.extract_docx(file_path)

        if extension == ".txt":
            return TextExtractor.extract_txt(file_path)

        raise ValueError("Unsupported file type")