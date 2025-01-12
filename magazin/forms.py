# FILE: magazin/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser
from .models import Album, Artist, Gen
from datetime import date
import datetime
import re
from django.core.validators import RegexValidator

class ContactForm(forms.Form):
    TIP_MESAJ_CHOICES = [
        ('reclamatie', 'Reclamatie'),
        ('intrebare', 'Intrebare'),
        ('review', 'Review'),
        ('cerere', 'Cerere'),
        ('programare', 'Programare'),
    ]

    nume = forms.CharField(max_length=10, required=True, label="Nume")
    prenume = forms.CharField(max_length=100, required=False, label="Prenume")
    data_nasterii = forms.DateField(required=False, label="Data nașterii")
    email = forms.EmailField(required=True, label="E-mail")
    confirmare_email = forms.EmailField(required=True, label="Confirmare e-mail")
    tip_mesaj = forms.ChoiceField(choices=TIP_MESAJ_CHOICES, required=True, label="Tip mesaj")
    subiect = forms.CharField(max_length=100, required=True, label="Subiect")
    minim_zile_asteptare = forms.IntegerField(min_value=1, required=True, label="Minim zile așteptare")
    mesaj = forms.CharField(widget=forms.Textarea, required=True, label="Mesaj (semnează-te la final)")

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        confirmare_email = cleaned_data.get("confirmare_email")
        data_nasterii = cleaned_data.get("data_nasterii")
        mesaj = cleaned_data.get("mesaj")
        nume = cleaned_data.get("nume")
        prenume = cleaned_data.get("prenume")
        subiect = cleaned_data.get("subiect")

        # Validare email
        if email != confirmare_email:
            raise ValidationError("Emailul și confirmarea emailului nu coincid.")

        # Validare majorat
        if data_nasterii:
            today = date.today()
            age = today.year - data_nasterii.year - ((today.month, today.day) < (data_nasterii.month, data_nasterii.day))
            if age < 18:
                raise ValidationError("Expeditorul trebuie să fie major.")

        # Validare număr de cuvinte în mesaj
        words = re.findall(r'\b\w+\b', mesaj)
        if not (5 <= len(words) <= 100):
            raise ValidationError("Mesajul trebuie să conțină între 5 și 100 de cuvinte.")

        # Validare linkuri în mesaj
        if any(word.startswith(('http://', 'https://')) for word in words):
            raise ValidationError("Mesajul nu poate conține linkuri.")

        # Validare semnătură
        if not mesaj.strip().endswith(nume):
            raise ValidationError("Mesajul trebuie să se încheie cu numele utilizatorului (semnătura).")

        # Validare text format doar din litere și spații, începe cu literă mare
        def validate_text(text, field_name):
            if text and not re.match(r'^[A-Z][a-zA-Z\s]*$', text):
                raise ValidationError(f"{field_name} trebuie să înceapă cu literă mare și să conțină doar litere și spații.")

        validate_text(nume, "Nume")
        validate_text(prenume, "Prenume")
        validate_text(subiect, "Subiect")

        return cleaned_data

class AlbumForm(forms.ModelForm):

    class Meta:
        model = Album
        fields = ['titlu', 'pret', 'artist', 'gen', 'imagine', 'data_lansare']
        labels = {
            'titlu': 'Titlu Album',
            'pret': 'Preț',
            'artist': 'Artist',
            'gen': 'Gen',
            'imagine': 'Imagine Album',
            'data_lansare': 'Data Lansării'
        }
        help_texts = {
            'titlu': 'Introduceți titlul albumului',
        }
        error_messages = {
            'titlu': {
                'required': 'Titlul este obligatoriu',
            },
            'pret': {
                'required': 'Prețul este obligatoriu',
                'invalid': 'Introduceți un preț valid',
            },
            'imagine': {
                'required': 'Imaginea este obligatorie',
            },
            'data_lansare': {
                'required': 'Data lansării este obligatorie',
            },
        }

    def clean_pret(self):
        pret = self.cleaned_data.get('pret')
        if pret <= 0:
            raise forms.ValidationError('Prețul trebuie să fie mai mare de 0')
        return pret

    def clean(self):
        cleaned_data = super().clean()
        additional_field_1 = cleaned_data.get('additional_field_1')
        additional_field_2 = cleaned_data.get('additional_field_2')

        # Exemplu de validare care implică două câmpuri
        if additional_field_1 and additional_field_2:
            if additional_field_1 == additional_field_2:
                raise forms.ValidationError('Câmpurile adiționale nu pot fi identice')

        return cleaned_data

    def save(self, commit=True):
        album = super().save(commit=False)
        # Procesare date din câmpurile adiționale
        album.some_field = self.cleaned_data['additional_field_1'] + self.cleaned_data['additional_field_2']
        if commit:
            album.save()
        return album
    
class CustomUserCreationForm(UserCreationForm):
    username = forms.CharField(
        max_length=150,
        validators=[
            RegexValidator(
                regex='^[\w\s@.+-]*$',
                message='Username-ul poate conține litere, numere, spații și caracterele @.+-',
                code='invalid_username'
            ),
        ]
    )
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'phone_number', 'address', 'birth_date', 'profile_picture', 'bio', 'password1', 'password2']

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if not phone_number.isdigit():
            raise forms.ValidationError('Numărul de telefon trebuie să conțină doar cifre.')
        return phone_number

    def clean_birth_date(self):
        birth_date = self.cleaned_data.get('birth_date')
        if birth_date and birth_date > datetime.date.today():
            raise forms.ValidationError('Data nașterii nu poate fi în viitor.')
        return birth_date

    def clean_address(self):
        address = self.cleaned_data.get('address')
        if len(address) < 10:
            raise forms.ValidationError('Adresa trebuie să conțină cel puțin 10 caractere.')
        return address
    
class CustomAuthenticationForm(AuthenticationForm):
    remember_me = forms.BooleanField(required=False, label='Ține-mă minte')