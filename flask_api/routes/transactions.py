from flask import Blueprint, jsonify
from library.models import Transaction
from services.serializers import transaction_data

transactions_api = Blueprint("transactions", __name__)


@transactions_api.get("")
def list_transactions():
    records = Transaction.objects.select_related("book", "member", "member__user", "issued_by").all()
    return jsonify(success=True, data=[transaction_data(record) for record in records]), 200


@transactions_api.get("/<int:transaction_id>")
def get_transaction(transaction_id):
    try:
        record = Transaction.objects.select_related("book", "member", "member__user", "issued_by").get(pk=transaction_id)
    except Transaction.DoesNotExist:
        return jsonify(success=False, error="Transaction not found"), 404
    return jsonify(success=True, data=transaction_data(record)), 200
