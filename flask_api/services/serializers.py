def book_data(book):
    return {"id": book.id, "title": book.title, "isbn": book.isbn, "author": book.author.name, "category": book.category.name, "publisher": book.publisher, "publication_date": book.publication_date.isoformat() if book.publication_date else None, "description": book.description, "total_copies": book.total_copies, "available_copies": book.available_copies}


def member_data(member):
    return {"id": member.id, "member_id": member.member_id, "username": member.user.username, "name": member.user.get_full_name() or member.user.username, "course": member.course, "department": member.department, "year": member.year, "status": member.status, "registration_date": member.registration_date.isoformat()}


def transaction_data(record):
    return {"id": record.id, "book": {"id": record.book_id, "title": record.book.title}, "member": {"id": record.member_id, "member_id": record.member.member_id, "name": record.member.user.get_full_name() or record.member.user.username}, "issued_by": record.issued_by.username, "issue_date": record.issue_date.isoformat(), "due_date": record.due_date.isoformat(), "return_date": record.return_date.isoformat() if record.return_date else None, "status": record.status, "fine_amount": float(record.fine_amount)}
