🔹 Estrutura do Projeto da Plataforma para Feirantes
Django + Python + SQLite3

#Como rodar o projeto 

//git bash, considerando que o python já esta instalado

$ git clone https://github.com/LucianoBampa/Projeto_Feira.git

$ cd Projeto_Feira

$ pip install django

$ source venv/Scripts/Activate

$ python manage.py runserver


//no navegador, entre em 127.0.0.1:8000

1. Objetivo
Desenvolver uma plataforma web para feirantes da cidade utilizando Python/Django e SQLite3, onde:
•	Os locais das feiras sejam exibidos em um mapa interativo com dias de funcionamento
•	Cada feirante possa cadastrar e exibir produtos com fotos
•	Sistema de autenticação para feirantes autorizados
•	Subdomínios dinâmicos para cada feirante (ex: joao.feiracidade.com)
________________________________________
2. Tecnologias do Stack
Backend:
•	Python 3.9+
•	Django 4.2 (framework principal)
•	Django REST Framework (APIs para frontend)
•	SQLite3 (banco de dados)
•	Pillow (manipulação de imagens)
•	django-extensions (funcionalidades extras)
Frontend:
•	Django Templates com Bootstrap 5
•	JavaScript vanilla + Leaflet.js (mapas open source)
•	HTMX (interatividade sem complexidade do React)
Infraestrutura:
•	Cloudinary (armazenamento de imagens)
•	WhiteNoise (servir arquivos estáticos)
•	Railway/Render (deploy)
________________________________________
3. Estrutura do Banco de Dados (SQLite3)
# models.py

from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

class Feira(models.Model):
    nome = models.CharField(max_length=100)
    endereco = models.CharField(max_length=200)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    dia_funcionamento = models.CharField(max_length=20, choices=[
        ('segunda', 'Segunda-feira'),
        ('terca', 'Terça-feira'),
        ('quarta', 'Quarta-feira'),
        ('quinta', 'Quinta-feira'),
        ('sexta', 'Sexta-feira'),
        ('sabado', 'Sábado'),
        ('domingo', 'Domingo'),
    ])
    horario_inicio = models.TimeField()
    horario_fim = models.TimeField()
    ativa = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.nome} - {self.dia_funcionamento}"

class Feirante(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nome_comercial = models.CharField(max_length=100)
    subdominio = models.SlugField(max_length=50, unique=True)
    telefone = models.CharField(max_length=15)
    email_contato = models.EmailField()
    descricao = models.TextField(blank=True)
    foto_perfil = models.ImageField(upload_to='feirantes/', blank=True)
    ativo = models.BooleanField(default=False)  # Aprovação do admin
    data_cadastro = models.DateTimeField(auto_now_add=True)
    feiras = models.ManyToManyField(Feira, through='ParticipacaoFeira')
    
    def __str__(self):
        return self.nome_comercial
    
    def get_absolute_url(self):
        return reverse('feirante_loja', kwargs={'subdominio': self.subdominio})

class ParticipacaoFeira(models.Model):
    feirante = models.ForeignKey(Feirante, on_delete=models.CASCADE)
    feira = models.ForeignKey(Feira, on_delete=models.CASCADE)
    data_inicio = models.DateField()
    ativa = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['feirante', 'feira']

class CategoriaProduto(models.Model):
    nome = models.CharField(max_length=50)
    icone = models.CharField(max_length=20, default='🥬')
    
    def __str__(self):
        return self.nome

class Produto(models.Model):
    feirante = models.ForeignKey(Feirante, on_delete=models.CASCADE)
    categoria = models.ForeignKey(CategoriaProduto, on_delete=models.CASCADE)
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True)
    preco = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    unidade = models.CharField(max_length=10, default='kg')  # kg, unidade, dúzia
    foto = models.ImageField(upload_to='produtos/')
    disponivel = models.BooleanField(default=True)
    data_cadastro = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.nome} - {self.feirante.nome_comercial}"
________________________________________
4. Estrutura de URLs
# urls.py (principal)
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .views import home, mapa_feiras

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('mapa/', mapa_feiras, name='mapa'),
    path('auth/', include('django.contrib.auth.urls')),
    path('feirante/', include('feirantes.urls')),
    path('api/', include('api.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# urls.py (app feirantes)
from django.urls import path
from . import views

urlpatterns = [
    path('cadastro/', views.cadastro_feirante, name='cadastro_feirante'),
    path('painel/', views.painel_feirante, name='painel_feirante'),
    path('produtos/', views.gerenciar_produtos, name='gerenciar_produtos'),
    path('perfil/', views.editar_perfil, name='editar_perfil'),
    path('<slug:subdominio>/', views.loja_feirante, name='feirante_loja'),
]
________________________________________
5. Views Principais
# views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages
from .models import Feira, Feirante, Produto
from .forms import FeiranteForm, ProdutoForm

def home(request):
    """Página inicial com lista de feiras"""
    feiras = Feira.objects.filter(ativa=True)
    feirantes_destaque = Feirante.objects.filter(ativo=True)[:6]
    return render(request, 'home.html', {
        'feiras': feiras,
        'feirantes_destaque': feirantes_destaque
    })

def mapa_feiras(request):
    """Página do mapa interativo"""
    feiras = Feira.objects.filter(ativa=True).prefetch_related('feirante_set')
    return render(request, 'mapa.html', {'feiras': feiras})

def loja_feirante(request, subdominio):
    """Página da loja individual do feirante"""
    feirante = get_object_or_404(Feirante, subdominio=subdominio, ativo=True)
    produtos = Produto.objects.filter(feirante=feirante, disponivel=True)
    return render(request, 'loja_feirante.html', {
        'feirante': feirante,
        'produtos': produtos
    })

@login_required
def painel_feirante(request):
    """Painel administrativo do feirante"""
    try:
        feirante = request.user.feirante
    except Feirante.DoesNotExist:
        return redirect('cadastro_feirante')
    
    produtos = Produto.objects.filter(feirante=feirante)
    return render(request, 'painel/dashboard.html', {
        'feirante': feirante,
        'produtos': produtos
    })

def cadastro_feirante(request):
    """Cadastro de novos feirantes"""
    if request.method == 'POST':
        form = FeiranteForm(request.POST, request.FILES)
        if form.is_valid():
            feirante = form.save(commit=False)
            feirante.user = request.user
            feirante.save()
            messages.success(request, 'Cadastro realizado! Aguarde aprovação.')
            return redirect('painel_feirante')
    else:
        form = FeiranteForm()
    return render(request, 'cadastro_feirante.html', {'form': form})
________________________________________
6. Templates Principais
<!-- base.html -->
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Feira Cidade{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.7.1/dist/leaflet.css" />
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-success">
        <div class="container">
            <a class="navbar-brand" href="{% url 'home' %}">🍊 Feira Cidade</a>
            <div class="navbar-nav ms-auto">
                {% if user.is_authenticated %}
                    <a class="nav-link" href="{% url 'painel_feirante' %}">Meu Painel</a>
                    <a class="nav-link" href="{% url 'logout' %}">Sair</a>
                {% else %}
                    <a class="nav-link" href="{% url 'login' %}">Entrar</a>
                {% endif %}
            </div>
        </div>
    </nav>
    
    <main class="container mt-4">
        {% if messages %}
            {% for message in messages %}
                <div class="alert alert-{{ message.tags }}">{{ message }}</div>
            {% endfor %}
        {% endif %}
        
        {% block content %}{% endblock %}
    </main>
    
    <script src="https://unpkg.com/leaflet@1.7.1/dist/leaflet.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>

<!-- mapa.html -->
{% extends 'base.html' %}

{% block content %}
<h2>🗺️ Mapa das Feiras</h2>
<div id="mapa" style="height: 500px;" class="rounded"></div>

<script>
var mapa = L.map('mapa').setView([-15.7942, -47.8822], 12); // Brasília exemplo

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(mapa);

{% for feira in feiras %}
L.marker([{{ feira.latitude }}, {{ feira.longitude }}])
  .addTo(mapa)
  .bindPopup(`
    <strong>{{ feira.nome }}</strong><br>
    📍 {{ feira.endereco }}<br>
    📅 {{ feira.get_dia_funcionamento_display }}<br>
    🕐 {{ feira.horario_inicio }} - {{ feira.horario_fim }}<br>
    <small>{{ feira.feirante_set.count }} feirantes</small>
  `);
{% endfor %}
</script>
{% endblock %}
________________________________________
7. Settings Django
# settings.py
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'sua-chave-secreta-aqui'
DEBUG = True
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'feirantes',
    'rest_framework',
    'cloudinary',
    'cloudinary_storage',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Arquivos estáticos
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'feira_projeto.urls'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Configuração de mídia (fotos)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Configuração Cloudinary (opcional)
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': 'seu-cloud-name',
    'API_KEY': 'sua-api-key',
    'API_SECRET': 'seu-api-secret',
}

DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

# Configurações de autenticação
LOGIN_URL = '/auth/login/'
LOGIN_REDIRECT_URL = '/feirante/painel/'
LOGOUT_REDIRECT_URL = '/'
________________________________________
8. Comandos para Inicialização
# Criar o projeto
django-admin startproject feira_projeto
cd feira_projeto
python manage.py startapp feirantes

# Instalar dependências
pip install django pillow django-rest-framework cloudinary django-cloudinary-storage whitenoise

# Configurar banco
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser

# Executar servidor
python manage.py runserver
________________________________________
9. Funcionalidades Implementadas
✅ Mapa Interativo: Leaflet.js mostrando feiras com popups informativos ✅ Sistema de Login: Django Auth nativo ✅ Painel do Feirante: CRUD de produtos e gerenciamento de perfil ✅ Subdomínios: URLs amigáveis para cada feirante ✅ Upload de Imagens: Suporte local ou Cloudinary ✅ Banco SQLite3: Simples e funcional para desenvolvimento ✅ Responsivo: Bootstrap 5 para mobile/desktop
________________________________________
10. Extensões Futuras
•	Sistema de Avaliações: Clientes podem avaliar feirantes
•	Catálogo de Produtos: Filtros por categoria/preço
•	Notificações Push: Avisos sobre feiras/produtos
•	API REST: Integração com app mobile
•	Sistema de Pedidos: E-commerce básico
11. Justificativa Acadêmica
Impacto Social: Digitalização do comércio local, incluindo pequenos produtores Aprendizado Técnico: Full-stack com Django, mapas, autenticação, deploy Sustentabilidade: Promove economia circular e consumo consciente

