from django.urls import path

from lab4.views import Lab4View

app_name = 'lab4'

urlpatterns = [
    path('', Lab4View.as_view(), name='index'),
]
