"""URLs for network app"""
# got help from this tutorial to configure importing avatar:
# https://gist.github.com/prodeveloper/7342dc1d3be6256c46a71730ce548db5

from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from . import views


urlpatterns = [
    # default index page
    path("", views.index, name="index"),
    # index with specific page num
    path("<int:pnum>", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    # default profile page
    path("profile/<str:name>", views.profile, name="profile"),
    # profile page with specific page num
    path("profile/<str:name>/<int:pnum>", views.profile, name="profile"),
    path("editprofile", views.editprofile, name="editprofile"),
    path("post", views.post, name="post"),
    # default following page
    path("following", views.following, name="following"),
    # following page with specific page num
    path("following/<int:pnum>", views.following, name="following"),

    # API routes
    path("follow/<str:name>", views.follow, name="follow"),
    path("like/<int:pk>", views.like, name="like"),
    path("update/<int:pk>", views.update, name="update")
]

# configuration to save user pictures
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
