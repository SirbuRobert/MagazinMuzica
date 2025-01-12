from django.views.generic import ListView
from django.db.models import Q
from .models import Album, Artist, Gen
from django.views.generic import FormView
from django.urls import reverse_lazy
from django.utils import timezone
from datetime import date
import json
import os
import re
from .forms import ContactForm

class ContactView(FormView):
    template_name = 'magazin/contact.html'
    form_class = ContactForm
    success_url = reverse_lazy('contact')

    def form_valid(self, form):
        data = form.cleaned_data
        data.pop('confirmare_email')  # Eliminăm confirmarea emailului

        # Calculăm vârsta în ani și luni
        if data['data_nasterii']:
            today = date.today()
            birth_date = data['data_nasterii']
            age_years = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
            age_months = (today.month - birth_date.month) % 12
            data['varsta'] = f"{age_years} ani și {age_months} luni"
            data.pop('data_nasterii')

        # Preprocesăm mesajul
        mesaj = data['mesaj']
        mesaj = re.sub(r'\s+', ' ', mesaj.replace('\n', ' '))
        data['mesaj'] = mesaj

        # Salvăm datele într-un fișier JSON
        timestamp = int(timezone.now().timestamp())
        file_name = f"mesaj_{timestamp}.json"
        file_path = os.path.join('magazin', 'mesaje', file_name)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

        return super().form_valid(form)

class AlbumListView(ListView):
    model = Album
    template_name = 'magazin/album_list.html'
    context_object_name = 'albume'
    paginate_by = 10  # Numărul de produse pe pagină
    
    def get_queryset(self):
        queryset = Album.objects.all()
        
        # Filtrare după titlu
        titlu = self.request.GET.get('titlu')
        if titlu:
            queryset = queryset.filter(titlu__icontains=titlu)
            
        # Filtrare după artist
        artist = self.request.GET.get('artist')
        if artist:
            queryset = queryset.filter(artist__nume__icontains=artist)
            
        # Filtrare după preț
        pret_min = self.request.GET.get('pret_min')
        pret_max = self.request.GET.get('pret_max')
        if pret_min:
            queryset = queryset.filter(pret__gte=pret_min)
        if pret_max:
            queryset = queryset.filter(pret__lte=pret_max)
            
        # Filtrare după gen
        gen = self.request.GET.get('gen')
        if gen:
            queryset = queryset.filter(gen__nume__icontains=gen)
            
        # Filtrare după data lansării
        data_min = self.request.GET.get('data_min')
        data_max = self.request.GET.get('data_max')
        if data_min:
            queryset = queryset.filter(data_lansare__gte=data_min)
        if data_max:
            queryset = queryset.filter(data_lansare__lte=data_max)
            
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['genuri'] = Gen.objects.all()
        context['artisti'] = Artist.objects.all()
        context['current_filters'] = self.request.GET
        return context