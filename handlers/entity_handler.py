from core.client import client
from datetime import datetime
from core.utils import safe_get_entity
from handlers.file_handler import save_entity_info, download_profile_photo

async def get_entity_info(entity):
    """Obtiene información general de la entidad (compatible con Telethon 1.40.0)"""
    try:
        real_entity = await safe_get_entity(entity)
        if not real_entity:
            return None
            
        # Información base
        info = {
            'name': getattr(real_entity, 'title', getattr(real_entity, 'first_name', 'Desconocido')),
            'id': getattr(real_entity, 'id', 'N/A'),
            'type': "Canal" if getattr(real_entity, 'is_channel', False) else 
                   "Grupo" if getattr(real_entity, 'is_group', False) else 
                   "Chat privado",
            'creation_date': getattr(real_entity, 'date', datetime.now()).strftime('%Y-%m-%d %H:%M:%S'),
            'description': getattr(real_entity, 'about', 'Sin descripción'),
            'participants_count': getattr(real_entity, 'participants_count', 'N/A'),
            'username': getattr(real_entity, 'username', 'N/A'),
            'verified': getattr(real_entity, 'verified', False),
            'restricted': getattr(real_entity, 'restricted', False),
            'scam': getattr(real_entity, 'scam', False),
            'access_hash': getattr(real_entity, 'access_hash', 'N/A'),
            'is_forum': getattr(real_entity, 'forum', False)
        }
        
        # Solución alternativa para foros (sin iter_forum_topics)
        if info['is_forum']:
            info['topics'] = []
            info['topics_count'] = 0
            print("\nℹ️ La versión 1.40.0 de Telethon no soporta análisis detallado de topics")
            
        return info
    except Exception as e:
        print(f"⚠️ Error al obtener información de la entidad: {e}")
        return None