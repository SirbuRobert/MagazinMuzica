from django.urls import path
from .views import AlbumListView, ContactView, add_album, register, custom_login, custom_logout, profile
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('albume/', AlbumListView.as_view(), name='album_list'),
    path('contact/', ContactView.as_view(), name='contact'),
    path('add-album/', add_album, name='add_album'),
    path('register/', register, name='register'),
    path('login/', custom_login, name='login'),
    path('logout/', custom_logout, name='logout'),
    path('profile/', profile, name='profile'),
    path('password_change/', auth_views.PasswordChangeView.as_view(template_name='magazin/password_change.html'), name='password_change'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(template_name='magazin/password_change_done.html'), name='password_change_done'),
]