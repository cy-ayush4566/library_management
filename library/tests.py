from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Author, Book, Category, Member, Transaction


class LibraryWorkflowTests(TestCase):
    def setUp(self):
        self.librarian = User.objects.create_user("librarian", password="pass12345", is_staff=True)
        student = User.objects.create_user("student", password="pass12345")
        self.member = Member.objects.create(user=student, member_id="M001", status="active")
        author = Author.objects.create(name="Author")
        category = Category.objects.create(name="Category")
        self.book = Book.objects.create(title="Test Book", isbn="1234567890123", author=author, category=category, total_copies=2, available_copies=2)

    def test_book_list_requires_login(self):
        response = self.client.get(reverse("book_list"))
        self.assertEqual(response.status_code, 302)

    def test_librarian_can_issue_and_return(self):
        self.client.login(username="librarian", password="pass12345")
        response = self.client.post(reverse("issue_book"), {"member": self.member.pk, "book": self.book.pk})
        self.assertEqual(response.status_code, 302)
        record = Transaction.objects.get()
        self.book.refresh_from_db()
        self.assertEqual(self.book.available_copies, 1)
        record.due_date = timezone.localdate() - timedelta(days=3)
        record.save()
        response = self.client.post(reverse("return_book"), {"transaction": record.pk})
        self.assertEqual(response.status_code, 302)
        record.refresh_from_db(); self.book.refresh_from_db()
        self.assertEqual(record.status, "returned")
        self.assertEqual(record.fine_amount, 15)
        self.assertEqual(self.book.available_copies, 2)
