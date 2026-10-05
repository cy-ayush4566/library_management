"""Small, isolated client for the separate Flask read API."""
import requests
from django.conf import settings


def _get(path, params=None):
    try:
        response = requests.get(f"{settings.FLASK_API_URL}{path}", params=params, timeout=2)
        response.raise_for_status()
        return response.json().get("data")
    except (requests.RequestException, ValueError):
        return None


def get_books():
    return _get("/api/books")


def get_book(book_id):
    return _get(f"/api/books/{book_id}")


def search_books(query):
    return _get("/api/books/search", {"q": query})


def get_statistics():
    return _get("/api/statistics")
