from django.db import models

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
    cantitate = models.IntegerField()
    locatie_depozit = models.CharField(max_length=200)
    ultima_actualizare = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.tip_produs} - {self.produs_id} ({self.cantitate})"

    class Meta:
        verbose_name_plural = "Stocuri"