from django.urls import path
from .views import AlbumListView, ContactView, add_album

urlpatterns = [
    path('albume/', AlbumListView.as_view(), name='album_list'),
    path('contact/', ContactView.as_view(), name='contact'),
    path('add-album/', add_album, name='add_album'),
]