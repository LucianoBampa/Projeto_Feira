from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from typing import Optional
from validate_docbr import CPF
from django.core.exceptions import ValidationError


class Especialidade(models.Model):
    """Especialidades dos feirantes (ex: Frutas, Verduras, Orgânicos)"""
    nome = models.CharField(max_length=100, unique=True)
    descricao = models.TextField(blank=True)
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Especialidade'
        verbose_name_plural = 'Especialidades'
        ordering = ['nome']

    def __str__(self):
        return self.nome


class Feira(models.Model):
    """Modelo para representar uma feira"""
    DIAS_SEMANA = [
        ('segunda', 'Segunda-feira'),
        ('terca', 'Terça-feira'),
        ('quarta', 'Quarta-feira'),
        ('quinta', 'Quinta-feira'),
        ('sexta', 'Sexta-feira'),
        ('sabado', 'Sábado'),
        ('domingo', 'Domingo'),
        ('segunda_quarta', 'Segunda e Quarta'),
        ('terca_quinta', 'Terça e Quinta'),
        ('segunda_quinta', 'Segunda a Quinta'),
        ('segunda_sexta', 'Segunda a Sexta'),
        ('sabado_domingo', 'Finais de Semana'),
        ('todos_dias', 'Todos os dias'),
    ]

    nome = models.CharField(max_length=200)
    endereco = models.TextField()
    cidade = models.CharField(max_length=100)
    estado = models.CharField(max_length=2)
    cep = models.CharField(max_length=9, blank=True)

    # Coordenadas para o mapa
    latitude = models.DecimalField(
        max_digits=10, decimal_places=7, blank=True, null=True)
    longitude = models.DecimalField(
        max_digits=10, decimal_places=7, blank=True, null=True)

    # Dias e horários de funcionamento
    dias_funcionamento = models.CharField(
        max_length=20, choices=DIAS_SEMANA, default='sabado')
    horario_funcionamento = models.CharField(
        max_length=100, blank=True, help_text="Ex: 7h às 12h")

    # Status
    ativa = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Feira'
        verbose_name_plural = 'Feiras'
        ordering = ['nome']

    def __str__(self):
        return f"{self.nome} - {self.cidade}"

    def get_dias_funcionamento_display(self):
        """Exibe os dias de funcionamento legíveis"""
        return dict(self.DIAS_SEMANA).get(self.dias_funcionamento, '')

    @property
    def latitude_float(self) -> Optional[float]:
        """Retorna latitude como float para JavaScript"""
        if self.latitude is not None:
            try:
                lat_str = str(self.latitude).replace(',', '.')
                return float(lat_str)
            except (ValueError, TypeError):
                return None
        return None

    @property
    def longitude_float(self) -> Optional[float]:
        """Retorna longitude como float para JavaScript"""
        if self.longitude is not None:
            try:
                lon_str = str(self.longitude).replace(',', '.')
                return float(lon_str)
            except (ValueError, TypeError):
                return None
        return None


class Feirante(models.Model):
    usuario = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='feirante')
    nome_comercial = models.CharField(max_length=200)
    cpf = models.CharField(max_length=14, unique=True)
    telefone = models.CharField(max_length=20)
    whatsapp = models.CharField(max_length=20, blank=True)
    email = models.EmailField()
    endereco = models.TextField(blank=True)
    cidade = models.CharField(max_length=100, blank=True)
    estado = models.CharField(max_length=2, blank=True)
    cep = models.CharField(max_length=9, blank=True)
    descricao = models.TextField(blank=True)
    foto = models.ImageField(upload_to='feirantes/', blank=True, null=True)
    especialidades = models.ManyToManyField(
        Especialidade, blank=True,
        help_text="Principais produtos/especialidades")
    feiras = models.ManyToManyField(
        Feira,
        blank=True,
        help_text="Feiras onde o feirante participa",
        related_name="feirantes"
    )
    subdominio = models.SlugField(
        max_length=100, unique=True,
        help_text="URL da loja: site.com/loja/[subdominio]")
    instagram = models.CharField(max_length=100, blank=True)
    facebook = models.CharField(max_length=100, blank=True)
    ativo = models.BooleanField(default=True)
    verificado = models.BooleanField(default=False)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    views = models.PositiveIntegerField(default=0)

    def clean(self):
        """Validação personalizada do CPF"""
        super().clean()
        if self.cpf:
            cpf_validator = CPF()
            if not cpf_validator.validate(self.cpf):
                raise ValidationError({'cpf': 'CPF inválido.'})

    class Meta:
        verbose_name = 'Feirante'
        verbose_name_plural = 'Feirantes'
        ordering = ['nome_comercial']

    def __str__(self):
        return self.nome_comercial

    def save(self, *args, **kwargs):
        if not self.subdominio:
            self.subdominio = slugify(self.nome_comercial)
        super().save(*args, **kwargs)


class Categoria(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    descricao = models.TextField(blank=True)
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorias'
        ordering = ['nome']

    def __str__(self):
        return self.nome


class Produto(models.Model):
    feirante = models.ForeignKey(Feirante, on_delete=models.CASCADE)
    categoria = models.ForeignKey(
        Categoria, on_delete=models.SET_NULL, null=True, blank=True)
    nome = models.CharField(max_length=200)
    descricao = models.TextField(blank=True)
    preco = models.DecimalField(
        max_digits=8, decimal_places=2, blank=True, null=True,
        help_text="Preço em reais")
    unidade = models.CharField(
        max_length=50, blank=True, help_text="Ex: kg, unidade, dúzia, maço")
    organico = models.BooleanField(default=False)
    producao_propria = models.BooleanField(default=True)
    foto = models.ImageField(upload_to='produtos/', blank=True, null=True)
    disponivel = models.BooleanField(default=True)
    estoque_limitado = models.BooleanField(default=False)
    observacoes = models.TextField(
        blank=True, help_text="Informações adicionais sobre disponibilidade")
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Produto'
        verbose_name_plural = 'Produtos'
        ordering = ['-criado_em']

    def __str__(self):
        return f"{self.nome} - {self.feirante.nome_comercial}"


class Contato(models.Model):
    nome = models.CharField(max_length=200)
    email = models.EmailField()
    telefone = models.CharField(max_length=20, blank=True)
    feirante = models.ForeignKey(
        Feirante, on_delete=models.CASCADE,
        help_text="Feirante que recebeu o contato")
    assunto = models.CharField(max_length=200)
    mensagem = models.TextField()
    lido = models.BooleanField(default=False)
    respondido = models.BooleanField(default=False)
    criado_em = models.DateTimeField(auto_now_add=True)
    respondido_em = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name = 'Contato'
        verbose_name_plural = 'Contatos'
        ordering = ['-criado_em']

    def __str__(self):
        return f"{self.assunto} - {self.nome}"
