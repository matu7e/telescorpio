from datetime import datetime  # ← Añade esto
from telethon.tl.types import (
    MessageMediaPhoto, MessageMediaDocument,
    DocumentAttributeVideo, DocumentAttributeAudio,
    DocumentAttributeSticker, DocumentAttributeFilename
)
from core.progress import show_progress
from core.client import client  # ← También añade esto para el cliente
import os

async def get_media(entity, media_type, limit=200):
    """Obtiene medios específicos de la entidad con barra de progreso"""
    media = []
    try:
        print(f"\n📸 Buscando {media_type}...")
        total_messages = 0
        last_progress = 0
        
        async for message in client.iter_messages(entity, limit=limit):
            total_messages += 1
            progress = int((total_messages / limit) * 100)
            if progress != last_progress:
                show_progress(total_messages, limit, prefix="Progreso:", suffix=f"{total_messages}/{limit} mensajes")
                last_progress = progress
            
            try:
                if not message.media:
                    continue
                    
                if media_type == 'photos' and isinstance(message.media, MessageMediaPhoto):
                    media.append(message)
                elif media_type == 'videos' and isinstance(message.media, MessageMediaDocument):
                    for attr in message.media.document.attributes:
                        if isinstance(attr, DocumentAttributeVideo):
                            media.append(message)
                            break
                elif media_type == 'audios' and isinstance(message.media, MessageMediaDocument):
                    for attr in message.media.document.attributes:
                        if isinstance(attr, DocumentAttributeAudio) and not isinstance(attr, DocumentAttributeSticker):
                            media.append(message)
                            break
                elif media_type == 'stickers' and isinstance(message.media, MessageMediaDocument):
                    for attr in message.media.document.attributes:
                        if isinstance(attr, DocumentAttributeSticker):
                            media.append(message)
                            break
                elif media_type == 'documents' and isinstance(message.media, MessageMediaDocument):
                    has_attributes = False
                    for attr in message.media.document.attributes:
                        if isinstance(attr, (DocumentAttributeVideo, DocumentAttributeAudio, DocumentAttributeSticker)):
                            has_attributes = True
                            break
                    if not has_attributes:
                        media.append(message)
            except Exception as e:
                continue
        
        print(f"\n✅ Encontrados {len(media)} {media_type} en {total_messages} mensajes")
        return media
    except Exception as e:
        print(f"\n⚠️ Error al obtener {media_type}: {e}")
        return []

async def save_media(media, media_type, paths):
    """Guarda y descarga los medios encontrados con barra de progreso"""
    if not paths or media_type not in paths:
        print(f"⚠️ Ruta no disponible para {media_type}")
        return None
        
    try:
        media_dir = paths[media_type]
        info_file = os.path.join(media_dir, f"info_{media_type}.txt")
        total_media = len(media)
        
        if total_media == 0:
            return None
        
        print(f"\n💾 Guardando {total_media} {media_type}...")
        
        with open(info_file, 'w', encoding='utf-8') as f:
            for idx, message in enumerate(media, 1):
                show_progress(idx, total_media, prefix="Progreso:", suffix=f"Medio {idx}/{total_media}")
                
                try:
                    sender_id = getattr(message, 'sender_id', 'Desconocido')
                    date = getattr(message, 'date', datetime.now()).strftime('%Y-%m-%d %H:%M:%S')
                    message_id = getattr(message, 'id', 'N/A')
                    
                    ext = '.jpg' if media_type == 'photos' else ''
                    if media_type == 'documents' and hasattr(message.media, 'document') and message.media.document.attributes:
                        for attr in message.media.document.attributes:
                            if isinstance(attr, DocumentAttributeFilename):
                                ext = os.path.splitext(attr.file_name)[1]
                                break
                    
                    filename = f"{media_type}_{idx}{ext}"
                    filepath = os.path.join(media_dir, filename)
                    
                    await client.download_media(message.media, file=filepath)
                    
                    f.write(f"📄 ARCHIVO #{idx}\n")
                    f.write("="*30 + "\n")
                    f.write(f"📁 Nombre: {filename}\n")
                    f.write(f"📩 ID Mensaje: {message_id}\n")
                    f.write(f"👤 ID Usuario: {sender_id}\n")
                    f.write(f"📅 Fecha: {date}\n")
                    f.write("\n")
                except Exception as e:
                    print(f"\n⚠️ Error al procesar medio {idx}: {e}")
                    continue
        
        print(f"\n✅ {total_media} {media_type} guardados correctamente")
        return info_file
    except Exception as e:
        print(f"\n⚠️ Error al guardar {media_type}: {e}")
        return None
