from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

def search_google_books(title, author=""):
    query = f"{title} {author}".strip().replace(" ", "+")
    url = f"https://www.googleapis.com/books/v1/volumes?q={query}"
    response = requests.get(url)
    data = response.json()
    if "items" in data:
        for item in data["items"]:
            info = item.get("volumeInfo", {})
            if title.lower() in info.get("title", "").lower():
                return {
                    "source": "Google Books",
                    "title": info.get("title"),
                    "link": info.get("infoLink")
                }
    return None

def search_internet_archive(title, author=""):
    query = f"{title} {author}".strip().replace(" ", "+")
    url = f"https://archive.org/advancedsearch.php?q=title:({query})&fl[]=identifier,title&output=json"
    response = requests.get(url)
    data = response.json()
    if data["response"]["docs"]:
        doc = data["response"]["docs"][0]
        return {
            "source": "Internet Archive",
            "title": doc.get("title"),
            "link": f"https://archive.org/details/{doc['identifier']}"
        }
    return None

@app.route("/")
def home():
    return "Book Availability Checker is running. Use /check_availability?title=...&author=..."

@app.route("/check_availability", methods=["GET"])
def check_availability():
    title = request.args.get("title")
    author = request.args.get("author", "")

    results = []

    gb_result = search_google_books(title, author)
    if gb_result:
        results.append(gb_result)

    ia_result = search_internet_archive(title, author)
    if ia_result:
        results.append(ia_result)

    return jsonify(results if results else {"message": "No results found."})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))
    app.run(host="0.0.0.0", port=port)
