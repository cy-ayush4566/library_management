from datetime import timedelta
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import AuthenticationForm
from django.core.paginator import Paginator
from django.db import transaction as db_transaction
from django.db.models import Count, Q, Sum
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from .forms import AuthorForm, BookForm, CategoryForm, FineForm, IssueBookForm, MemberForm, ReturnBookForm
from .models import Author, Book, Category, Fine, Member, Transaction
from .services.flask_api import get_statistics


def librarian_required(view):
    return user_passes_test(lambda user: user.is_authenticated and (user.is_staff or user.groups.filter(name="Librarian").exists()), login_url="login")(view)


def staff_required(view):
    return user_passes_test(lambda user: user.is_authenticated and user.is_staff, login_url="login")(view)


def _page(request, queryset, size=10):
    return Paginator(queryset, size).get_page(request.GET.get("page"))


def _library_stats():
    return {
        "total_books": Book.objects.count(),
        "available_books": Book.objects.aggregate(n=Sum("available_copies"))["n"] or 0,
        "issued_books": Transaction.objects.filter(status="issued").count(),
        "total_members": Member.objects.count(),
        "overdue_books": Transaction.objects.filter(status="issued", due_date__lt=timezone.localdate()).count(),
        "total_fines": Fine.objects.aggregate(n=Sum("amount"))["n"] or Decimal("0"),
    }


def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        login(request, form.get_user())
        return redirect(request.GET.get("next") or "dashboard")
    return render(request, "login.html", {"form": form})


@login_required
def dashboard(request):
    today = timezone.localdate()
    if hasattr(request.user, "member_profile") and not (request.user.is_staff or request.user.groups.filter(name="Librarian").exists()):
        member = request.user.member_profile
        active = Transaction.objects.filter(member=member, status="issued").select_related("book")
        return render(request, "dashboard/student.html", {
            "active_transactions": active, "history": Transaction.objects.filter(member=member).select_related("book")[:6],
            "my_books": active.count(), "due_soon": active.filter(due_date__range=(today, today + timedelta(days=3))).count(),
            "overdue": active.filter(due_date__lt=today).count(), "my_fines": Fine.objects.filter(transaction__member=member, paid=False).aggregate(n=Sum("amount"))["n"] or 0,
        })
    stats = get_statistics() or _library_stats()
    context = {"stats": stats, "recent_transactions": Transaction.objects.select_related("book", "member", "member__user")[:8]}
    if request.user.is_staff:
        return render(request, "dashboard/admin.html", context)
    context.update({
        "today_issues": Transaction.objects.filter(issue_date=today).count(),
        "today_returns": Transaction.objects.filter(return_date=today).count(),
        "pending_fines": Fine.objects.filter(paid=False).aggregate(n=Sum("amount"))["n"] or 0,
    })
    return render(request, "dashboard/librarian.html", context)


@login_required
def book_list(request):
    query = request.GET.get("q", "").strip()
    books = Book.objects.select_related("author", "category")
    if query:
        books = books.filter(Q(title__icontains=query) | Q(isbn__icontains=query) | Q(author__name__icontains=query) | Q(category__name__icontains=query))
    return render(request, "books/list.html", {"books": _page(request, books), "query": query})


@login_required
def book_detail(request, pk):
    return render(request, "books/detail.html", {"book": get_object_or_404(Book.objects.select_related("author", "category"), pk=pk)})


@librarian_required
def book_create(request):
    form = BookForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Book added successfully.")
        return redirect("book_list")
    return render(request, "books/form.html", {"form": form, "title": "Add Book"})


@librarian_required
def book_edit(request, pk):
    book = get_object_or_404(Book, pk=pk)
    form = BookForm(request.POST or None, request.FILES or None, instance=book)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Book updated successfully.")
        return redirect("book_detail", pk=book.pk)
    return render(request, "books/form.html", {"form": form, "title": "Edit Book"})


@librarian_required
def book_delete(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == "POST":
        try:
            book.delete()
            messages.success(request, "Book deleted.")
        except Exception:
            messages.error(request, "This book has transaction records and cannot be deleted.")
        return redirect("book_list")
    return render(request, "confirm_delete.html", {"object": book, "cancel_url": reverse("book_detail", args=[pk])})


def _simple_crud(request, model, form_class, template_prefix, label, pk=None):
    instance = get_object_or_404(model, pk=pk) if pk else None
    form = form_class(request.POST or None, instance=instance)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, f"{label} saved successfully.")
        return redirect(f"{template_prefix}_list")
    return render(request, "shared/form.html", {"form": form, "title": f"{'Edit' if instance else 'Add'} {label}"})


@staff_required
def author_list(request):
    return render(request, "shared/list.html", {"items": _page(request, Author.objects.annotate(book_count=Count("books")).order_by("name")), "title": "Authors", "add_url": "author_create", "edit_url": "author_edit", "is_category": False})


@staff_required
def author_form(request, pk=None):
    return _simple_crud(request, Author, AuthorForm, "author", "Author", pk)


@staff_required
def category_list(request):
    return render(request, "shared/list.html", {"items": _page(request, Category.objects.annotate(book_count=Count("books")).order_by("name")), "title": "Categories", "add_url": "category_create", "edit_url": "category_edit", "is_category": True})


@staff_required
def category_form(request, pk=None):
    return _simple_crud(request, Category, CategoryForm, "category", "Category", pk)


@librarian_required
def member_list(request):
    query = request.GET.get("q", "").strip()
    members = Member.objects.select_related("user")
    if query:
        members = members.filter(Q(member_id__icontains=query) | Q(user__username__icontains=query) | Q(user__first_name__icontains=query))
    return render(request, "members/list.html", {"members": _page(request, members), "query": query})


@librarian_required
def member_create(request):
    form = MemberForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Member added successfully.")
        return redirect("member_list")
    return render(request, "members/form.html", {"form": form, "title": "Add Member"})


@librarian_required
def member_edit(request, pk):
    member = get_object_or_404(Member, pk=pk)
    form = MemberForm(request.POST or None, instance=member)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Member updated successfully.")
        return redirect("member_list")
    return render(request, "members/form.html", {"form": form, "title": "Edit Member"})


@librarian_required
def issue_book(request):
    form = IssueBookForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        with db_transaction.atomic():
            book = Book.objects.select_for_update().get(pk=form.cleaned_data["book"].pk)
            member = Member.objects.select_for_update().get(pk=form.cleaned_data["member"].pk)
            open_count = Transaction.objects.filter(member=member, status="issued").count()
            if book.available_copies < 1 or member.status != "active" or open_count >= 5:
                messages.error(request, "Issue could not be completed. Please check availability, status, and borrowing limit.")
                return redirect("issue_book")
            Transaction.objects.create(book=book, member=member, issued_by=request.user, issue_date=timezone.localdate(), due_date=timezone.localdate() + timedelta(days=14))
            book.available_copies -= 1
            book.save(update_fields=["available_copies", "updated_at"])
        messages.success(request, f"{book.title} issued to {member.member_id}. Due in 14 days.")
        return redirect("transaction_list")
    return render(request, "transactions/issue.html", {"form": form})


@librarian_required
def return_book(request):
    form = ReturnBookForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        with db_transaction.atomic():
            record = Transaction.objects.select_for_update().select_related("book").get(pk=form.cleaned_data["transaction"].pk)
            if record.status != "issued":
                messages.error(request, "This transaction was already returned.")
                return redirect("return_book")
            today = timezone.localdate()
            record.return_date, record.status = today, "returned"
            days = max(0, (today - record.due_date).days)
            record.fine_amount = Decimal(days * 5)
            record.save(update_fields=["return_date", "status", "fine_amount"])
            record.book.available_copies += 1
            record.book.save(update_fields=["available_copies", "updated_at"])
            if days:
                Fine.objects.update_or_create(transaction=record, defaults={"amount": record.fine_amount, "reason": f"Overdue by {days} day(s)"})
        messages.success(request, f"Book returned. Fine: ₹{record.fine_amount}.")
        return redirect("transaction_list")
    return render(request, "transactions/return.html", {"form": form})


@librarian_required
def transaction_list(request):
    records = Transaction.objects.select_related("book", "member", "member__user", "issued_by")
    return render(request, "transactions/list.html", {"transactions": _page(request, records)})


@librarian_required
def overdue_list(request):
    records = Transaction.objects.filter(status="issued", due_date__lt=timezone.localdate()).select_related("book", "member", "member__user")
    return render(request, "transactions/list.html", {"transactions": _page(request, records), "title": "Overdue Books"})


@librarian_required
def fine_list(request):
    return render(request, "fines/list.html", {"fines": _page(request, Fine.objects.select_related("transaction", "transaction__book", "transaction__member", "transaction__member__user"))})


@librarian_required
def fine_toggle_paid(request, pk):
    fine = get_object_or_404(Fine, pk=pk)
    if request.method == "POST":
        fine.paid = not fine.paid
        fine.save(update_fields=["paid"])
        messages.success(request, "Fine payment status updated.")
    return redirect("fine_list")


@librarian_required
def reports(request):
    total_transactions = Transaction.objects.count()
    return render(request, "reports/index.html", {
        "stats": _library_stats(),
        "categories": Category.objects.annotate(total=Count("books")).order_by("-total"),
        "popular_books": Book.objects.annotate(total=Count("transactions")).order_by("-total", "title")[:8],
        "active_members": Member.objects.annotate(total=Count("transactions")).order_by("-total", "member_id")[:8],
        "total_issued": total_transactions,
        "total_returned": Transaction.objects.filter(status="returned").count(),
    })


@login_required
def my_books(request):
    if not hasattr(request.user, "member_profile"):
        raise Http404
    transactions = Transaction.objects.filter(member=request.user.member_profile, status="issued").select_related("book")
    return render(request, "transactions/list.html", {"transactions": transactions, "title": "My Issued Books", "student_view": True})


@login_required
def my_history(request):
    if not hasattr(request.user, "member_profile"):
        raise Http404
    transactions = Transaction.objects.filter(member=request.user.member_profile).select_related("book")
    return render(request, "transactions/list.html", {"transactions": _page(request, transactions), "title": "My Borrowing History", "student_view": True})


@login_required
def my_fines(request):
    if not hasattr(request.user, "member_profile"):
        raise Http404
    fines = Fine.objects.filter(transaction__member=request.user.member_profile).select_related("transaction", "transaction__book")
    return render(request, "fines/list.html", {"fines": fines, "student_view": True})


@login_required
def profile(request):
    if not hasattr(request.user, "member_profile"):
        raise Http404
    return render(request, "members/profile.html", {"member": request.user.member_profile})
