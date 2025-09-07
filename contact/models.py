from django.db import models
from django.urls import reverse # Used in get_absolute_url() to get URL for specified ID
from django.db.models import UniqueConstraint # Constrains fields to unique values
from django.db.models.functions import Lower
from django.conf import settings
# Create your models here.

class Feira(models.Model): 
    nome = models.CharField(
        max_length=200,
        unique=True,
        help_text="Digite o nome da feira"
        )
    latitude = models.FloatField()
    longitude = models.FloatField()

    def __str__(self):
        return(f"{self.nome}")

    def get_absolute_url(self):
        """Retorna a URL de uma Feira"""
        return reverse('feira-detail', args=[str(self.id)])


class Barraca(models.Model):
    nome = models.CharField(
        max_length=200,
        unique = False,
        help_text = "Nome de uma barraquinha")

    feira = models.ForeignKey( # a qual feira essa barraca pertence
        Feira,
        on_delete = models.CASCADE,
        related_name = "barracas"
        )

    dono = models.ForeignKey( # quem é o User dono da barraca
        settings.AUTH_USER_MODEL,
        on_delete = models.CASCADE)

    def __str__(self):
        return self.nome

    def get_absolute_url(self):
        """Retorna a URL de uma Barraca"""
        return reverse('barraca-detail', args=[str(self.id)])



class Produto(models.Model):
    nome = models.CharField(
        max_length=200,
        unique = False,
        help_text = "Nome de um produto")
    barraca = models.ForeignKey(
        Barraca,  # a barraca à qual o produto pertence
        on_delete=models.CASCADE,  # se a barraca for deletada, os produtos também
        related_name='produtos'   # permite acessar os produtos de uma barraca via barraca.produtos.all()
    )
    def __str__(self):
        return self.nome

