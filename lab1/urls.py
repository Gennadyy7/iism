from django.urls import path

from lab1.views import Lab1View

app_name = 'lab1'

urlpatterns = [
    path('', Lab1View.as_view(), name='index'),
]
