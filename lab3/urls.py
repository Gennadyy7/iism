from django.urls import path

from lab3.views import Lab3View

app_name = 'lab3'

urlpatterns = [
    path('', Lab3View.as_view(), name='index'),
]
