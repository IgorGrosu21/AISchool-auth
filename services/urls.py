from django.urls import path

from services import views

urlpatterns = [
    # Service token endpoint
    path("auth/", views.AuthView.as_view(), name="auth"),
    # Create users bulk endpoint
    path("create-users-bulk/", views.CreateUsersBulkView.as_view(), name="create-users-bulk"),
    # Generate token endpoint
    path("generate-token/", views.GenerateTokenView.as_view(), name="generate-token"),
    # JWKS endpoint
    path(".well-known/jwks.json", views.JWKSView.as_view(), name="jwks"),
]
