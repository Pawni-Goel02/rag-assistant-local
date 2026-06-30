from pathlib import Path
from text_extract import TextExtractor

pages = TextExtractor.extract(
    Path("uploads/datasci.pdf")
)

for page in pages:
    print("=" * 40)
    print("Source:", page["source"])
    print("Page:", page["page"])
    print("=" * 40)
    print(page["text"][:300])