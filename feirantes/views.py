import json
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import FeiranteForm, ProdutoForm, CadastroFeiranteForm
from .forms import AvaliacaoForm
from django.contrib.auth.models import User
from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth.password_validation import (
    password_validators_help_texts,
    validate_password,
)
from django.db import transaction
from django.db.models import F, Avg
from django.utils.text import slugify
from django.urls import reverse
from .models import Feira, Feirante, Produto, Avaliacao
from django.http import HttpResponseForbidden
from validate_docbr import CPF
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.exceptions import ValidationError
from django.contrib.auth.views import PasswordResetConfirmView


def listar_feirantes(request):
    """Lista todos os feirantes ativos"""
    feirantes = Feirante.objects.filter(ativo=True).order_by('nome_comercial')
    paginator = Paginator(feirantes, 6)
    page_number = request.GET.get('page')
    feirantes = paginator.get_page(page_number)
    return render(request, 'feirantes/lista.html', {
        'feirantes': feirantes
    })


def mapa_feiras(request):
    """Exibe o mapa com as feiras usando JSON"""
    feiras = Feira.objects.filter(ativa=True).prefetch_related('feirantes')
    feiras_data = []

    for feira in feiras:
        if feira.latitude is not None and feira.longitude is not None:
            try:
                lat = float(str(feira.latitude).replace(',', '.'))
                lng = float(str(feira.longitude).replace(',', '.'))
            except (ValueError, TypeError):
                continue

            feiras_data.append({
                'nome': feira.nome,
                'endereco': feira.endereco,
                'cidade': feira.cidade,
                'estado': feira.estado,
                'horario': feira.horario_funcionamento,
                'dias': feira.get_dias_funcionamento_display(),
                'latitude': lat,
                'longitude': lng,
                'feirantes_count': feira.feirantes.count(),  # type: ignore
                'url': reverse('feirantes:detalhe_feira', args=[feira.pk])
            })

    return render(request, 'feirantes/mapa.html', {
        'feiras_json': json.dumps(feiras_data)
    })


def mapa_feiras_feirante(request, subdominio):
    """Mapa mostrando apenas as feiras onde um feirante específico atua"""
    feirante = get_object_or_404(Feirante, subdominio=subdominio, ativo=True)
    feiras = feirante.feiras.filter(ativa=True)

    feiras_data = []
    for feira in feiras:
        if feira.latitude is not None and feira.longitude is not None:
            try:
                lat = float(str(feira.latitude).replace(',', '.'))
                lng = float(str(feira.longitude).replace(',', '.'))

                feiras_data.append({
                    'nome': feira.nome,
                    'endereco': feira.endereco,
                    'cidade': feira.cidade,
                    'estado': feira.estado,
                    'horario': feira.horario_funcionamento,
                    'dias': feira.get_dias_funcionamento_display(),
                    'latitude': lat,
                    'longitude': lng,
                    'feirantes_count': feira.feirantes.count(),
                    'url': reverse('feirantes:detalhe_feira', args=[feira.id])
                })
            except (ValueError, TypeError):
                continue

    return render(request, 'feirantes/mapa_feiras_feirante.html', {
        'feiras_json': json.dumps(feiras_data),
        'feirante': feirante,
        'feiras': feiras
    })


def listar_feiras(request):
    """Lista todas as feiras ativas com seus feirantes"""
    feiras = Feira.objects.filter(ativa=True).prefetch_related(
        'feirantes').order_by('nome')
    return render(request, 'feirantes/lista_feiras.html', {'feiras': feiras})


def buscar(request):
    """Busca feirantes e produtos"""
    query = request.GET.get('q', '')
    feirantes = []
    produtos = []

    if query:
        feirantes = Feirante.objects.filter(
            nome_comercial__icontains=query, ativo=True
        )
        produtos = Produto.objects.filter(
            nome__icontains=query, disponivel=True, feirante__ativo=True
        )

    return render(request, 'feirantes/busca.html', {
        'query': query,
        'feirantes': feirantes,
        'produtos': produtos
    })


def loja_feirante(request, subdominio):
    feirante: Feirante = get_object_or_404(
        Feirante, subdominio=subdominio, ativo=True
    )
    produtos = Produto.objects.filter(
        feirante=feirante, disponivel=True
    ).select_related('categoria')

    viewed_key = f"viewed_feirante_{feirante.id}"  # type: ignore
    if viewed_key not in request.session:
        if (
            not request.user.is_authenticated
            or not hasattr(request.user, 'feirante')
            or request.user.feirante.id != feirante.id  # type: ignore
        ):
            Feirante.objects.filter(subdominio=subdominio).update(
                views=F('views') + 1
            )
            request.session[viewed_key] = True  # Marca como visualizado

    return render(request, 'feirantes/loja.html', {
        'feirante': feirante,
        'produtos': produtos
    })


def cadastro_feirante(request):
    """Página de cadastro de feirantes"""
    if request.user.is_authenticated:
        return redirect('feirantes:listar')

    if request.method == 'POST':
        form = CadastroFeiranteForm(request.POST)
        if form.is_valid():
            try:
                nome_completo = form.cleaned_data['nome_completo']
                nome_comercial = form.cleaned_data['nome_comercial']
                cpf = form.cleaned_data['cpf']
                email = form.cleaned_data['email']
                telefone = form.cleaned_data['telefone']
                senha = form.cleaned_data['senha']
                descricao = form.cleaned_data.get('descricao', '')

                # O formulário já validou o CPF, então podemos usar diretamente
                cpf_validator = CPF()
                cpf_limpo = ''.join(filter(str.isdigit, cpf))
                cpf_formatado = cpf_validator.mask(cpf_limpo)

                if Feirante.objects.filter(cpf=cpf_formatado).exists():
                    messages.error(request, 'Este CPF já está cadastrado.')
                    return render(
                        request, 'feirantes/cadastro.html', {
                            'form': form,
                            'password_validators_help_texts':
                            password_validators_help_texts
                        })

                if User.objects.filter(email=email).exists():
                    messages.error(request, 'Este e-mail já está cadastrado.')
                    return render(
                        request, 'feirantes/cadastro.html', {
                            'form': form,
                            'password_validators_help_texts':
                                password_validators_help_texts
                        })

                subdominio_base = slugify(nome_comercial)
                subdominio = subdominio_base
                contador = 1
                while Feirante.objects.filter(subdominio=subdominio).exists():
                    subdominio = f"{subdominio_base}-{contador}"
                    contador += 1

                with transaction.atomic():
                    user = User.objects.create_user(
                        username=email,
                        email=email,
                        password=senha,
                        first_name=(nome_completo.split()[
                                    0] if nome_completo else ''),
                        last_name=(' '.join(nome_comercial.split()[1:]) if len(
                            nome_comercial.split()) > 1 else '')
                    )

                    Feirante.objects.create(
                        usuario=user,
                        nome_comercial=nome_comercial,
                        cpf=cpf_formatado,
                        telefone=telefone,
                        email=email,
                        descricao=descricao,
                        subdominio=subdominio,
                        ativo=True
                    )

                login(request, user)
                messages.success(
                    request,
                    f'Cadastro realizado com sucesso! \
                        Bem-vindo, {nome_comercial}!')
                return redirect('feirantes:painel')

            except Exception as e:
                messages.error(request, f'Erro ao criar cadastro: {str(e)}')
                return render(
                    request, 'feirantes/cadastro.html', {
                        'form': form,
                        'password_validators_help_texts':
                            password_validators_help_texts
                    })
        else:
            # Se o formulário não for válido, renderize com os erros
            return render(request, 'feirantes/cadastro.html', {
                'form': form,
                'password_validators_help_texts':
                    password_validators_help_texts})
    else:
        form = CadastroFeiranteForm()

    return render(request, 'feirantes/cadastro.html', {
        'form': form,
        'password_validators_help_texts': password_validators_help_texts})


def detalhe_feira(request, pk):
    """Mostra os detalhes de uma feira e seus feirantes"""
    feira = get_object_or_404(Feira, pk=pk, ativa=True)
    feirantes = feira.feirantes.filter(ativo=True)  # type: ignore
    return render(request, 'feirantes/detalhe_feira.html', {
        'feira': feira,
        'feirantes': feirantes
    })


def avaliar_feirante(request, feirante_id):
    feirante = get_object_or_404(Feirante, pk=feirante_id)

    # Bloqueia autoavaliação
    if request.user.is_authenticated and hasattr(request.user, 'feirante'):
        if request.user.feirante.id == feirante.id:  # type: ignore
            messages.warning(request, "Você não pode avaliar a si mesmo.")
            return redirect('feirantes:listar')

    if request.method == 'POST':
        form = AvaliacaoForm(request.POST)
        if form.is_valid():
            avaliacao = form.save(commit=False)
            avaliacao.feirante = feirante
            avaliacao.save()
            messages.success(request, "Avaliação registrada com sucesso!")
            return redirect('feirantes:listar')
    else:
        form = AvaliacaoForm()

    return render(request, 'feirantes/avaliar_feirante.html', {
        'form': form,
        'feirante': feirante
    })


@login_required
def painel_feirante(request):
    """Painel administrativo do feirante (com paginação de avaliações)"""
    try:
        feirante = request.user.feirante
    except Feirante.DoesNotExist:
        messages.error(request, 'Complete seu cadastro como feirante.')
        return redirect('feirantes:cadastro')

    # Produtos do feirante
    produtos = Produto.objects.filter(feirante=feirante)

    # Avaliações ordenadas
    avaliacoes_qs = Avaliacao.objects.filter(
        feirante=feirante
    ).order_by('-criado_em')

    # Média de notas
    media = avaliacoes_qs.aggregate(media=Avg('nota'))['media']
    media_avaliacao = round(media, 1) if media else None

    # Paginação (3 avaliações por página)
    paginator = Paginator(avaliacoes_qs, 3)
    page_number = request.GET.get('page', 1)
    try:
        avaliacoes = paginator.page(page_number)
    except PageNotAnInteger:
        avaliacoes = paginator.page(1)
    except EmptyPage:
        avaliacoes = paginator.page(paginator.num_pages)

    # Verifica se o perfil do feirante está completo
    perfil_completo = all([
        feirante.descricao,
        feirante.foto,
        produtos.exists(),
        feirante.feiras.exists(),
    ])

    # Renderiza o painel com as avaliações paginadas
    return render(request, 'feirantes/painel/dashboard.html', {
        'feirante': feirante,
        'produtos': produtos,
        'avaliacoes': avaliacoes,          # objeto paginado
        'media_avaliacao': media_avaliacao,
        'perfil_completo': perfil_completo,
    })


@login_required
def editar_perfil(request):
    """Editar perfil do feirante - com alteração de senha opcional"""
    try:
        feirante = request.user.feirante
    except Feirante.DoesNotExist:
        messages.error(request, 'Complete seu cadastro como feirante.')
        return redirect('feirantes:cadastro')

    if request.method == 'POST':
        # Adicionar o CPF ao POST data antes de criar o formulário
        post_data = request.POST.copy()
        post_data['cpf'] = feirante.cpf  # Garantir que o CPF esteja presente
        form = FeiranteForm(post_data, request.FILES, instance=feirante)

        if form.is_valid():
            feirante = form.save(commit=False)

            senha = form.cleaned_data.get('senha')
            confirmar_senha = form.cleaned_data.get('confirmar_senha')

            # Verifica e valida senha no padrão Django
            if senha or confirmar_senha:
                if senha != confirmar_senha:
                    messages.error(request, 'As senhas não coincidem.')
                    return render(request,
                                  'feirantes/painel/editar_perfil.html', {
                                      'form': form,
                                      'feirante': feirante,
                                      'password_validators_help_texts':
                                      password_validators_help_texts(),
                                  })

                try:
                    if senha:
                        validate_password(str(senha), request.user)
                    request.user.set_password(senha)
                    request.user.save()
                    update_session_auth_hash(request, request.user)
                    messages.success(request, 'Senha atualizada com sucesso!')
                except ValidationError as e:
                    for erro in e.messages:
                        messages.error(request, erro)
                    return render(
                        request, 'feirantes/painel/editar_perfil.html', {
                            'form': form,
                            'feirante': feirante,
                            'password_validators_help_texts':
                            password_validators_help_texts(),
                        })

            feirante.save()
            form.save_m2m()

            messages.success(request, 'Perfil atualizado com sucesso!')
            return redirect('feirantes:painel')
        else:
            messages.error(request, 'Corrija os erros no formulário.')
    else:
        form = FeiranteForm(instance=feirante)

    return render(request, 'feirantes/painel/editar_perfil.html', {
        'form': form,
        'feirante': feirante,
        'password_validators_help_texts':
        password_validators_help_texts(),
    })


@login_required
def gerenciar_produtos(request):
    """Lista de produtos do feirante"""
    try:
        feirante = request.user.feirante
    except Feirante.DoesNotExist:
        return HttpResponseForbidden(
            "Acesso negado. Complete seu cadastro como feirante.")

    produtos = Produto.objects.filter(feirante=feirante).order_by('-criado_em')
    return render(request, 'feirantes/painel/produtos.html',
                  {'produtos': produtos})


@login_required
def criar_produto(request):
    """Criar novo produto"""
    try:
        feirante = request.user.feirante
    except Feirante.DoesNotExist:
        messages.error(
            request,
            'Complete seu cadastro como feirante antes de adicionar produtos.')
        return redirect('feirantes:cadastro')

    if request.method == 'POST':
        form = ProdutoForm(request.POST, request.FILES)
        if form.is_valid():
            produto = form.save(commit=False)
            produto.feirante = feirante
            produto.save()
            form.save_m2m()
            messages.success(request, 'Produto criado com sucesso!')
            return redirect('feirantes:produtos')
        else:
            messages.error(request, 'Corrija os erros no formulário.')
    else:
        form = ProdutoForm()

    return render(request, 'feirantes/painel/produto_form.html',
                  {'form': form, 'acao': 'Criar'})


@login_required
def editar_produto(request, pk):
    """Editar produto existente"""
    try:
        feirante = request.user.feirante
    except Feirante.DoesNotExist:
        return HttpResponseForbidden("Acesso negado.")

    produto = get_object_or_404(Produto, pk=pk, feirante=feirante)

    if request.method == 'POST':
        form = ProdutoForm(request.POST, request.FILES, instance=produto)
        if form.is_valid():
            form.save()
            messages.success(request, 'Produto atualizado com sucesso!')
            return redirect('feirantes:produtos')
        else:
            messages.error(request, 'Corrija os erros no formulário.')
    else:
        form = ProdutoForm(instance=produto)

    return render(request, 'feirantes/painel/produto_form.html',
                  {'form': form, 'acao': 'Editar'})


@login_required
def excluir_produto(request, pk):
    """Excluir produto"""
    try:
        feirante = request.user.feirante
    except Feirante.DoesNotExist:
        return HttpResponseForbidden("Acesso negado.")

    produto = get_object_or_404(Produto, pk=pk, feirante=feirante)

    if request.method == 'POST':
        produto.delete()
        messages.success(request, 'Produto excluído com sucesso!')
        return redirect('feirantes:produtos')

    return render(request, 'feirantes/painel/produto_confirm_delete.html',
                  {'produto': produto})


@login_required
def minhas_feiras(request):
    """Feiras que o feirante participa"""
    feirante = request.user.feirante
    feiras = feirante.feiras.all()
    return render(request, 'feirantes/painel/minhas_feiras.html',
                  {'feiras': feiras})


# Termos de uso e política de privacidade
def termos_uso(request):
    return render(request, 'feirantes/termos_uso.html')


def politica_privacidade(request):
    return render(request, 'feirantes/politica_privacidade.html')


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    """View personalizada para redefinição de
          senha com exibição das regras do Django"""
    template_name = 'registration/senha_redefinir_confirmar.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Adiciona os textos de ajuda dos validadores de senha
        context[
            'password_validators_help_texts'
        ] = password_validators_help_texts()
        return context
