🔹 Estrutura do Projeto da Plataforma para Feirantes
Django + Python + SQLite3

#Como rodar o projeto 

//git bash, considerando que o python já esta instalado

$ git clone https://github.com/LucianoBampa/Projeto_Feira.git

$ cd Projeto_Feira

$ python.exe -m pip install --upgrade pip

$ python -m venv venv

$ source venv/Scripts/Activate

$ pip install -r requirements.txt

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
from django.contrib.auth.decorators import login_required
from django.contrib.auth import views as auth_views
from django.urls import path, reverse_lazy
from . import views

app_name = 'feirantes'

urlpatterns = [
    # URLs PÚBLICAS
    path('', views.listar_feirantes, name='listar'),
    path('mapa/', views.mapa_feiras, name='mapa'),
    path('loja/<slug:subdominio>/feiras/',
         views.mapa_feiras_feirante, name='mapa_feiras_feirante'),
    path('feiras/', views.listar_feiras, name='lista_feiras'),
    path('buscar/', views.buscar, name='buscar'),
    path('loja/<slug:subdominio>/', views.loja_feirante, name='loja_feirante'),
    path('feira/<int:pk>/', views.detalhe_feira, name='detalhe_feira'),
    path('cadastro/', views.cadastro_feirante, name='cadastro'),
    path('feirante/<int:feirante_id>/avaliar/',
         views.avaliar_feirante, name='avaliar_feirante'),

    # Recuperação de senha
    path(
        'senha/redefinir/',
        auth_views.PasswordResetView.as_view(
            template_name='registration/senha_redefinir_formulario.html',
            email_template_name='registration/senha_redefinir_email.html',
            subject_template_name='registration/senha_redefinir_assunto.txt',
            success_url=reverse_lazy('feirantes:password_reset_done')
        ),
        name='password_reset'
    ),
    path(
        'senha/redefinir/enviado/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='registration/senha_redefinir_enviado.html'
        ),
        name='password_reset_done'
    ),
    path(
        'senha/redefinir/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='registration/senha_redefinir_confirmar.html',
            success_url=reverse_lazy('feirantes:password_reset_complete')
        ),
        name='password_reset_confirm'
    ),
    path(
        'senha/redefinir/concluido/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='registration/senha_redefinir_completa.html'
        ),
        name='password_reset_complete'
    ),

    # Login e Logout
    path(
        'login/',
        auth_views.LoginView.as_view(template_name='registration/login.html'),
        name='login'
    ),
    path(
        'logout/',
        auth_views.LogoutView.as_view(next_page='feirantes:login'),
        name='logout'
    ),

    # URLs PROTEGIDAS
    path('painel/', login_required(views.painel_feirante,
         login_url='feirantes:login'), name='painel'),
    path('painel/editar-perfil/', login_required(views.editar_perfil,
         login_url='feirantes:login'), name='editar_perfil'),
    path('painel/produtos/', login_required(views.gerenciar_produtos,
         login_url='feirantes:login'), name='produtos'),
    path('painel/produtos/novo/', login_required(views.criar_produto,
         login_url='feirantes:login'), name='novo_produto'),
    path('painel/produtos/<int:pk>/editar/', login_required(
        views.editar_produto,
         login_url='feirantes:login'), name='editar_produto'),
    path('painel/produtos/<int:pk>/excluir/', login_required(
        views.excluir_produto,
         login_url='feirantes:login'), name='excluir_produto'),
    path('painel/minhas-feiras/', login_required(views.minhas_feiras,
         login_url='feirantes:login'), name='minhas_feiras'),
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
"""
Django settings for project project.

Generated by 'django-admin startproject' using Django 4.2.23.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

from django.contrib.messages import constants as messages
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-fo!o%8+ltx@p00jaumyx0o+lm8b_n%ryqw9=*wwi4^0kk3*_'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'widget_tweaks',
    'feirantes',    
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'templates'
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'project.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME':
        'django.contrib.auth.password_validation.'
        'UserAttributeSimilarityValidator',
    },
    {
        'NAME':
        'django.contrib.auth.password_validation.'
        'MinimumLengthValidator',
        'OPTIONS': {'min_length': 8},
    },
    {
        'NAME':
        'django.contrib.auth.password_validation.'
        'CommonPasswordValidator',
    },
    {
        'NAME':
        'django.contrib.auth.password_validation.'
        'NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/
LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_L10N = True
USE_I18N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/
STATIC_URL = 'static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Configuração para arquivos de mídia (fotos dos produtos)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Configurações de autenticação
LOGIN_URL = 'feirantes:login'
LOGOUT_REDIRECT_URL = '/'
LOGIN_REDIRECT_URL = 'feirantes:painel'


ACCOUNT_LOGOUT_REDIRECT_URL = '/'

# Configurações de mensagens (Bootstrap classes)
MESSAGE_TAGS = {
    messages.DEBUG: 'alert-secondary',
    messages.INFO: 'alert-info',
    messages.SUCCESS: 'alert-success',
    messages.WARNING: 'alert-warning',
    messages.ERROR: 'alert-danger',
}

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Configurações específicas para upload de arquivos
FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB

# Configuração do backend de email para desenvolvimento
# Durante o desenvolvimento, os emails serão impressos no console
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

________________________________________
8. Comandos para Inicialização
# Criar o projeto
django-admin startproject feira_projeto
cd feira_projeto
python manage.py startapp feirantes

# Instalar dependências
pip install --upgrade pip
pip install -r requirements.txt

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
10. Extensões    
•	Sistema de Avaliações: Clientes podem avaliar feirantes
•	Sistema de Aizualiações: A cada visita ao feirante uma visualização é contada 
•	Catálogo de Produtos: Com o modo CRUD
•	API REST: Integração com app mobile
________________________________________
11. Justificativa Acadêmica
Impacto Social: Digitalização do comércio local, incluindo pequenos produtores Aprendizado Técnico: Full-stack com Django, mapas, autenticação, deploy Sustentabilidade: Promove economia circular e consumo consciente

