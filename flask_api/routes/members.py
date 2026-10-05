from flask import Blueprint, jsonify
from library.models import Member
from services.serializers import member_data

members_api = Blueprint("members", __name__)


@members_api.get("")
def list_members():
    members = Member.objects.select_related("user").all()
    return jsonify(success=True, data=[member_data(member) for member in members]), 200


@members_api.get("/<int:member_id>")
def get_member(member_id):
    try:
        member = Member.objects.select_related("user").get(pk=member_id)
    except Member.DoesNotExist:
        return jsonify(success=False, error="Member not found"), 404
    return jsonify(success=True, data=member_data(member)), 200
