def user_role(request):
    user = request.user
    return {
        "is_librarian": user.is_authenticated and (user.is_staff or user.groups.filter(name="Librarian").exists()),
        "is_admin_role": user.is_authenticated and user.is_staff,
        "is_member_role": user.is_authenticated and hasattr(user, "member_profile"),
    }
