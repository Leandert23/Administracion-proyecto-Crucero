# mi_proyecto/urls.py
from django.urls import path, include
from django.contrib.auth import views as auth_views
from apps.usuarios import views as usuario_views

urlpatterns = [
    # Authentication URLs
    path('login/', usuario_views.custom_login, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('password-change/', usuario_views.custom_password_change, name='password_change'),
    path('password-change/done/', auth_views.PasswordChangeDoneView.as_view(
        template_name='auth/password_change_done.html'
    ), name='password_change_done'),
    
    # Password reset
    path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name='auth/password_reset.html',
        email_template_name='auth/password_reset_email.html',
        subject_template_name='auth/password_reset_subject.txt',
        success_url='/password-reset/done/'
    ), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='auth/password_reset_done.html'
    ), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='auth/password_reset_confirm.html',
        success_url='/reset/done/'
    ), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='auth/password_reset_complete.html'
    ), name='password_reset_complete'),
    # Crear rol desde modal
    path('roles/create/', usuario_views.create_role, name='create_role'),
    path('roles/list/', usuario_views.roles_list, name='roles_list'),
    path('roles/<int:role_id>/edit/', usuario_views.edit_role, name='edit_role'),
    path('roles/<int:role_id>/', usuario_views.role_detail, name='role_detail'),
    path('modules/list/', usuario_views.modules_list, name='modules_list'),
    path('search/', usuario_views.search_users, name='search_users'),
    # Crear usuario desde modal (rutas relativas; se incluyen bajo 'usuarios/' en el proyecto)
    path('create/', usuario_views.create_user, name='create_user'),
    path('create/simple/', usuario_views.create_user_simple, name='create_user_simple'),
    path('by-crucero/', usuario_views.users_by_crucero, name='users_by_crucero'),
    path('<int:usuario_id>/deactivate/', usuario_views.deactivate_user, name='deactivate_user'),
    path('<int:usuario_id>/activate/', usuario_views.activate_user, name='activate_user'),
    path('<int:usuario_id>/edit/', usuario_views.edit_user, name='edit_user'),
    # Admin-only: manage superusers without crucero
    path('admin/superusers/', usuario_views.admin_superusers, name='admin_superusers'),
    path('admin/superusers/create/', usuario_views.create_superuser_admin, name='create_superuser_admin'),
]
