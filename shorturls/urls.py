from django.urls import path

from django.forms import *
from .views import RedirectView,InvalidoView,FileCreateView,FileListView,FileUpdateView,DashboardView,FileDeleteView


app_name = "shorturls"

urlpatterns = [
               path("s/<slug:short>/", RedirectView.as_view(), name="index"),
               path("invalido", InvalidoView.as_view(), name="invalido"),


               path("create", FileCreateView.as_view(), name="create"),
               path("list", FileListView.as_view(), name="list"),
               path("procesar/<int:pk>/", FileUpdateView.as_view(), name="procesar"),
               path("delete/<int:pk>/", FileDeleteView.as_view(), name="procesar"),
               path('dashboard', DashboardView.as_view(), name='dashboard'),

               ]
