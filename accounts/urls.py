from django.urls import path

from .views import SignUpView, login_me_in

urlpatterns = [
    path("signup/", SignUpView, name="signup"),
    path("signin",login_me_in,name='signin')
]