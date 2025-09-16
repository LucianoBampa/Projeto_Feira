from django.contrib import admin
from .models import Feira, Feirante, Produto, Especialidade, Categoria, Contato
from .forms import FeiraForm  # Importe o formulário do forms.py
from validate_docbr import CPF
from django.core.exceptions import ValidationError


@admin.register(Feira)
class FeiraAdmin(admin.ModelAdmin):
    form = FeiraForm  # Use o formulário personalizado
    list_display = ['nome', 'cidade', 'estado', 'dias_funcionamento', 'ativa']
    list_filter = ['cidade', 'estado', 'dias_funcionamento', 'ativa']
    search_fields = ['nome', 'endereco', 'cidade']
    list_editable = ['ativa']

    fieldsets = (
        ('Informações Básicas', {
            'fields': ('nome', 'endereco', 'cidade', 'estado', 'cep')
        }),
        ('Localização', {
            'fields': ('latitude', 'longitude')
        }),
        ('Funcionamento', {
            'fields': ('dias_funcionamento', 'horario_funcionamento')
        }),
        ('Informações Adicionais', {
            'fields': ('descricao',)
        }),
        ('Status', {
            'fields': ('ativa',)
        }),
    )


@admin.register(Feirante)
class FeiranteAdmin(admin.ModelAdmin):
    list_display = ['nome_comercial', 'cpf', 'cidade',
                    'estado', 'ativo', 'verificado']
    list_filter = ['cidade', 'estado', 'ativo', 'verificado']
    search_fields = ['nome_comercial', 'email', 'cidade']
    filter_horizontal = ['especialidades', 'feiras']
    list_editable = ['ativo', 'verificado']

    def save_model(self, request, obj, form, change):
        # Valida CPF antes de salvar no admin também
        if obj.cpf:
            cpf_validator = CPF()
            cpf_limpo = ''.join(filter(str.isdigit, obj.cpf))
            if not cpf_validator.validate(cpf_limpo):
                raise ValidationError('CPF inválido')
            obj.cpf = cpf_validator.mask(cpf_limpo)
        super().save_model(request, obj, form, change)


@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'feirante', 'categoria', 'preco', 'disponivel']
    list_filter = ['categoria', 'organico', 'disponivel']
    search_fields = ['nome', 'feirante__nome_comercial']
    list_editable = ['disponivel']


@admin.register(Especialidade)
class EspecialidadeAdmin(admin.ModelAdmin):
    list_display = ['nome', 'ativo']
    list_filter = ['ativo']
    search_fields = ['nome']


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'ativo']
    list_filter = ['ativo']
    search_fields = ['nome']


@admin.register(Contato)
class ContatoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'email', 'feirante',
                    'lido', 'respondido', 'criado_em']
    list_filter = ['lido', 'respondido', 'criado_em']
    search_fields = ['nome', 'email', 'assunto']
    list_editable = ['lido', 'respondido']
