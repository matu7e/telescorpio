# handlers/collection_handler.py
from handlers.entity_handler import get_entity_info
from handlers.user_handler import get_users_with_message_count, save_users
from handlers.link_handler import get_links, save_links
from handlers.media_handler import get_media, save_media
from handlers.file_handler import download_profile_photo, save_entity_info
from core.progress import show_progress

async def collect_all_data(entity, paths):
    """Recopila todos los datos de la entidad con barras de progreso"""
    if not paths:
        print("⚠️ No se pueden guardar los datos - rutas no definidas")
        return False
        
    print("\n🔍 Comenzando recolección completa de datos...")
    
    try:
        # 1. Información general y foto de perfil
        print("\n📌 Obteniendo información general...")
        entity_info = await get_entity_info(entity)
        if entity_info:
            await save_entity_info(entity_info, paths)
            await download_profile_photo(entity, paths)
            print(f"✅ Información guardada en: {paths['info']}")
        else:
            print("⚠️ No se pudo obtener información general")
        
        # 2. Usuarios con conteo de mensajes
        print("\n👥 Obteniendo lista de usuarios con conteo de mensajes...")
        users = await get_users_with_message_count(entity)
        if users:
            await save_users(users, paths)
            print(f"✅ Usuarios guardados en: {paths['users']}")
        else:
            print("ℹ️ No se pudieron obtener usuarios o el chat no tiene usuarios")
        
        # 3. Enlaces
        print("\n🔗 Obteniendo enlaces compartidos...")
        links = await get_links(entity)
        if links:
            await save_links(links, paths)
            print(f"✅ Enlaces guardados en: {paths['links']}")
        else:
            print("ℹ️ No se encontraron enlaces compartidos")
        
        # 4. Medios
        media_types = ['photos', 'videos', 'audios', 'stickers', 'documents']
        for media_type in media_types:
            print(f"\n📸 Obteniendo {media_type}...")
            media = await get_media(entity, media_type)
            if media:
                await save_media(media, media_type, paths)
                print(f"✅ {media_type.capitalize()} guardados en: {paths[media_type]}")
            else:
                print(f"ℹ️ No se encontraron {media_type}")
        
        print("\n✅ Recolección completa finalizada!")
        return True
    except Exception as e:
        print(f"\n⚠️ Error crítico durante la recolección completa: {e}")
        return False