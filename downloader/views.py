from django.shortcuts import redirect
from django.http import Http404, FileResponse
from django.views import View
from django.views.generic.edit import FormView
from .form import LinkForm 
import uuid
import os 
import yt_dlp
import io 
# Nota: Ya no necesitamos 'time' ni 'threading'
from django.conf import settings 

class HomeView(FormView):
    # ... (El código de HomeView se mantiene igual)

    template_name = 'downloader/homepage.html'
    form_class = LinkForm
    success_url = '/'  

    def form_valid(self, form):
        
        youtube_link = form.cleaned_data['link']
        
        temp_dir = os.path.join(os.path.dirname(__file__), 'temp_downloads')
        os.makedirs(temp_dir, exist_ok=True)
        
        file_id = str(uuid.uuid4()) 

        # PATRÓN DE SALIDA: Usa metadatos y el ID para asegurar un nombre único
        out_template = os.path.join(temp_dir, f'%(title)s_%(album)s_%(release_year)s-{file_id}.%(ext)s')
        
        try:
            
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': out_template, 
                'concurrent_fragment_downloads': 20, 
                'writethumbnail': True, 
                'embed_thumbnail': True, 
                'writemetadata': True,
                
                'parse_metadata': { 
                    'title': '%(title)s',
                    'album': '%(album)s',
                    'release_year': '%(release_year)s',
                    'artist': '%(artist)s',
                },
                'postprocessors': [
                    {
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'flac', 
                        'preferredquality': '5', 
                    },
                    {
                        'key': 'EmbedThumbnail',
                        'already_have_thumbnail': False,
                    }
                ],
                'ffmpeg_location': 'C:/Users/usuario/Documents/ffmpeg/bin/ffmpeg.exe', 
                'noplaylist': True,
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.extract_info(youtube_link, download=True) 
            
            # --- Buscar el nombre de archivo generado ---
            actual_file_name = None
            for fname in os.listdir(temp_dir):
                if fname.endswith(f'-{file_id}.flac'):
                    actual_file_name = fname
                    break
            
            if not actual_file_name:
                raise FileNotFoundError("Error: yt-dlp no pudo encontrar el archivo .flac.")

            # Redirecciona pasando el nombre completo del archivo
            return redirect('download_file', file_name=actual_file_name)

        except Exception as e:
            
            print(f"Error en la descarga/conversión de yt-dlp: {e}")
            form.add_error(None, f"Error al procesar el enlace. Detalles: {e}")
            return self.form_invalid(form) 


    def get_context_data(self, **kwargs):
        
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'YouTube a FLAC Converter'
        return context


# ----------------------------------------------------------------------
# VISTA CORREGIDA Y FINAL (SIN LIMPIEZA INMEDIATA)
# ----------------------------------------------------------------------
class DownloadFileView(View):
    
    def get(self, request, file_name): 

        file_path = os.path.join(os.path.dirname(__file__), 'temp_downloads', file_name)

        if os.path.exists(file_path): 
            try:
                
                # Abre el manejador del archivo binario
                file_handle = open(file_path, 'rb') 
                
                response = FileResponse(
                    file_handle, 
                    as_attachment=True, 
                    filename=file_name,
                    content_type='audio/flac' 
                )
                
                # LA ÚNICA TAREA EN response.close ES CERRAR EL MANEJADOR
                # Esto libera el bloqueo del sistema operativo inmediatamente después de la descarga.
                # El archivo permanece en el disco, pero DEJA DE ESTAR BLOQUEADO.
                response.close = file_handle.close
                
                return response

            except Exception as e:
                print(f"Error al servir el archivo: {e}")
                raise Http404("Error interno al acceder al archivo.")
        else:
            
            raise Http404("El archivo solicitado no existe.")