from django.db.models.signals import post_migrate
from django.dispatch import receiver

GROUPS = {
    "Public Verified": [],
    "Club Executive": [
        ("clubs", "change_club"),
        ("clubs", "add_clubwhyjoin"),
        ("clubs", "change_clubwhyjoin"),
        ("clubs", "delete_clubwhyjoin"),
        ("clubs", "add_clubannouncement"),
        ("clubs", "change_clubannouncement"),
        ("clubs", "delete_clubannouncement")    
    ],
    "Club Administrators" : [
        ("clubs", "can_approve_club_changes"),
        ("clubs", "add_club"),
        ("clubs", "change_club"),
        ("clubs", "add_clubwhyjoin"),
        ("clubs", "change_clubwhyjoin"),
        ("clubs", "delete_clubwhyjoin"),
        ("clubs", "add_clubannouncement"),
        ("clubs", "change_clubannouncement"),
        ("clubs", "delete_clubannouncement")
    ]
}

@receiver(post_migrate, dispatch_uid="users.signals.create_default_groups")
def create_default_groups(sender, **kwargs):
    from django.contrib.auth.models import Group, Permission

    for group_name, perm_specs in GROUPS.items():
        group, _ = Group.objects.get_or_create(name=group_name)

        permissions = []
        for app_label, codename in perm_specs: 
            try: 
                permissions.append(Permission.objects.get(content_type__app_label = app_label, codename=codename))
            except Permission.DoesNotExist:
                continue

        if permissions:
            group.permissions.add(*permissions)
