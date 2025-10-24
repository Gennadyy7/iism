from django.urls import path

from lab5.views import Lab5View

app_name = 'lab5'

urlpatterns = [
    path('', Lab5View.as_view(), name='index'),
]
