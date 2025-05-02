from config.settings import REPORTS_DIR
from config.directories import SUB_DIRS
from core.utils import sanitize_filename
from core.client import client  # ← Añade esto
from datetime import datetime  # ← Y esto por si acaso
import os


async def save_entity_info(info, paths):
    """Guarda la información de la entidad incluyendo topics si existen"""
    if not info or not paths:
        print("⚠️ No hay información para guardar o rutas no definidas")
        return None
        
    try:
        info_file = os.path.join(paths['info'], 'informacion_general.txt')
        
        with open(info_file, 'w', encoding='utf-8') as f:
            f.write("📌 INFORMACIÓN GENERAL\n")
            f.write("="*40 + "\n")
            f.write(f"🔹 Nombre: {info.get('name', 'Desconocido')}\n")
            f.write(f"🔹 Tipo: {info.get('type', 'N/A')}\n")
            f.write(f"🆔 ID: {info.get('id', 'N/A')}\n")
            f.write(f"🔑 Access Hash: {info.get('access_hash', 'N/A')}\n")
            f.write(f"📅 Fecha de creación: {info.get('creation_date', 'N/A')}\n")
            f.write(f"👥 Miembros: {info.get('participants_count', 'N/A')}\n")
            f.write(f"📝 Descripción: {info.get('description', 'N/A')}\n")
            f.write(f"🔗 Username: @{info.get('username', 'N/A')}\n")
            f.write(f"✅ Verificado: {'Sí' if info.get('verified', False) else 'No'}\n")
            f.write(f"🚫 Restringido: {'Sí' if info.get('restricted', False) else 'No'}\n")
            f.write(f"⚠️ Scam: {'Sí' if info.get('scam', False) else 'No'}\n")
            
            # Sección de topics/foro
            if info.get('is_forum', False):
                f.write("\n🗂 INFORMACIÓN DE FORO\n")
                f.write("="*40 + "\n")
                f.write(f"📌 Total de topics: {info.get('topics_count', 0)}\n")
                
                if info.get('topics'):
                    f.write("\n📌 Lista de topics:\n")
                    for topic in info['topics']:
                        f.write(f"  • {topic.get('title', 'Sin título')} (ID: {topic.get('id', 'N/A')})\n")
                        f.write(f"    📅 Creado: {topic.get('creation_date', 'N/A')}\n")
                        f.write(f"    💬 Mensajes: {topic.get('messages', 0)}\n")
                        if topic.get('last_message_date'):
                            f.write(f"    ⏱ Último mensaje: {topic['last_message_date'].strftime('%Y-%m-%d %H:%M:%S')}\n")
            else:
                f.write("\nℹ️ Este chat no es un foro o no tiene topics\n")
        
        return info_file
    except Exception as e:
        print(f"⚠️ Error al guardar información general: {e}")
        return None

async def setup_directories(entity_title):
    """Crea la estructura de directorios para el reporte"""
    try:
        safe_title = "".join(c for c in str(entity_title) if c.isalnum() or c in (' ', '_')).rstrip()
        if not safe_title:
            safe_title = "sin_nombre"
            
        base_path = os.path.join(REPORTS_DIR, safe_title)
        os.makedirs(base_path, exist_ok=True)
        
        paths = {'base': base_path}
        
        # Directorio de información
        info_path = os.path.join(base_path, SUB_DIRS['info'])
        os.makedirs(info_path, exist_ok=True)
        paths['info'] = info_path
        
        # Directorio de usuarios
        users_path = os.path.join(base_path, SUB_DIRS['users'])
        os.makedirs(users_path, exist_ok=True)
        paths['users'] = users_path
        
        # Directorios de medios
        media_path = os.path.join(base_path, 'media')
        os.makedirs(media_path, exist_ok=True)
        paths['media'] = media_path
        
        for media_type, media_dir in SUB_DIRS['media'].items():
            media_type_path = os.path.join(media_path, media_dir)
            os.makedirs(media_type_path, exist_ok=True)
            paths[media_type] = media_type_path
        
        # Directorio de enlaces
        links_path = os.path.join(base_path, SUB_DIRS['links'])
        os.makedirs(links_path, exist_ok=True)
        paths['links'] = links_path
        
        return paths
    except Exception as e:
        print(f"⚠️ Error crítico al crear directorios: {e}")
        return None

async def download_profile_photo(entity, paths):
    """Descarga la foto de perfil de la entidad"""
    try:
        if not paths or 'profile' not in paths:
            print("⚠️ Ruta no disponible para foto de perfil")
            return None
            
        profile_photo_path = os.path.join(paths['profile'], 'profile_photo.jpg')
        result = await client.download_profile_photo(entity, file=profile_photo_path)
        
        if not result:
            print("ℹ️ La entidad no tiene foto de perfil o no se pudo descargar")
            return None
            
        return profile_photo_path
    except Exception as e:
        print(f"⚠️ No se pudo descargar la foto de perfil: {e}")
        return None
