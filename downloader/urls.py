from django.urls import path
from .views import HomeView, DownloadFileView
from . import views


urlpatterns = [
    
    path('', HomeView.as_view(), name='homepage'),
    path('download/<str:file_name>/', views.DownloadFileView.as_view(), name='download_file')
]