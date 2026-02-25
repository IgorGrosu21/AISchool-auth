from django.urls import path

from api import views

urlpatterns = [
    # Auth endpoints
    path("signup/", views.signup_view, name="signup"),
    path("login/", views.login_view, name="login"),
    path("oauth2/", views.oauth2_view, name="oauth2"),
    # Token endpoints
    path("refresh/", views.refresh_token_view, name="refresh"),
    path("logout/", views.logout_view, name="logout"),
    path("logout-all/", views.logout_all_view, name="logout-all"),
    # User endpoints
    path("user/", views.UserView.as_view(), name="user"),
    path("user/email/", views.user_email_view, name="user-email"),
    path("user/password/", views.user_password_view, name="user-password"),
    # Verification endpoints
    path("verify-code/", views.verify_code_view, name="verify-code"),
    path("restore/", views.restore_password_view, name="restore"),
]
