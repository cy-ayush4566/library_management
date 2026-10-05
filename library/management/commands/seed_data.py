from datetime import timedelta

from django.contrib.auth.models import Group, User
from django.core.management.base import BaseCommand
from django.utils import timezone

from library.models import Author, Book, Category, Fine, Member, Transaction


class Command(BaseCommand):
    help = "Create realistic demonstration data for the library system."

    def handle(self, *args, **options):
        librarian_group, _ = Group.objects.get_or_create(name="Librarian")
        admin, _ = User.objects.get_or_create(username="admin", defaults={"first_name": "Library", "last_name": "Admin", "is_staff": True, "is_superuser": True})
        admin.is_staff = admin.is_superuser = True
        admin.set_password("admin123")
        admin.save()
        librarian, _ = User.objects.get_or_create(username="librarian", defaults={"first_name": "Anita", "last_name": "Sharma"})
        librarian.set_password("librarian123")
        librarian.save()
        librarian.groups.add(librarian_group)
        author_info = [("Robert C. Martin", "Software engineer and author known for clean code practices."), ("Bjarne Stroustrup", "Creator of the C++ programming language."), ("Andrew S. Tanenbaum", "Computer science professor and textbook author."), ("Eric Matthes", "Author of practical programming books for beginners."), ("E. Balagurusamy", "Indian author of widely used programming textbooks."), ("Abraham Silberschatz", "Author and computer science researcher."), ("James Clear", "Writer on habits and personal improvement.")]
        authors = {name: Author.objects.get_or_create(name=name, defaults={"biography": bio})[0] for name, bio in author_info}
        category_names = ["Programming", "Database", "Computer Networks", "Operating Systems", "Software Engineering", "Personal Development"]
        categories = {name: Category.objects.get_or_create(name=name, defaults={"description": f"Books about {name.lower()}."})[0] for name in category_names}
        books = [("Clean Code", "9780132350884", "Robert C. Martin", "Software Engineering"), ("The C++ Programming Language", "9780321563842", "Bjarne Stroustrup", "Programming"), ("Computer Networks", "9780132126953", "Andrew S. Tanenbaum", "Computer Networks"), ("Python Crash Course", "9781593279288", "Eric Matthes", "Programming"), ("Programming in ANSI C", "9781259004619", "E. Balagurusamy", "Programming"), ("Database System Concepts", "9780078022159", "Abraham Silberschatz", "Database"), ("Operating System Concepts", "9781119800361", "Abraham Silberschatz", "Operating Systems"), ("Atomic Habits", "9780735211292", "James Clear", "Personal Development"), ("The Clean Coder", "9780137081073", "Robert C. Martin", "Software Engineering"), ("Modern Operating Systems", "9780133591620", "Andrew S. Tanenbaum", "Operating Systems"), ("Effective Python", "9780134853987", "Eric Matthes", "Programming"), ("Head First SQL", "9780596526849", "Abraham Silberschatz", "Database"), ("Computer Networking", "9780132126953X", "Andrew S. Tanenbaum", "Computer Networks"), ("Agile Software Development", "9780135974445", "Robert C. Martin", "Software Engineering"), ("Python for Data Analysis", "9781098104030", "Eric Matthes", "Programming")]
        book_objects = []
        for index, (title, isbn, author, category) in enumerate(books, start=1):
            book, _ = Book.objects.get_or_create(isbn=isbn, defaults={"title": title, "author": authors[author], "category": categories[category], "publisher": "Academic Press", "description": f"A useful college library edition of {title}.", "total_copies": 4, "available_copies": 4})
            book_objects.append(book)
        members = []
        for index, (username, first, last) in enumerate([("student1", "Aarav", "Patel"), ("student2", "Diya", "Verma"), ("student3", "Kabir", "Singh"), ("student4", "Meera", "Nair")], start=1):
            user, _ = User.objects.get_or_create(username=username, defaults={"first_name": first, "last_name": last, "email": f"{username}@college.edu"})
            user.first_name, user.last_name = first, last
            user.set_password("student123")
            user.save()
            member, _ = Member.objects.get_or_create(user=user, defaults={"member_id": f"BCS2026{index:03d}", "phone": f"98765000{index}", "course": "B.Sc. Computer Science", "department": "Computer Science", "year": 2, "status": "active"})
            members.append(member)
        today = timezone.localdate()
        if not Transaction.objects.exists():
            issued = Transaction.objects.create(book=book_objects[0], member=members[0], issued_by=librarian, issue_date=today - timedelta(days=5), due_date=today + timedelta(days=9))
            book_objects[0].available_copies -= 1; book_objects[0].save(update_fields=["available_copies"])
            late = Transaction.objects.create(book=book_objects[3], member=members[1], issued_by=librarian, issue_date=today - timedelta(days=20), due_date=today - timedelta(days=6))
            book_objects[3].available_copies -= 1; book_objects[3].save(update_fields=["available_copies"])
            returned = Transaction.objects.create(book=book_objects[5], member=members[2], issued_by=librarian, issue_date=today - timedelta(days=30), due_date=today - timedelta(days=16), return_date=today - timedelta(days=14), status="returned")
            Fine.objects.get_or_create(transaction=returned, defaults={"amount": 10, "reason": "Overdue by 2 day(s)", "paid": True})
        self.stdout.write(self.style.SUCCESS("Demo data created. Use admin/admin123, librarian/librarian123, or student1/student123."))
