from django.shortcuts import redirect
from django.http import Http404, FileResponse
from django.views import View
from django.views.generic.edit import FormView
from .form import LinkForm 
import uuid
import os 
import yt_dlp
from mutagen.flac import FLAC # <--- NUEVA IMPORTACIÓN
from django.conf import settings 

class HomeView(FormView):

    template_name = 'downloader/homepage.html'
    form_class = LinkForm
    success_url = '/'  

    def form_valid(self, form):
        
        youtube_link = form.cleaned_data['link']
        
        temp_dir = os.path.join(os.path.dirname(__file__), 'temp_downloads')
        os.makedirs(temp_dir, exist_ok=True)
        
        file_id = str(uuid.uuid4()) 
        
        # Diccionario para guardar la información que *sí* extrae yt-dlp (título, canal)
        info_dict = {} 
        
        def hook(d):
            # Obtener el info_dict para extraer el título y canal (necesario para mutagen)
            if d['status'] == 'finished':
                nonlocal info_dict
                info_dict = d['info_dict']

        # PATRÓN DE SALIDA
        out_template = os.path.join(temp_dir, f'%(title)s-{file_id}.%(ext)s')
        
        try:
            
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': out_template, 
                'concurrent_fragment_downloads': 20, 
                'progress_hooks': [hook], # Usamos el hook para obtener info_dict
                
                # Deshabilitamos todas las configuraciones de metadatos problemáticas:
                'writethumbnail': True, 
                'embed_thumbnail': True, 
                'writemetadata': False, # Deshabilitamos la escritura automática
                'parse_metadata': {}, # Vacío
                
                # POSTPROCESADORES (Solo los esenciales)
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
            
            # --- 1. BUSCAR el nombre de archivo generado con el UUID ---
            actual_file_name_with_uuid = None
            for fname in os.listdir(temp_dir):
                if fname.endswith(f'-{file_id}.flac'):
                    actual_file_name_with_uuid = fname
                    break
            
            if not actual_file_name_with_uuid:
                raise FileNotFoundError("Error: yt-dlp no pudo encontrar el archivo .flac.")

            # --- 2. RENOMBRAR Y LIMPIAR EL ARCHIVO EN DISCO (Lógica de renombrado anterior) ---
            base_name, extension = os.path.splitext(actual_file_name_with_uuid) 
            uuid_string_to_remove = f'-{file_id}' 
            try:
                index_to_cut = base_name.rindex(uuid_string_to_remove)
                base_name_clean_no_uuid = base_name[:index_to_cut]
            except ValueError:
                base_name_clean_no_uuid = base_name

            final_file_name_browser = base_name_clean_no_uuid + extension
            final_file_name_disk = final_file_name_browser.replace(' ', '_')

            # Manejo del WinError 183
            path_to_final_file = os.path.join(temp_dir, final_file_name_disk)
            if os.path.exists(path_to_final_file):
                print(f"DEBUG: Eliminando archivo de destino preexistente: {final_file_name_disk}")
                os.remove(path_to_final_file)

            os.rename(
                os.path.join(temp_dir, actual_file_name_with_uuid), 
                path_to_final_file
            )
            print("DEBUG: Archivo renombrado exitosamente en el disco.")
            
            # --- 3. ESCRIBIR METADATOS FORZADAMENTE CON MUTAGEN ---
            
            # 3a. Obtener valores de fallback
            title = info_dict.get('title', base_name_clean_no_uuid)
            artist_album = info_dict.get('channel', info_dict.get('uploader', 'Unknown Artist'))
            year = info_dict.get('upload_date', '')[:4] if info_dict.get('upload_date') else ''
            
            print("-" * 30)
            print(f"DEBUG: Escribiendo metadatos con Mutagen:")
            print(f"DEBUG: Título: {title}, Artista/Álbum: {artist_album}, Año: {year}")
            
            # 3b. Escribir al archivo FLAC
            audio = FLAC(path_to_final_file)
            
            # FLAC tags
            audio['title'] = [title]
            audio['artist'] = [artist_album]
            audio['album'] = [artist_album]
            audio['date'] = [year]
            
            audio.save()
            print("DEBUG: Metadatos escritos exitosamente.")
            print("-" * 30)
            
            # ------------------------------------------------------------------------
            return redirect('download_file', file_name=final_file_name_browser)

        except Exception as e:
            
            print(f"Error en el proceso de descarga/metadatos: {e}")
            form.add_error(None, f"Error al procesar el enlace. Detalles: {e}")
            return self.form_invalid(form) 


    def get_context_data(self, **kwargs):
        
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'YouTube a FLAC Converter'
        return context

class DownloadFileView(View):
    # La vista de descarga no necesita cambios, solo sirve el archivo limpio
    
    def get(self, request, file_name): 
        
        file_name_for_disk = file_name.replace(' ', '_').replace('%20', '_')
        file_path = os.path.join(os.path.dirname(__file__), 'temp_downloads', file_name_for_disk)

        if os.path.exists(file_path): 
            try:
                file_handle = open(file_path, 'rb') 
                response = FileResponse(
                    file_handle, 
                    as_attachment=True, 
                    filename=file_name, 
                    content_type='audio/flac' 
                )
                response.close = file_handle.close
                return response

            except Exception as e:
                print(f"Error al servir el archivo: {e}")
                raise Http404("Error interno al acceder al archivo.")
        else:
            raise Http404("El archivo solicitado no existe.")