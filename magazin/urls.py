from django.urls import path
from django.contrib.auth import views as auth_views
from .views import (
    AlbumListView, 
    InstrumentListView,
    ContactView, 
    add_album, 
    register, 
    custom_login, 
    custom_logout, 
    profile,
    oferta,
    add_oferta_permission,
    cart_view,
    add_to_cart,
    remove_from_cart,
    update_cart_quantity,
)

urlpatterns = [
    path('albume/', AlbumListView.as_view(), name='album_list'),
    path('instrumente/', InstrumentListView.as_view(), name='instrument_list'),
    path('contact/', ContactView.as_view(), name='contact'),
    path('add-album/', add_album, name='add_album'),
    path('register/', register, name='register'),
    path('login/', custom_login, name='login'),
    path('logout/', custom_logout, name='logout'),
    path('profile/', profile, name='profile'),
    path('password_change/', auth_views.PasswordChangeView.as_view(template_name='magazin/password_change.html'), name='password_change'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(template_name='magazin/password_change_done.html'), name='password_change_done'),
    path('oferta/', oferta, name='oferta'),
    path('add-oferta-permission/', add_oferta_permission, name='add_oferta_permission'),
    path('cart/', cart_view, name='cart'),
    path('cart/add/', add_to_cart, name='add_to_cart'),
    path('cart/remove/', remove_from_cart, name='remove_from_cart'),
    path('cart/update/', update_cart_quantity, name='update_cart_quantity'),
]