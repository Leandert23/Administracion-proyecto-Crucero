from django.db.models.signals import post_migrate
from django.contrib.auth.models import Group, Permission
from django.dispatch import receiver
from django.apps import apps

GROUP_PERMS = {
    'Admin Restaurante': ['add', 'change', 'delete', 'view'],
    'Gestor Inventario': ['view_ingrediente', 'change_warehousestock', 'view_warehousestock', 'view_pantryitem', 'change_pantryitem', 'add_request', 'change_request', 'view_request', 'add_requestline', 'change_requestline', 'view_requestline'],
    'Operador Consumo': ['view_platillo', 'view_menu', 'view_restaurante', 'add_serviceinvoice', 'add_buffetbulkrecord'],
    'Creador Menus': ['add_menu', 'change_menu', 'view_menu', 'add_platillo', 'change_platillo', 'view_platillo'],
}

@receiver(post_migrate)
def create_groups(sender, **kwargs):
    if sender.label != 'restaurant':
        return
    app_models = apps.get_app_config('restaurant').get_models()
    # Build permission map by codename
    perm_map = {p.codename: p for p in Permission.objects.filter(content_type__app_label='restaurant')}
    for group_name, perms in GROUP_PERMS.items():
        group, _ = Group.objects.get_or_create(name=group_name)
        assign = []
        for code in perms:
            if '_' not in code:  # expand generic verbs to all restaurant models
                verbs = [code]
                for p in list(perm_map.values()):
                    if p.codename.startswith(tuple(f"{v}_" for v in verbs)):
                        assign.append(p)
            else:
                p = perm_map.get(code)
                if p:
                    assign.append(p)
        group.permissions.set(assign)
        group.save()
