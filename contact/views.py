from django.shortcuts import render
from .models import Feira, Barraca
from django.views import generic



def index(request):
    return render(
        request, 'contact/index.html',
    )

class FeiraView(generic.ListView):
    model = Feira
    template_name = "contact/feira_list.html"
    paginate_by = 10

class BarracaView(generic.DetailView):
    model = Barraca
    template_name = ""
    

