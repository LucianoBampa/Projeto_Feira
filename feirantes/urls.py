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

    # Termos de uso e política de privacidade
    path('termos-uso/', views.termos_uso, name='termos_uso'),
    path('politica-privacidade/', views.politica_privacidade,
         name='politica_privacidade'),

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
        views.CustomPasswordResetConfirmView.as_view(
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
