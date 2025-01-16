from django.contrib.auth.models import AbstractUser, Permission
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.contrib.auth.signals import user_logged_out
from django.dispatch import receiver

@receiver(user_logged_out)
def remove_oferta_permission(sender, user, request, **kwargs):
    if user.has_perm('magazin.vizualizeaza_oferta'):
        content_type = ContentType.objects.get_for_model(CustomUser)
        permission = Permission.objects.get(
            codename='vizualizeaza_oferta',
            content_type=content_type,
        )
        user.user_permissions.remove(permission)
        user.save()

class CustomUser(AbstractUser):
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    
    class Meta:
        permissions = [
            ("vizualizeaza_oferta", "Poate vizualiza ofertele speciale"),
        ]

    def __str__(self):
        return self.username

class Artist(models.Model):
    nume = models.CharField(max_length=200)
    biografie = models.TextField()
    tara = models.CharField(max_length=100)
    an_formare = models.IntegerField()

    def __str__(self):
        return self.nume

    class Meta:
        verbose_name_plural = "Artiști"

class Gen(models.Model):
    nume = models.CharField(max_length=100)
    descriere = models.TextField()

    def __str__(self):
        return self.nume

    class Meta:
        verbose_name_plural = "Genuri"

class Album(models.Model):
    titlu = models.CharField(max_length=200)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)
    data_lansare = models.DateField()
    pret = models.DecimalField(max_digits=10, decimal_places=2)
    descriere = models.TextField()
    imagine = models.ImageField(upload_to='albume/', blank=True, null=True)
    gen = models.ManyToManyField(Gen)

    def __str__(self):
        return f"{self.titlu} - {self.artist}"

    class Meta:
        verbose_name_plural = "Albume"

class Melodie(models.Model):
    titlu = models.CharField(max_length=200)
    album = models.ForeignKey(Album, on_delete=models.CASCADE)
    durata = models.DurationField()
    pret = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.titlu

    class Meta:
        verbose_name_plural = "Melodii"

class Instrument(models.Model):
    nume = models.CharField(max_length=200)
    marca = models.CharField(max_length=100)
    pret = models.DecimalField(max_digits=10, decimal_places=2)
    descriere = models.TextField()
    stare = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.marca} {self.nume}"

    class Meta:
        verbose_name_plural = "Instrumente"

class Accesoriu(models.Model):
    nume = models.CharField(max_length=200)
    pret = models.DecimalField(max_digits=10, decimal_places=2)
    descriere = models.TextField()
    compatibilitate = models.CharField(max_length=200)

    def __str__(self):
        return self.nume

    class Meta:
        verbose_name_plural = "Accesorii"

class Stoc(models.Model):
    TIPURI_PRODUSE = [
        ('album', 'Album'),
        ('instrument', 'Instrument'),
        ('accesoriu', 'Accesoriu'),
    ]
    
    produs_id = models.IntegerField()
    tip_produs = models.CharField(max_length=50, choices=TIPURI_PRODUSE)
    cantitate = models.IntegerField(default=0)
    locatie_depozit = models.CharField(max_length=200)
    ultima_actualizare = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Stocuri"
        indexes = [
            models.Index(fields=['tip_produs', 'produs_id']),
        ]

    def get_produs(self):
        if self.tip_produs == 'album':
            return Album.objects.get(id=self.produs_id)
        elif self.tip_produs == 'instrument':
            return Instrument.objects.get(id=self.produs_id)
        elif self.tip_produs == 'accesoriu':
            return Accesoriu.objects.get(id=self.produs_id)
        return None
