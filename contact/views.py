from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Feira, Barraca
from django.views import generic
from django.http import Http404



def index(request):
    return render(
        request, 'contact/index.html',
    )

class FeiraView(generic.ListView): #lista de feiras
    model = Feira
    template_name = "contact/feira-list.html"
    paginate_by = 10



class FeiraDetail(generic.DetailView):
    model = Feira
    template_name = "contact/feira-detail.html"

    def get(self, request, *args, **kwargs): #sistema de mensagens do django para lidar com erros, ainda falta implementar nos templates
        try:                                 #função: caso não encontre x ID de feira, redireciona de volta a lista de feiras, outras abordagens também podem ser usadas
            return super().get(request, *args, **kwargs)
        except Http404: #caso haja um erro 404 (não encontrou aquele ID)
            messages.error(request, "Esta feira não existe ou foi removida")
            return redirect("contact:feiras")  
            
    

