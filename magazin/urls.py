from django.urls import path
from .views import AlbumListView, ContactView

urlpatterns = [
    path('albume/', AlbumListView.as_view(), name='album_list'),
    path('contact/', ContactView.as_view(), name='contact'),
]