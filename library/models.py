from datetime import timedelta

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class Author(models.Model):
    name = models.CharField(max_length=150, unique=True)
    biography = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Book(models.Model):
    title = models.CharField(max_length=255)
    isbn = models.CharField("ISBN", max_length=20, unique=True)
    author = models.ForeignKey(Author, on_delete=models.PROTECT, related_name="books")
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="books")
    publisher = models.CharField(max_length=150, blank=True)
    publication_date = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True)
    total_copies = models.PositiveIntegerField(default=1)
    available_copies = models.PositiveIntegerField(default=1)
    cover_image = models.ImageField(upload_to="book_covers/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["title"]

    def clean(self):
        if self.available_copies > self.total_copies:
            raise ValidationError({"available_copies": "Available copies cannot exceed total copies."})

    def __str__(self):
        return f"{self.title} ({self.isbn})"


class Member(models.Model):
    STATUS_CHOICES = [("active", "Active"), ("inactive", "Inactive")]
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="member_profile")
    member_id = models.CharField(max_length=30, unique=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    course = models.CharField(max_length=120, blank=True)
    department = models.CharField(max_length=120, blank=True)
    year = models.PositiveSmallIntegerField(null=True, blank=True)
    registration_date = models.DateField(default=timezone.localdate)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="active")

    class Meta:
        ordering = ["member_id"]

    def __str__(self):
        return f"{self.member_id} — {self.user.get_full_name() or self.user.username}"


class Transaction(models.Model):
    STATUS_CHOICES = [("issued", "Issued"), ("returned", "Returned")]
    book = models.ForeignKey(Book, on_delete=models.PROTECT, related_name="transactions")
    member = models.ForeignKey(Member, on_delete=models.PROTECT, related_name="transactions")
    issued_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="issued_transactions")
    issue_date = models.DateField(default=timezone.localdate)
    due_date = models.DateField()
    return_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="issued")
    fine_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0)

    class Meta:
        ordering = ["-issue_date", "-id"]

    def save(self, *args, **kwargs):
        if not self.due_date:
            self.due_date = self.issue_date + timedelta(days=14)
        super().save(*args, **kwargs)

    @property
    def overdue_days(self):
        comparison = self.return_date or timezone.localdate()
        return max(0, (comparison - self.due_date).days) if self.status == "issued" or self.return_date else 0

    def __str__(self):
        return f"{self.book.title} — {self.member.member_id}"


class Fine(models.Model):
    transaction = models.OneToOneField(Transaction, on_delete=models.CASCADE, related_name="fine")
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    reason = models.CharField(max_length=255)
    paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["paid", "-created_at"]

    def __str__(self):
        return f"₹{self.amount} for transaction #{self.transaction_id}"
