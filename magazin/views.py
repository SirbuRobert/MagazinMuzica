from django.views.generic import ListView
from django.db.models import Q, Subquery, OuterRef
from .models import Album, Artist, Gen, Instrument, Stoc, CustomUser
from django.views.generic import FormView
from django.urls import reverse_lazy
from django.utils import timezone
from datetime import date
import json
import os
import re
from .forms import ContactForm
from django.shortcuts import render, redirect
from .forms import AlbumForm
from django.contrib.auth import login, logout, authenticate
from .forms import CustomUserCreationForm, CustomAuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.template.loader import render_to_string
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db.models import F
import json

@require_http_methods(["POST"])
def add_to_cart(request):
    data = json.loads(request.body)
    product_id = data.get('product_id')
    product_type = data.get('product_type')
    quantity = data.get('quantity', 1)

    try:
        if product_type == 'album':
            product = Album.objects.get(id=product_id)
        elif product_type == 'instrument':
            product = Instrument.objects.get(id=product_id)
        else:
            return JsonResponse({
                'success': False,
                'message': 'Tip de produs invalid'
            })

        stoc = Stoc.objects.get(
            produs_id=product_id,
            tip_produs=product_type
        )

        if stoc.cantitate >= quantity:
            return JsonResponse({
                'success': True,
                'product_name': product.titlu if hasattr(product, 'titlu') else product.nume,
                'product_price': float(product.pret),
                'stock_count': stoc.cantitate
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Stoc insuficient'
            })
    except (Album.DoesNotExist, Instrument.DoesNotExist, Stoc.DoesNotExist):
        return JsonResponse({
            'success': False,
            'message': 'Produsul nu există'
        })

@require_http_methods(["GET"])
def cart_view(request):
    return render(request, 'magazin/cart.html')

@require_http_methods(["POST"])
def remove_from_cart(request):
    data = json.loads(request.body)
    return JsonResponse({'success': True})

@require_http_methods(["POST"])
def update_cart_quantity(request):
    data = json.loads(request.body)
    product_id = data.get('product_id')
    product_type = data.get('product_type')
    quantity = data.get('quantity', 1)

    stoc = Stoc.objects.filter(
        produs_id=product_id, 
        tip_produs=product_type
    ).first()

    if not stoc or stoc.cantitate < quantity:
        return JsonResponse({
            'success': False,
            'message': 'Cantitate solicitată indisponibilă',
            'available_quantity': stoc.cantitate if stoc else 0
        }, status=400)

    return JsonResponse({
        'success': True,
        'stock_count': stoc.cantitate
    })

def oferta(request):
    if not request.user.has_perm('magazin.vizualizeaza_oferta'):
        context = {
            'titlu': 'Eroare afisare oferta',
            'mesaj_personalizat': 'Nu ai voie să vizualizezi oferta'
        }
        return HttpResponseForbidden(
            render_to_string('magazin/403.html', context, request)
        )
    return render(request, 'magazin/oferta.html')

def add_oferta_permission(request):
    if request.user.is_authenticated:
        content_type = ContentType.objects.get_for_model(CustomUser)
        permission = Permission.objects.get(
            codename='vizualizeaza_oferta',
            content_type=content_type,
        )
        request.user.user_permissions.add(permission)
        request.user.save()
    return redirect('oferta')

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Parola a fost schimbată cu succes!')
            return redirect('profile')
        else:
            messages.error(request, 'Vă rugăm să corectați erorile de mai jos.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'magazin/password_change.html', {
        'form': form
    })

@login_required
def profile(request):
    if request.method == 'POST':
        password_form = PasswordChangeForm(request.user, request.POST)
        if password_form.is_valid():
            user = password_form.save()
            # Actualizăm sesiunea pentru a nu deconecta utilizatorul
            update_session_auth_hash(request, user)
            messages.success(request, 'Parola a fost schimbată cu succes!')
            return redirect('profile')
    else:
        password_form = PasswordChangeForm(request.user)
    
    context = {
        'user': request.user,
        'password_form': password_form
    }
    return render(request, 'magazin/profile.html', context)

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'magazin/register.html', {'form': form})

def custom_login(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            if form.cleaned_data.get('remember_me'):
                request.session.set_expiry(86400)  # 1 day
            else:
                request.session.set_expiry(0)
            return redirect('profile')
    else:
        form = CustomAuthenticationForm()
    return render(request, 'magazin/login.html', {'form': form})

def custom_logout(request):
    logout(request)
    return redirect('login')

def profile(request):
    return render(request, 'magazin/profile.html')

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

class InstrumentListView(ListView):
    model = Instrument 
    template_name = 'magazin/instrument_list.html'
    context_object_name = 'instrumente'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        nume = self.request.GET.get('nume')
        marca = self.request.GET.get('marca')
        pret_min = self.request.GET.get('pret_min')
        pret_max = self.request.GET.get('pret_max')
        stare = self.request.GET.get('stare')

        if nume:
            queryset = queryset.filter(nume__icontains=nume)
        if marca:
            queryset = queryset.filter(marca__icontains=marca)
        if pret_min:
            queryset = queryset.filter(pret__gte=pret_min)
        if pret_max:
            queryset = queryset.filter(pret__lte=pret_max)
        if stare:
            queryset = queryset.filter(stare=stare)

        # Adăugăm informații despre stoc
        queryset = queryset.annotate(
            stoc_cantitate=Subquery(
                Stoc.objects.filter(
                    tip_produs='instrument',
                    produs_id=OuterRef('id')
                ).values('cantitate')[:1]
            )
        )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['marci'] = Instrument.objects.values_list('marca', flat=True).distinct()
        context['stari'] = Instrument.objects.values_list('stare', flat=True).distinct()
        context['current_filters'] = self.request.GET
        return context

class AlbumListView(ListView):
    model = Album
    template_name = 'magazin/album_list.html'
    context_object_name = 'albume'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = super().get_queryset()
        titlu = self.request.GET.get('titlu')
        artist = self.request.GET.get('artist')
        gen = self.request.GET.get('gen')
        pret_min = self.request.GET.get('pret_min')
        pret_max = self.request.GET.get('pret_max')
        data_min = self.request.GET.get('data_min')
        data_max = self.request.GET.get('data_max')

        if titlu:
            queryset = queryset.filter(titlu__icontains=titlu)
        if artist:
            queryset = queryset.filter(artist_id=artist)
        if gen:
            queryset = queryset.filter(gen__id=gen)
        if pret_min:
            queryset = queryset.filter(pret__gte=pret_min)
        if pret_max:
            queryset = queryset.filter(pret__lte=pret_max)
        if data_min:
            queryset = queryset.filter(data_lansare__gte=data_min)
        if data_max:
            queryset = queryset.filter(data_lansare__lte=data_max)

        # Adăugăm informații despre stoc pentru albume
        queryset = queryset.annotate(
            stoc_cantitate=Subquery(
                Stoc.objects.filter(
                    tip_produs='album',
                    produs_id=OuterRef('id')
                ).values('cantitate')[:1]
            )
        )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['genuri'] = Gen.objects.all()
        context['artisti'] = Artist.objects.all()
        context['current_filters'] = self.request.GET
        return context

def add_album(request):
    if not request.user.groups.filter(name='Administratori_produse').exists():
        context = {
            'titlu': 'Eroare adaugare produse',
            'mesaj_personalizat': 'Nu ai voie să adaugi albume'
        }
        return HttpResponseForbidden(
            render_to_string('magazin/403.html', context, request)
        )
        
    if request.method == 'POST':
        form = AlbumForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('album_list')
    else:
        form = AlbumForm()
    return render(request, 'magazin/add_album.html', {'form': form})