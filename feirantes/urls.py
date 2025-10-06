from django.contrib.auth.decorators import login_required
from django.urls import path
from . import views

app_name = 'feirantes'

urlpatterns = [
    # URLs PÚBLICAS (acesso livre)
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


    # URLs PROTEGIDAS (requerem login)
    path('painel/', login_required(views.painel_feirante), name='painel'),
    path('painel/editar-perfil/',
         login_required(views.editar_perfil), name='editar_perfil'),
    path('painel/produtos/',
         login_required(views.gerenciar_produtos), name='produtos'),
    path('painel/produtos/novo/',
         login_required(views.criar_produto), name='novo_produto'),
    path('painel/produtos/<int:pk>/editar/',
         login_required(views.editar_produto), name='editar_produto'),
    path('painel/produtos/<int:pk>/excluir/',
         login_required(views.excluir_produto), name='excluir_produto'),
    path('painel/minhas-feiras/',
         login_required(views.minhas_feiras), name='minhas_feiras'),
]
