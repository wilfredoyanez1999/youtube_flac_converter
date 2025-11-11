import os
import time
import datetime

# --- CONFIGURACIÓN ---
# La ubicación de la carpeta 'temp_downloads' ahora es relativa a este archivo (downloader/)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMP_DIR = os.path.join(BASE_DIR, 'temp_downloads')

# Archivos de más de 1 hora (3600 segundos) serán eliminados
MAX_AGE_SECONDS = 3600

# INTERVALO DE EJECUCIÓN: El script se ejecutará cada 10 minutos (600 segundos)
SLEEP_TIME_SECONDS = 600

def run_cleanup():
    """Busca y elimina archivos más antiguos que la edad máxima permitida."""
    
    print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Iniciando limpieza en: {TEMP_DIR}")
    
    current_time = time.time()
    cutoff_time = current_time - MAX_AGE_SECONDS

    if not os.path.exists(TEMP_DIR):
        print("Advertencia: El directorio temporal no existe.")
        return

    files_cleaned = 0
    
    for filename in os.listdir(TEMP_DIR):
        file_path = os.path.join(TEMP_DIR, filename)
        
        # Solo procesa archivos FLAC y evita directorios
        if filename.endswith('.flac') and os.path.isfile(file_path):
            try:
                # Obtiene la hora de la última modificación del archivo
                file_mod_time = os.path.getmtime(file_path)
                
                # Comprueba si el archivo es más antiguo que el tiempo de corte
                if file_mod_time < cutoff_time:
                    os.remove(file_path)
                    print(f"  > Archivo ELIMINADO: {filename}")
                    files_cleaned += 1
                
            except OSError as e:
                # Captura el WinError 32 si el archivo fue creado recientemente y aún está bloqueado
                print(f"  > ERROR: No se pudo eliminar {filename}. Está siendo utilizado o tiene un error: {e}")
            except Exception as e:
                print(f"  > Error inesperado con {filename}: {e}")

    print(f"Limpieza completada. Archivos eliminados: {files_cleaned}")
    print("-" * 30)

def auto_clean_loop():
    """Función principal que ejecuta la limpieza en bucle para el hilo."""
    print("\n--- INICIANDO PROCESO DE LIMPIEZA AUTOMÁTICO (Hilo) ---")
    while True:
        try:
            run_cleanup()
        except Exception as e:
            print(f"Error grave en el bucle principal de limpieza: {e}")
        
        # Espera el tiempo configurado antes de la próxima ejecución
        time.sleep(SLEEP_TIME_SECONDS)

# Nota: Este __main__ ya no se usa, el bucle lo inicia apps.py
# if __name__ == "__main__":
#     auto_clean_loop()