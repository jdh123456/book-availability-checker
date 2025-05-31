from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

def search_gutenberg(title, author=""):
    query = f"{title} {author}".strip().replace(" ", "+")
    url = f"https://gutendex.com/books?search={query}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        for book in data.get("results", []):
            epub_link = book.get("formats", {}).get("application/epub+zip")
            if epub_link:
                return {
                    "title": book.get("title"),
                    "source": "Project Gutenberg",
                    "link": epub_link
                }
    except:
        return None

def search_google_books(title, author=""):
    q = f"{title} {author}".strip().replace(" ", "+")
    url = f"https://www.googleapis.com/books/v1/volumes?q={q}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        items = data.get("items", [])
        results = []
        for item in items:
            volume_info = item.get("volumeInfo", {})
            link = volume_info.get("infoLink")
            if link:
                results.append({
                    "title": volume_info.get("title", "Unknown"),
                    "source": "Google Books",
                    "link": link
                })
        return results
    except:
        return []

def search_internet_archive(title, author=""):
    q = f"{title} {author}".strip().replace(" ", "+")
    url = f"https://archive.org/advancedsearch.php?q={q}&output=json"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        docs = data.get("response", {}).get("docs", [])
        results = []
        for doc in docs[:3]:  # limit to first few
            identifier = doc.get("identifier")
            if identifier:
                results.append({
                    "title": doc.get("title", "Unknown"),
                    "source": "Internet Archive",
                    "link": f"https://archive.org/details/{identifier}"
                })
        return results
    except:
        return []

@app.route("/")
def home():
    return "Book Availability Checker is running. Use /check_availability?title=...&author=..."

@app.route("/check_availability")
def check_availability():
    title = request.args.get("title", "")
    author = request.args.get("author", "")

    results = []

    gutenberg_result = search_gutenberg(title, author)
    if gutenberg_result:
        results.append(gutenberg_result)

    results.extend(search_google_books(title, author))
    results.extend(search_internet_archive(title, author))

    return jsonify(results)