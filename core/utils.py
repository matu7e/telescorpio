import os
from datetime import datetime

async def safe_get_entity(entity):
    """Obtiene la entidad de forma segura"""
    try:
        if hasattr(entity, 'entity'):
            return entity.entity
        return entity
    except Exception as e:
        print(f"⚠️ Error al obtener entidad: {e}")
        return None

def sanitize_filename(filename):
    """Limpia un string para usarlo como nombre de archivo"""
    return "".join(c for c in str(filename) if c.isalnum() or c in (' ', '_')).rstrip()