from django.urls import path

from contact import views

app_name = 'contact'

urlpatterns = [
    path('', views.index, name='index'),
    path('feira/<int:pk>', views.FeiraView.as_view(), name = 'feira'),
    path('barraca/<int:pk>', views.BarracaView.as_view(), name = 'barraca'),
]
