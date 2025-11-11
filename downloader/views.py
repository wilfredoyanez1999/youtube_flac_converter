from django.shortcuts import redirect
from django.http import Http404, FileResponse
from django.views import View
from django.views.generic.edit import FormView
from .form import LinkForm 
import uuid
import os 
import yt_dlp
import io 


class HomeView(FormView):

    template_name = 'downloader/homepage.html'
    form_class = LinkForm
    success_url = '/'  

    def form_valid(self, form):
        
        youtube_link = form.cleaned_data['link']
        temp_dir = os.path.join(os.path.dirname(__file__), 'temp_downloads')
        os.makedirs(temp_dir, exist_ok=True)
        
        file_id = str(uuid.uuid4()) 

        
        try:
            
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': os.path.join(temp_dir, f'{file_id}.%(ext)s'),
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'flac', 
                    'preferredquality': '0', 
                }],
                
                'ffmpeg_location': 'C:/Users/usuario/Documents/ffmpeg/bin/ffmpeg.exe', 
                'noplaylist': True,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.extract_info(youtube_link, download=True)
            
            
            return redirect('download_file', file_id=file_id)

        except Exception as e:
            
            print(f"Error en la descarga/conversión de yt-dlp: {e}")
            form.add_error(None, f"Error al procesar el enlace. Verifique que el link es válido. Detalles: {e}")
            return self.form_invalid(form) 


    def get_context_data(self, **kwargs):
        
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'YouTube a FLAC Converter'
        return context

class DownloadFileView(View):
    
    def get(self, request, file_id):

        file_path = os.path.join(os.path.dirname(__file__), 'temp_downloads', f'{file_id}.flac')

        if os.path.exists(file_path):
            try:
                
                file_handle = open(file_path, 'rb') 
                
                response = FileResponse(
                    file_handle, 
                    as_attachment=True, 
                    filename=f"youtube_audio_{file_id}.flac",
                    content_type='audio/flac' 
                )
                
                
                
                return response

            except Exception as e:
                print(f"Error al servir el archivo: {e}")
                raise Http404("Error interno al acceder al archivo.")
        else:
            
            raise Http404("El archivo solicitado no existe.")

        