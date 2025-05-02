from core.client import client 
from telethon.errors import ChatAdminRequiredError, ChannelPrivateError
from core.progress import show_progress
import os

async def get_users_with_message_count(entity, limit=200):
    """Obtiene usuarios con conteo de mensajes y barra de progreso"""
    users = []
    try:
        print("\n👥 Obteniendo lista de usuarios...")
        participants = await client.get_participants(entity, limit=limit)
        total_users = len(participants)
        
        if total_users == 0:
            print("ℹ️ No se encontraron usuarios en este chat")
            return []
        
        print(f"📊 Analizando mensajes de {total_users} usuarios...")
        
        for idx, user in enumerate(participants, 1):
            try:
                show_progress(idx, total_users, prefix="Progreso:", suffix=f"Usuario {idx}/{total_users}")
                
                message_count = 0
                async for msg in client.iter_messages(entity, from_user=user, limit=1000):  # Limitamos a 100 mensajes por usuario
                    message_count += 1
                
                user_info = {
                    'id': getattr(user, 'id', 'N/A'),
                    'first_name': getattr(user, 'first_name', ''),
                    'last_name': getattr(user, 'last_name', ''),
                    'username': getattr(user, 'username', 'N/A'),
                    'phone': getattr(user, 'phone', 'N/A'),
                    'bot': getattr(user, 'bot', False),
                    'verified': getattr(user, 'verified', False),
                    'premium': getattr(user, 'premium', False),
                    'deleted': getattr(user, 'deleted', False),
                    'status': str(getattr(user, 'status', 'Desconocido')),
                    'last_online': getattr(getattr(user, 'status', None), 'was_online', 'N/A'),
                    'access_hash': getattr(user, 'access_hash', 'N/A'),
                    'message_count': message_count
                }
                users.append(user_info)
            except Exception as e:
                print(f"\n⚠️ Error al procesar usuario {getattr(user, 'id', '')}: {e}")
                continue
                
        print("\n✅ Conteo de mensajes completado")
        return sorted(users, key=lambda x: x['message_count'], reverse=True)
                
    except (ChatAdminRequiredError, ChannelPrivateError) as e:
        print(f"\n⚠️ No se pueden obtener usuarios: {e}")
    except Exception as e:
        print(f"\n⚠️ Error al obtener usuarios: {str(e)}")
    
    return users

async def save_users(users, paths):
    """Guarda la información de usuarios incluyendo conteo de mensajes"""
    if not users or not paths:
        print("ℹ️ No hay usuarios para guardar o rutas no definidas")
        return None
        
    try:
        csv_file = os.path.join(paths['users'], 'usuarios.csv')
        with open(csv_file, 'w', encoding='utf-8') as f:
            f.write("ID,Nombre,Username,Telefono,Bot,Verificado,Premium,Eliminado,Estado,Ultima conexion,Access Hash,Mensajes\n")
            for user in users:
                full_name = f"{user.get('first_name', '')} {user.get('last_name', '')}".strip()
                f.write(f"{user.get('id', 'N/A')},\"{full_name}\",@{user.get('username', 'N/A')},{user.get('phone', 'N/A')},")
                f.write(f"{'Sí' if user.get('bot', False) else 'No'},{'Sí' if user.get('verified', False) else 'No'},")
                f.write(f"{'Sí' if user.get('premium', False) else 'No'},{'Sí' if user.get('deleted', False) else 'No'},")
                f.write(f"{user.get('status', 'N/A')},{user.get('last_online', 'N/A')},{user.get('access_hash', 'N/A')},{user.get('message_count', 0)}\n")
        
        detailed_file = os.path.join(paths['users'], 'usuarios_detallado.txt')
        with open(detailed_file, 'w', encoding='utf-8') as f:
            for idx, user in enumerate(users, 1):
                full_name = f"{user.get('first_name', '')} {user.get('last_name', '')}".strip()
                f.write(f"👤 USUARIO #{idx} ({user.get('message_count', 0)} mensajes)\n")
                f.write("="*40 + "\n")
                f.write(f"🆔 ID: {user.get('id', 'N/A')}\n")
                f.write(f"👤 Nombre: {full_name}\n")
                f.write(f"🔗 Username: @{user.get('username', 'N/A')}\n")
                f.write(f"📞 Teléfono: {user.get('phone', 'N/A')}\n")
                f.write(f"🤖 Bot: {'Sí' if user.get('bot', False) else 'No'}\n")
                f.write(f"✅ Verificado: {'Sí' if user.get('verified', False) else 'No'}\n")
                f.write(f"💎 Premium: {'Sí' if user.get('premium', False) else 'No'}\n")
                f.write(f"❌ Eliminado: {'Sí' if user.get('deleted', False) else 'No'}\n")
                f.write(f"🔄 Estado: {user.get('status', 'N/A')}\n")
                f.write(f"⏱ Última conexión: {user.get('last_online', 'N/A')}\n")
                f.write(f"🔑 Access Hash: {user.get('access_hash', 'N/A')}\n")
                f.write(f"💬 Total mensajes: {user.get('message_count', 0)}\n")
                f.write("\n")
        
        return csv_file, detailed_file
    except Exception as e:
        print(f"⚠️ Error al guardar usuarios: {e}")
        return None
