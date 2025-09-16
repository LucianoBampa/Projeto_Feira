from django import forms
from .models import Feira, Feirante, Produto
from validate_docbr import CPF
from typing import Optional


# ==========================
# Form de Feira
# ==========================
class FeiraForm(forms.ModelForm):
    latitude = forms.FloatField(
        required=False,
        label="Latitude",
        help_text="Ex: -20.5531",
        widget=forms.NumberInput(
            attrs={"class": "form-control"})
    )
    longitude = forms.FloatField(
        required=False,
        label="Longitude",
        help_text="Ex: -48.5678",
        widget=forms.NumberInput(
            attrs={"class": "form-control"})
    )

    class Meta:
        model = Feira
        fields = [
            'nome', 'endereco', 'cidade', 'estado', 'cep',
            'latitude', 'longitude', 'dias_funcionamento',
            'horario_funcionamento', 'ativa'
        ]
        widgets = {
            "nome": forms.TextInput(
                attrs={"class": "form-control"}),
            "endereco": forms.TextInput(
                attrs={"class": "form-control"}),
            "cidade": forms.TextInput(
                attrs={"class": "form-control"}),
            "estado": forms.TextInput(
                attrs={"class": "form-control"}),
            "cep": forms.TextInput(
                attrs={"class": "form-control"}),
            "dias_funcionamento": forms.TextInput(
                attrs={"class": "form-control"}),
            "horario_funcionamento": forms.TextInput(
                attrs={"class": "form-control"}),
            "ativa": forms.CheckboxInput(
                attrs={"class": "form-check-input"}),
        }

    def clean_latitude(self) -> Optional[float]:
        value = self.cleaned_data.get("latitude")
        return float(value) if value not in (None, "") else None

    def clean_longitude(self) -> Optional[float]:
        value = self.cleaned_data.get("longitude")
        return float(value) if value not in (None, "") else None

# ==========================
# Form de Feirante Cadastro
# ==========================


class CadastroFeiranteForm(forms.Form):
    nome_completo = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "autocomplete": "off",
            "autocorrect": "off",
            "autocapitalize": "off",
            "spellcheck": "false"
        }),
        label="Nome Completo *"
    )
    nome_comercial = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "autocomplete": "off",
            "autocorrect": "off",
            "autocapitalize": "off",
            "spellcheck": "false"
        }),
        label="Nome Comercial *"
    )
    cpf = forms.CharField(
        max_length=14,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "autocomplete": "off",
            "autocorrect": "off",
            "autocapitalize": "off",
            "spellcheck": "false"
        }),
        label="CPF *"
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            "class": "form-control",
            "autocomplete": "off",
            "autocorrect": "off",
            "autocapitalize": "off",
            "spellcheck": "false"
        }),
        label="Email *"
    )
    telefone = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "autocomplete": "off",
            "autocorrect": "off",
            "autocapitalize": "off",
            "spellcheck": "false",
            "inputmode": "numeric"
        }),
        label="Telefone *"
    )
    senha = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "autocomplete": "new-password",
            "autocorrect": "off",
            "autocapitalize": "off",
            "spellcheck": "false"
        }),
        label="Senha *"
    )
    confirmar_senha = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "autocomplete": "new-password",
            "autocorrect": "off",
            "autocapitalize": "off",
            "spellcheck": "false"
        }),
        label="Confirmar Senha *"
    )
    descricao = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            "class": "form-control",
            "rows": 3,
            "autocomplete": "off",
            "autocorrect": "off",
            "autocapitalize": "off",
            "spellcheck": "false"
        }),
        label="Descrição"
    )

    def clean_cpf(self):
        cpf = self.cleaned_data.get('cpf', '')
        cpf_validator = CPF()
        cpf_limpo = ''.join([char for char in cpf if char.isdigit()])
        if not cpf_validator.validate(cpf_limpo):
            raise forms.ValidationError("CPF inválido.")
        return cpf_validator.mask(cpf_limpo)

    def clean(self):
        cleaned_data = super().clean()
        senha = cleaned_data.get("senha")
        confirmar_senha = cleaned_data.get("confirmar_senha")

        if senha and confirmar_senha and senha != confirmar_senha:
            raise forms.ValidationError("As senhas não coincidem.")

        return cleaned_data


# ==========================
# Form de Feirante Edição
# ==========================


class FeiranteForm(forms.ModelForm):
    confirmar_email = forms.EmailField(
        required=False,
        label="Confirmar E-mail",
        widget=forms.EmailInput(attrs={"class": "form-control"})
    )
    senha = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
        required=False,
        label="Nova senha"
    )
    confirmar_senha = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
        required=False,
        label="Confirmar nova senha"
    )

    class Meta:
        model = Feirante
        fields = [
            'nome_comercial', 'cpf', 'telefone', 'whatsapp',
            'email', 'endereco', 'cidade', 'estado', 'cep',
            'descricao', 'foto', 'especialidades',
            'feiras', 'ativo', 'verificado', 'subdominio',
            'instagram', 'facebook'
        ]
        widgets = {
            "nome_comercial": forms.TextInput(
                attrs={"class": "form-control"}),
            'cpf': forms.TextInput(
                attrs={'class': 'form-control', 'readonly': 'readonly'}),
            "telefone": forms.TextInput(
                attrs={"class": "form-control"}),
            "whatsapp": forms.TextInput(
                attrs={"class": "form-control"}),
            "email": forms.EmailInput(
                attrs={"class": "form-control"}),
            "endereco": forms.Textarea(
                attrs={"class": "form-control", "rows": 3}),
            "cidade": forms.TextInput(
                attrs={"class": "form-control"}),
            "estado": forms.TextInput(
                attrs={"class": "form-control"}),
            "cep": forms.TextInput(
                attrs={"class": "form-control"}),
            "descricao": forms.Textarea(
                attrs={"class": "form-control", "rows": 3}),
            "foto": forms.ClearableFileInput(
                attrs={"class": "form-control"}),
            "especialidades": forms.SelectMultiple(
                attrs={"class": "form-select"}),
            "feiras": forms.SelectMultiple(
                attrs={"class": "form-select"}),
            "ativo": forms.CheckboxInput(
                attrs={"class": "form-check-input"}),
            "verificado": forms.CheckboxInput(
                attrs={"class": "form-check-input"}),
            "subdominio": forms.TextInput(
                attrs={"class": "form-control"}),
            "instagram": forms.TextInput(
                attrs={"class": "form-control"}),
            "facebook": forms.TextInput(
                attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            # Para edição, tornar o CPF não obrigatório
            self.fields['cpf'].required = False
            self.fields['confirmar_email'].initial = self.instance.email

    def clean_cpf(self):
        cpf = self.cleaned_data.get("cpf", "")
        # Se o CPF estiver vazio (na edição), usar o CPF existente
        if not cpf and self.instance and self.instance.pk:
            return self.instance.cpf

        if cpf:
            cpf_validator = CPF()
            # Corrigindo o uso do filter e join
            cpf_limpo = ''.join([char for char in cpf if char.isdigit()])
            if not cpf_validator.validate(cpf_limpo):
                raise forms.ValidationError("CPF inválido.")
            cpf_formatado = cpf_validator.mask(cpf_limpo)

            qs = Feirante.objects.filter(cpf=cpf_formatado)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError("Este CPF já está cadastrado.")

            return cpf_formatado
        return cpf

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if email:
            qs = Feirante.objects.filter(email=email)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError("Este e-mail já está cadastrado.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        confirmar_email = cleaned_data.get("confirmar_email")
        senha = cleaned_data.get("senha")
        confirmar_senha = cleaned_data.get("confirmar_senha")

        if email and confirmar_email and email != confirmar_email:
            raise forms.ValidationError("Os e-mails não coincidem.")

        if senha or confirmar_senha:
            if senha != confirmar_senha:
                raise forms.ValidationError("As senhas não coincidem.")
            if senha and len(senha) < 6:
                raise forms.ValidationError(
                    "A senha deve ter pelo menos 6 caracteres.")


# ==========================
# Form de Produto
# ==========================
class ProdutoForm(forms.ModelForm):
    preco = forms.DecimalField(
        required=False,
        max_digits=8,
        decimal_places=2,
        widget=forms.NumberInput(attrs={"class": "form-control"})
    )

    class Meta:
        model = Produto
        fields = [
            'categoria', 'nome', 'descricao', 'preco', 'unidade',
            'organico', 'producao_propria', 'foto', 'disponivel',
            'estoque_limitado', 'observacoes'
        ]
        widgets = {
            "categoria": forms.Select(
                attrs={"class": "form-select"}),
            "nome": forms.TextInput(
                attrs={"class": "form-control"}),
            "descricao": forms.Textarea(
                attrs={"class": "form-control", "rows": 3}),
            "unidade": forms.TextInput(
                attrs={"class": "form-control"}),
            "organico": forms.CheckboxInput(
                attrs={"class": "form-check-input"}),
            "producao_propria": forms.CheckboxInput(
                attrs={"class": "form-check-input"}),
            "foto": forms.ClearableFileInput(
                attrs={"class": "form-control"}),
            "disponivel": forms.CheckboxInput(
                attrs={"class": "form-check-input"}),
            "estoque_limitado": forms.CheckboxInput(
                attrs={"class": "form-check-input"}),
            "observacoes": forms.Textarea(
                attrs={"class": "form-control", "rows": 2}),
        }
