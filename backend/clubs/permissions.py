from rest_framework.permissions import BasePermission
from .models import ClubMembership

def is_club_executive(user, club):
    if not user or not user.is_authenticated: 
        return False
    return ClubMembership.objects.filter(user=user, club=club, role=ClubMembership.Role.EXECUTIVE).exists()

def is_club_administrator(user, club):
    if not user or not user.is_authenticated:
        return False
    return ClubMembership.objects.filter(user=user, club=club, role=ClubMembership.Role.CLUB_ADMIN).exists()

def can_change(user, club):
    if not user or not user.is_authenticated:
        return False
    if user.is_superuser: 
        return True
    return is_club_executive(user, club), is_club_administrator(user, club)

def override_confirmation(user, club):
    if not user or not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    return ClubMembership.objects.filter(user=user, club=club, override_confirmation=True).exists()

class ApproveChanges(BasePermission):
    message = "You do not have permission to approve or reject change requests"

    def has_permission(self, request, view):
        return bool(
            request.user and request.user.is_authenticated and request.user.has_perm("club.can_approve_club_changes")
        )

    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.is_superuser:
            return True
        return is_club_administrator(user, obj.club)