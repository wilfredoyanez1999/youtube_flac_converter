import os
import threading
import time

from django.apps import AppConfig


class DownloaderConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'downloader'

    def ready(self):
        # El chequeo RUN_MAIN es vital para evitar que el código se ejecute
        # dos veces o en procesos no deseados como migraciones.
        if os.environ.get('RUN_MAIN', None) == 'true':
            
            # Importar la función después de cargar la configuración
            from .cleaner import auto_clean_loop 

            # Creamos un hilo. daemon=True asegura que el hilo muera cuando el proceso principal de Django termine.
            cleaner_thread = threading.Thread(target=auto_clean_loop, daemon=True)
            cleaner_thread.start()
            print("Hilo de limpieza iniciado en segundo plano. Los archivos se eliminarán cada 10 minutos.")