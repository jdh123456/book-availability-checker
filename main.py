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
                    "link": epub_link,
                    "format": "ePub"
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
            results.append({
                "title": volume_info.get("title", "Unknown"),
                "source": "Google Books",
                "link": volume_info.get("infoLink"),
                "summary": volume_info.get("description", ""),
                "subject": ", ".join(volume_info.get("categories", [])),
                "format": "Website"
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
        for doc in docs[:3]:
            identifier = doc.get("identifier")
            if identifier:
                results.append({
                    "title": doc.get("title", "Unknown"),
                    "source": "Internet Archive",
                    "link": f"https://archive.org/details/{identifier}",
                    "format": "Website"
                })
        return results
    except:
        return []

def search_open_library(title, author=""):
    q = f"{title} {author}".strip().replace(" ", "+")
    url = f"https://openlibrary.org/search.json?title={q}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        docs = data.get("docs", [])
        if docs:
            doc = docs[0]
            olid = doc.get("key", "")  # e.g., "/works/OL123W"
            work_url = f"https://openlibrary.org{olid}.json"
            work_resp = requests.get(work_url)
            if work_resp.ok:
                work_data = work_resp.json()
                return {
                    "title": doc.get("title"),
                    "source": "Open Library",
                    "link": f"https://openlibrary.org{olid}",
                    "subject": ", ".join(work_data.get("subjects", [])[:5]),
                    "summary": work_data.get("description", {}).get("value") if isinstance(work_data.get("description"), dict) else work_data.get("description", ""),
                    "format": "Website"
                }
    except:
        return None

@app.route("/")
def home():
    return "Book Availability & Metadata Checker is running. Use /check_availability?title=...&author=..."

@app.route("/check_availability")
def check_availability():
    title = request.args.get("title", "")
    author = request.args.get("author", "")

    results = []

    # Add each source
    gutenberg_result = search_gutenberg(title, author)
    if gutenberg_result:
        results.append(gutenberg_result)

    results.extend(search_google_books(title, author))
    results.extend(search_internet_archive(title, author))

    openlib_result = search_open_library(title, author)
    if openlib_result:
        results.append(openlib_result)

    return jsonify(results)