from datetime import timedelta

from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import Author, Book, Category, Fine, Member, Transaction


class StyledForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")


class BookForm(StyledForm):
    class Meta:
        model = Book
        fields = ["title", "isbn", "author", "category", "publisher", "publication_date", "description", "total_copies", "available_copies", "cover_image"]
        widgets = {"publication_date": forms.DateInput(attrs={"type": "date"}), "description": forms.Textarea(attrs={"rows": 4})}


class AuthorForm(StyledForm):
    class Meta:
        model = Author
        fields = ["name", "biography"]
        widgets = {"biography": forms.Textarea(attrs={"rows": 4})}


class CategoryForm(StyledForm):
    class Meta:
        model = Category
        fields = ["name", "description"]
        widgets = {"description": forms.Textarea(attrs={"rows": 4})}


class MemberForm(StyledForm):
    username = forms.CharField(max_length=150, help_text="Used for the member login.")
    first_name = forms.CharField(max_length=150)
    last_name = forms.CharField(max_length=150, required=False)
    email = forms.EmailField(required=False)
    password = forms.CharField(widget=forms.PasswordInput, required=False, help_text="Required only for a new member.")

    class Meta:
        model = Member
        fields = ["member_id", "phone", "address", "course", "department", "year", "registration_date", "status"]
        widgets = {"registration_date": forms.DateInput(attrs={"type": "date"}), "address": forms.Textarea(attrs={"rows": 3})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            user = self.instance.user
            for key in ("username", "first_name", "last_name", "email"):
                self.fields[key].initial = getattr(user, key)
            self.fields["password"].help_text = "Leave blank to keep the existing password."

    def clean_username(self):
        username = self.cleaned_data["username"]
        existing = User.objects.filter(username=username).exclude(pk=self.instance.user_id if self.instance.pk else None)
        if existing.exists():
            raise ValidationError("This username is already in use.")
        return username

    def save(self, commit=True):
        member = super().save(commit=False)
        data = self.cleaned_data
        if member.pk:
            user = member.user
        else:
            user = User()
        user.username, user.first_name, user.last_name, user.email = data["username"], data["first_name"], data["last_name"], data["email"]
        if data.get("password"):
            user.set_password(data["password"])
        elif not user.pk:
            user.set_password("student123")
        if commit:
            user.save()
            member.user = user
            member.save()
        return member


class IssueBookForm(StyledForm):
    class Meta:
        model = Transaction
        fields = ["member", "book"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["member"].queryset = Member.objects.filter(status="active")
        self.fields["book"].queryset = Book.objects.filter(available_copies__gt=0)

    def clean(self):
        cleaned = super().clean()
        member, book = cleaned.get("member"), cleaned.get("book")
        if member and member.status != "active":
            self.add_error("member", "Inactive members cannot borrow books.")
        if book and book.available_copies < 1:
            self.add_error("book", "This book is not currently available.")
        if member and Transaction.objects.filter(member=member, status="issued").count() >= 5:
            self.add_error("member", "A member can borrow at most 5 books.")
        return cleaned


class ReturnBookForm(forms.Form):
    transaction = forms.ModelChoiceField(queryset=Transaction.objects.none(), widget=forms.Select(attrs={"class": "form-control"}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["transaction"].queryset = Transaction.objects.filter(status="issued").select_related("book", "member", "member__user")


class FineForm(StyledForm):
    class Meta:
        model = Fine
        fields = ["paid"]
