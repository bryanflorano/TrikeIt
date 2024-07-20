from django.urls import path
from . import views

urlpatterns = [
    path("accounts/login/", views.login_view, name="login_view"),
    path("accounts/signup/", views.signup_view, name="signup_view"),
    path("", views.index, name="index"),
    path("profile/", views.profile_view, name="profile_view"),
    path("payment/", views.payment_view, name="payment_view"),
    path("waiting/<str:booking_id>/", views.waiting_view, name="waiting_view"),
    path("confirmed/<str:booking_id>/", views.confirmed_view, name="confirmed_view"),
    path("review-trip/<str:booking_id>/", views.review_trip_view, name="review_trip_view"),
    path("history/", views.history_view, name="history_view"), 
]