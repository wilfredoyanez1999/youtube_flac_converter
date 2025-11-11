from django.urls import path
from .views import HomeView, DownloadFileView

urlpatterns = [
    
    path('', HomeView.as_view(), name='homepage'),
    
    path('download/<str:file_id>/', DownloadFileView.as_view(), name='download_file'),
]