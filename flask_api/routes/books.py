from flask import Blueprint, jsonify, request
from django.db.models import Q
from library.models import Book
from services.serializers import book_data

books_api = Blueprint("books", __name__)


@books_api.get("")
def list_books():
    books = Book.objects.select_related("author", "category").all()
    return jsonify(success=True, data=[book_data(book) for book in books]), 200


@books_api.get("/search")
def search_books():
    query = request.args.get("q", "").strip()
    if not query:
        return jsonify(success=False, error="Query parameter 'q' is required"), 400
    books = Book.objects.select_related("author", "category").filter(Q(title__icontains=query) | Q(isbn__icontains=query) | Q(author__name__icontains=query) | Q(category__name__icontains=query))
    return jsonify(success=True, data=[book_data(book) for book in books]), 200


@books_api.get("/<int:book_id>")
def get_book(book_id):
    try:
        book = Book.objects.select_related("author", "category").get(pk=book_id)
    except Book.DoesNotExist:
        return jsonify(success=False, error="Book not found"), 404
    return jsonify(success=True, data=book_data(book)), 200
