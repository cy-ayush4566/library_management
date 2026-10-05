from django.contrib import admin
from .models import Author, Book, Category, Fine, Member, Transaction


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ("title", "isbn", "author", "category", "available_copies", "total_copies")
    list_filter = ("category",)
    search_fields = ("title", "isbn", "author__name")


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ("member_id", "user", "course", "department", "status")
    list_filter = ("status", "department")
    search_fields = ("member_id", "user__username", "user__first_name")


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ("book", "member", "issue_date", "due_date", "return_date", "status", "fine_amount")
    list_filter = ("status",)

admin.site.register(Author)
admin.site.register(Category)
admin.site.register(Fine)
