from django.urls import path
from django.shortcuts import redirect
from contact import views

app_name = 'contact'

urlpatterns = [
    path('', views.index, name='index'),
    path('feiras/', views.FeiraView.as_view(), name = 'feira'), #lista de todas as feiras
    path('feira/<int:pk>', views.FeiraDetail.as_view(), name = 'barracas'), #lista de barracas em uma feira
]
def custom_404_view(request, exception):
    return redirect('index')
