import asyncio
from telethon.errors import ChannelPrivateError
from core.client import client
from colorama import Fore, Style, init

init(autoreset=True)

async def show_main_menu():
    """Muestra el menú principal con estilo hacker"""
    try:
        print(Fore.GREEN + r"""
                                                                                                                
$$$$$$$$\        $$\            $$$$$$\                                          $$\           
\__$$  __|       $$ |          $$  __$$\                                         \__|          
   $$ | $$$$$$\  $$ | $$$$$$\  $$ /  \__| $$$$$$$\  $$$$$$\   $$$$$$\   $$$$$$\  $$\  $$$$$$\  
   $$ |$$  __$$\ $$ |$$  __$$\ \$$$$$$\  $$  _____|$$  __$$\ $$  __$$\ $$  __$$\ $$ |$$  __$$\ 
   $$ |$$$$$$$$ |$$ |$$$$$$$$ | \____$$\ $$ /      $$ /  $$ |$$ |  \__|$$ /  $$ |$$ |$$ /  $$ |
   $$ |$$   ____|$$ |$$   ____|$$\   $$ |$$ |      $$ |  $$ |$$ |      $$ |  $$ |$$ |$$ |  $$ |
   $$ |\$$$$$$$\ $$ |\$$$$$$$\ \$$$$$$  |\$$$$$$$\ \$$$$$$  |$$ |      $$$$$$$  |$$ |\$$$$$$  |
   \__| \_______|\__| \_______| \______/  \_______| \______/ \__|      $$  ____/ \__| \______/ 
                                                                       $$ |                    
                                                                       $$ |                    
                                                                       \__|                    
        """)
        print(Fore.LIGHTGREEN_EX + "\n[*] Bienvenido al " + Fore.LIGHTCYAN_EX + "TELEGRAM OSINT TOOL" + Fore.LIGHTGREEN_EX + " [*]\n")
        print(Fore.GREEN + "="*100)
        print(Fore.LIGHTCYAN_EX + "1. 🕵️‍♂️ Escanear objetivo por enlace público")
        print("2. 👥 Listar y analizar mis grupos/canales")
        print("0. 🚪 Finalizar operación")
        print(Fore.GREEN + "="*100)
        
        while True:
            choice = input(Fore.LIGHTGREEN_EX + "\n\033[95m[?]\033[0m Seleccione una opción (0-2) >>> " + Style.RESET_ALL).strip()
            print()
            print(Fore.GREEN + "="*100)
            if choice in ["0", "1", "2"]:
                return choice
            print(Fore.RED + "[!] Opción inválida. Inténtelo nuevamente.")
            
    except Exception as e:
        print(Fore.RED + f"\n[!] Error crítico en el menú: {str(e)}")
        return "0"

from colorama import Fore, Style
from core.client import client  # Asegurate de importar tu client

async def list_user_chats():
    """Lista grupos y canales del usuario, excluyendo chats personales"""
    
    try:
        dialogs = await client.get_dialogs()
        
        public_chats = [
            dialog for dialog in dialogs 
            if getattr(dialog, 'is_group', False) or 
               getattr(dialog, 'is_channel', False) or
               getattr(dialog, 'megagroup', False)
        ]
        
        if not public_chats:
            print(Fore.YELLOW + "[!] No tienes grupos o canales disponibles." + Style.RESET_ALL)
            return None
        
        for idx, dialog in enumerate(public_chats, 1):
            name = getattr(dialog, 'name', 'Chat sin nombre')
            if getattr(dialog, 'is_channel', False):
                chat_type = "Canal"
            elif getattr(dialog, 'megagroup', False):
                chat_type = "Supergrupo"
            else:
                chat_type = "Grupo"
            
            print(
                Fore.LIGHTCYAN_EX + f"{idx}. {name} " +
                Fore.LIGHTRED_EX + f"({chat_type}, ID: {getattr(dialog, 'id', 'N/A')})" +
                Style.RESET_ALL
            )
            
        while True:
            try:
                print(Fore.GREEN + "="*100)
                choice = input(Fore.LIGHTGREEN_EX + "\n\033[95m[?]\033[0m Seleccione un chat (0 para cancelar) >>> " + Style.RESET_ALL)
                print(Fore.GREEN + "="*100)
                if choice == "0":
                    return None
                
                choice = int(choice)
                if 1 <= choice <= len(public_chats):
                    return public_chats[choice - 1]
                
                print(Fore.RED + "[!] Selección inválida." + Style.RESET_ALL)
            except ValueError:
                print(Fore.RED + "[!] Por favor ingrese un número válido." + Style.RESET_ALL)
    except Exception as e:
        print(Fore.RED + f"[!] Error al listar chats: {e}" + Style.RESET_ALL)
        return None

        
async def get_chat_by_link():
    """Obtiene un chat por enlace"""
    while True:
        try:
            url = input(Fore.LIGHTGREEN_EX + "\n[+] Ingrese el enlace del chat objetivo: " + Style.RESET_ALL).strip()
            if not url:
                print(Fore.RED + "[!] Debe ingresar un enlace válido.")
                continue
            
            try:
                print(Fore.LIGHTGREEN_EX + "\n[*] Analizando enlace, espere...")
                entity = await client.get_entity(url)
                print(Fore.LIGHTCYAN_EX + "[✓] Chat encontrado exitosamente.")
                return entity
            except ValueError:
                print(Fore.RED + "[!] El enlace no es válido o el chat no existe.")
            except ChannelPrivateError:
                print(Fore.RED + "[!] El chat es privado y no tienes autorización.")
            except Exception as e:
                print(Fore.RED + f"[!] Error al obtener el chat: {e}")
            
            return None
        except Exception as e:
            print(Fore.RED + f"[!] Error inesperado: {e}")
            return None
