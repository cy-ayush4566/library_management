from django.contrib.auth.views import LogoutView
from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"), path("login/", views.login_view, name="login"), path("logout/", LogoutView.as_view(), name="logout"),
    path("books/", views.book_list, name="book_list"), path("books/add/", views.book_create, name="book_create"), path("books/<int:pk>/", views.book_detail, name="book_detail"), path("books/<int:pk>/edit/", views.book_edit, name="book_edit"), path("books/<int:pk>/delete/", views.book_delete, name="book_delete"),
    path("authors/", views.author_list, name="author_list"), path("authors/add/", views.author_form, name="author_create"), path("authors/<int:pk>/edit/", views.author_form, name="author_edit"),
    path("categories/", views.category_list, name="category_list"), path("categories/add/", views.category_form, name="category_create"), path("categories/<int:pk>/edit/", views.category_form, name="category_edit"),
    path("members/", views.member_list, name="member_list"), path("members/add/", views.member_create, name="member_create"), path("members/<int:pk>/edit/", views.member_edit, name="member_edit"),
    path("issue/", views.issue_book, name="issue_book"), path("return/", views.return_book, name="return_book"), path("transactions/", views.transaction_list, name="transaction_list"), path("overdue/", views.overdue_list, name="overdue_list"),
    path("fines/", views.fine_list, name="fine_list"), path("fines/<int:pk>/toggle/", views.fine_toggle_paid, name="fine_toggle_paid"), path("reports/", views.reports, name="reports"),
    path("my-books/", views.my_books, name="my_books"), path("my-history/", views.my_history, name="my_history"), path("my-fines/", views.my_fines, name="my_fines"), path("profile/", views.profile, name="profile"),
]
