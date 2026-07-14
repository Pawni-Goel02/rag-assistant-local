import requests
from bs4 import BeautifulSoup


class URLExtractor:

    @staticmethod
    def extract(url):

        response = requests.get(
            url,
            timeout=10,
            headers={
                "User-Agent": "Mozilla/5.0"
            }
        )

        response.raise_for_status()

        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

        # Remove unwanted tags
        for tag in soup(
            [
                "script",
                "style",
                "noscript"
            ]
        ):
            tag.decompose()

        text = soup.get_text(
            separator="\n",
            strip=True
        )

        return [
            {
                "page": 1,
                "text": text,
                "source": url
            }
        ]