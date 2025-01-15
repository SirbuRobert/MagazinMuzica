from django.contrib import admin
from .models import Album, Artist, Gen, Melodie, Instrument, Accesoriu, Stoc
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Informații de bază', {
            'fields': ('titlu', 'artist', 'data_lansare', 'gen')
        }),
        ('Detalii comerciale', {
            'fields': ('pret', 'descriere', 'imagine')
        }),
    )
    search_fields = ['titlu', 'artist__nume']
    list_filter = ('data_lansare', 'artist', 'gen')
    list_display = ('id', 'titlu', 'artist', 'data_lansare', 'pret')

@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Informații principale', {
            'fields': ('nume', 'biografie')
        }),
        ('Detalii suplimentare', {
            'fields': ('tara', 'an_formare')
        }),
    )
    search_fields = ['nume', 'tara']
    list_filter = ('tara', 'an_formare')
    list_display = ('nume', 'tara', 'an_formare')

@admin.register(Gen)
class GenAdmin(admin.ModelAdmin):
    search_fields = ['nume']
    list_display = ('nume', 'descriere')

@admin.register(Melodie)
class MelodieAdmin(admin.ModelAdmin):
    search_fields = ['titlu', 'album__titlu']
    list_filter = ('album', 'durata')
    list_display = ('titlu', 'album', 'durata', 'pret')

@admin.register(Instrument)
class InstrumentAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Informații produs', {
            'fields': ('nume', 'marca', 'pret')
        }),
        ('Detalii tehnice', {
            'fields': ('descriere', 'stare')
        }),
    )
    search_fields = ['nume', 'marca']
    list_filter = ('marca', 'stare')
    list_display = ('nume', 'marca', 'pret', 'stare')

@admin.register(Accesoriu)
class AccesoriuAdmin(admin.ModelAdmin):
    search_fields = ['nume']
    list_filter = ('compatibilitate',)
    list_display = ('nume', 'pret', 'compatibilitate')

@admin.register(Stoc)
class StocAdmin(admin.ModelAdmin):
    search_fields = ['produs_id', 'locatie_depozit']
    list_filter = ('tip_produs', 'locatie_depozit')
    list_display = ('tip_produs', 'cantitate', 'locatie_depozit', 'ultima_actualizare')

class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('phone_number', 'address', 'birth_date', 'profile_picture', 'bio')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('phone_number', 'address', 'birth_date', 'profile_picture', 'bio')}),
    )

admin.site.register(CustomUser, CustomUserAdmin)

# Personalizare pagină admin
admin.site.site_header = "Administrare Magazin de Muzică"
admin.site.site_title = "Portal Admin"
admin.site.index_title = "Panoul de Administrare"