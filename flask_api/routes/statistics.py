from decimal import Decimal

from flask import Blueprint, jsonify
from django.db.models import Sum
from django.utils import timezone
from library.models import Book, Fine, Member, Transaction

statistics_api = Blueprint("statistics", __name__)


@statistics_api.get("")
def statistics():
    data = {
        "total_books": Book.objects.count(),
        "available_books": Book.objects.aggregate(value=Sum("available_copies"))["value"] or 0,
        "issued_books": Transaction.objects.filter(status="issued").count(),
        "total_members": Member.objects.count(),
        "overdue_books": Transaction.objects.filter(status="issued", due_date__lt=timezone.localdate()).count(),
        "total_fines": float(Fine.objects.aggregate(value=Sum("amount"))["value"] or Decimal("0")),
    }
    return jsonify(success=True, data=data), 200
