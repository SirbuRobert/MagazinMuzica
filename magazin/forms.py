# FILE: magazin/forms.py
from django import forms
from django.core.exceptions import ValidationError
from datetime import date
import re

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