from django.shortcuts import render
from .models import Feira, Barraca
from django.views import generic



def index(request):
    return render(
        request, 'contact/index.html',
    )

class FeiraView(generic.ListView): #lista de feiras
    model = Feira
    template_name = "contact/feira-list.html"
    paginate_by = 10

class FeiraDetail(generic.DetailView): #lista de barracas de uma feira X
    model = Feira
    template_name = "contact/feira-detail.html"
    

