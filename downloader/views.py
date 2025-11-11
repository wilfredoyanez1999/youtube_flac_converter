from django.shortcuts import render
from django import forms
from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404, FileResponse
from django.views import View
from django.views.generic.edit import FormView
from .form import LinkForm
import uuid
import io


class HomeView(FormView):

    template_name = 'downloader/homepage.html'
    form_class = LinkForm
    success_url = '/'  # Se anula por la implementación de form_valid

    def form_valid(self, form):
        
        youtube_link = form.cleaned_data['link']
        
        
        
        file_id = str(uuid.uuid4()) 
        
        return redirect('download_file', file_id=file_id)

    def get_context_data(self, **kwargs):
        
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'YouTube a FLAC Converter'
        return context

class DownloadFileView(View):
    
    def get(self, request, file_id):

        file_name = f"audio_youtube_convertido_{file_id}.flac"
        file_data = b"Este es un contenido de audio simulado en FLAC."
        
        temp_file = io.BytesIO(file_data)
        
        try:
            response = FileResponse(
                temp_file, 
                as_attachment=True, 
                filename=file_name,
                
                content_type='audio/plain' 
            )
            
            
            return response
            
        except Exception as e:
            print(f"Error durante la descarga: {e}")
            raise Http404("El archivo de descarga no se encontró o hubo un error.")
