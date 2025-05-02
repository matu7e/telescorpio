import asyncio  # ¡Este es el import que falta!
from core.client import client
from menus.main_menu import show_main_menu, list_user_chats, get_chat_by_link
from menus.entity_menu import show_entity_menu
from handlers.entity_handler import get_entity_info
from handlers.collection_handler import collect_all_data
from handlers.file_handler import setup_directories, save_entity_info, download_profile_photo
from handlers.user_handler import get_users_with_message_count, save_users
from handlers.link_handler import get_links, save_links, create_link_info, process_link
from handlers.media_handler import get_media, save_media
from analyzers.activity_analyzer import analyze_activity_patterns, detect_activity_spikes, plot_activity
from analyzers.domain_analyzer import analyze_domains, get_risk_domains
from analyzers.pattern_analyzer import analyze_messages
from colorama import Fore, Style

async def main():
    """Función principal"""
    try:
        await client.start()
        
        while True:
            try:
                choice = await show_main_menu()
                
                if choice == "0":
                    print("\n👋 Saliendo de la herramienta...")
                    break
                
                elif choice == "1":
                    entity = await get_chat_by_link()
                elif choice == "2":
                    entity = await list_user_chats()
                else:
                    print("⚠️ Opción no válida.")
                    continue
                
                if not entity:
                    continue
                
                # Configurar directorios
                entity_title = getattr(entity, 'title', getattr(entity, 'first_name', 'entidad_desconocida'))
                paths = await setup_directories(entity_title)
                if not paths:
                    print("⚠️ No se pudo crear la estructura de directorios. Continuando sin guardar datos...")
                    continue
                
                print(
                    Fore.LIGHTGREEN_EX + "\n📁 Todos los reportes se guardarán en: " +
                    Fore.LIGHTCYAN_EX + f"{paths['base']}" +
                    Style.RESET_ALL
                )
                
                while True:
                    action = await show_entity_menu(entity, entity_title)
                    
                    if action == "0":
                        break
                        
                    elif action == "1":
                        print(Fore.LIGHTGREEN_EX + "\n📌 Obteniendo información general..." + Style.RESET_ALL)
                        info = await get_entity_info(entity)
                        if info:
                            await save_entity_info(info, paths)
                            await download_profile_photo(entity, paths)
                            print(
                                Fore.LIGHTGREEN_EX + "✅ Información guardada en: " +
                                Fore.LIGHTCYAN_EX + f"{paths['info']}" +
                                Style.RESET_ALL
                            )
                        else:
                            print(Fore.RED + "⚠️ No se pudo obtener información general" + Style.RESET_ALL)
                            
                    elif action == "2":
                        print(Fore.LIGHTGREEN_EX + "\n👥 Obteniendo usuarios con conteo de mensajes..." + Style.RESET_ALL)
                        users = await get_users_with_message_count(entity)
                        if users:
                            await save_users(users, paths)
                            print(
                                Fore.LIGHTGREEN_EX + "✅ Usuarios guardados en: " +
                                Fore.LIGHTCYAN_EX + f"{paths['users']}" +
                                Style.RESET_ALL
                            )
                        else:
                            print(Fore.RED + "⚠️ No se pudieron obtener usuarios" + Style.RESET_ALL)
                            
                    elif action == "3":
                        print(Fore.LIGHTGREEN_EX + "\n🔗 Obteniendo enlaces compartidos..." + Style.RESET_ALL)
                        links, stats = await get_links(entity)  # Ahora recibe ambos valores de retorno
                        if links:
                            await save_links(links, stats, paths)  # Pasar stats como segundo argumento
                            print(
                                Fore.LIGHTGREEN_EX + "✅ Enlaces guardados en: " +
                                Fore.LIGHTCYAN_EX + f"{paths['links']}" +
                                Style.RESET_ALL
                            )
                        else:
                            print(Fore.YELLOW + "ℹ️ No se encontraron enlaces compartidos" + Style.RESET_ALL)
                            
                    elif action == "4":
                        print(Fore.LIGHTGREEN_EX + "\n📸 Obteniendo fotos..." + Style.RESET_ALL)
                        photos = await get_media(entity, 'photos')
                        if photos:
                            await save_media(photos, 'photos', paths)
                            print(
                                Fore.LIGHTGREEN_EX + "✅ Fotos guardadas en: " +
                                Fore.LIGHTCYAN_EX + f"{paths['photos']}" +
                                Style.RESET_ALL
                            )
                        else:
                            print(Fore.YELLOW + "ℹ️ No se encontraron fotos" + Style.RESET_ALL)
                            
                    elif action == "5":
                        print(Fore.LIGHTGREEN_EX + "\n🎥 Obteniendo videos..." + Style.RESET_ALL)
                        videos = await get_media(entity, 'videos')
                        if videos:
                            await save_media(videos, 'videos', paths)
                            print(
                                Fore.LIGHTGREEN_EX + "✅ Videos guardados en: " +
                                Fore.LIGHTCYAN_EX + f"{paths['videos']}" +
                                Style.RESET_ALL
                            )
                        else:
                            print(Fore.YELLOW + "ℹ️ No se encontraron videos" + Style.RESET_ALL)
                            
                    elif action == "6":
                        print(Fore.LIGHTGREEN_EX + "\n🎧 Obteniendo audios..." + Style.RESET_ALL)
                        audios = await get_media(entity, 'audios')
                        if audios:
                            await save_media(audios, 'audios', paths)
                            print(
                                Fore.LIGHTGREEN_EX + "✅ Audios guardados en: " +
                                Fore.LIGHTCYAN_EX + f"{paths['audios']}" +
                                Style.RESET_ALL
                            )
                        else:
                            print(Fore.YELLOW + "ℹ️ No se encontraron audios" + Style.RESET_ALL)
                            
                    elif action == "7":
                        print(Fore.LIGHTGREEN_EX + "\n🖼️ Obteniendo stickers..." + Style.RESET_ALL)
                        stickers = await get_media(entity, 'stickers')
                        if stickers:
                            await save_media(stickers, 'stickers', paths)
                            print(
                                Fore.LIGHTGREEN_EX + "✅ Stickers guardados en: " +
                                Fore.LIGHTCYAN_EX + f"{paths['stickers']}" +
                                Style.RESET_ALL
                            )
                        else:
                            print(Fore.YELLOW + "ℹ️ No se encontraron stickers" + Style.RESET_ALL)
                            
                    elif action == "8":
                        print(Fore.LIGHTGREEN_EX + "\n📄 Obteniendo documentos..." + Style.RESET_ALL)
                        documents = await get_media(entity, 'documents')
                        if documents:
                            await save_media(documents, 'documents', paths)
                            print(
                                Fore.LIGHTGREEN_EX + "✅ Documentos guardados en: " +
                                Fore.LIGHTCYAN_EX + f"{paths['documents']}" +
                                Style.RESET_ALL
                            )
                        else:
                            print(Fore.YELLOW + "ℹ️ No se encontraron documentos" + Style.RESET_ALL)
                            
                    elif action == "9":
                        success = await collect_all_data(entity, paths)
                        if success:
                            print(
                                Fore.LIGHTGREEN_EX + "✅ Todos los datos guardados en: " +
                                Fore.LIGHTCYAN_EX + f"{paths['base']}" +
                                Style.RESET_ALL
                            )
                                
                    elif action == "10":
                        activity = await analyze_activity_patterns(entity)
                        await plot_activity(activity, f"{paths['info']}/activity_plot.png")
                        
                    
                    elif action == "11":
                        spikes_data = await detect_activity_spikes(entity)
                        if spikes_data and spikes_data['spikes']:
                            print(Fore.LIGHTGREEN_EX + "\n🔔 Análisis completado. Revisa el resumen arriba." + Style.RESET_ALL)
                        else:
                            print(Fore.YELLOW + "ℹ️ No se detectaron picos de actividad inusuales" + Style.RESET_ALL)
                    
                    elif action == "12":
                        print(Fore.LIGHTGREEN_EX + "\n🌐 Analizando dominios de enlaces..." + Style.RESET_ALL)
                        links = await get_links(entity)
                        if links:
                            domain_counter = await analyze_domains(links, paths)
                            if domain_counter:
                                risky = get_risk_domains(domain_counter)

                                print(Fore.LIGHTGREEN_EX + "\n🔍 Dominios más frecuentes:" + Style.RESET_ALL)
                                for dom, count in domain_counter.most_common(10):
                                    print(f"  {dom}: {count} apariciones")

                                if risky:
                                    print(Fore.RED + "\n⚠️ Dominios potencialmente riesgosos:" + Style.RESET_ALL)
                                    for dom, data in risky.items():
                                        flags = ", ".join(data['flags']) if isinstance(data, dict) else ""
                                        print(f"  {dom}: {data['count'] if isinstance(data, dict) else data} apariciones {flags}")
                        else:
                            print(Fore.YELLOW + "ℹ️ No se encontraron enlaces para analizar" + Style.RESET_ALL)
                    
                    
                    # Modificación para la opción 13 del menú
                    elif action == "13":
                            print(Fore.LIGHTGREEN_EX + "\n🕵️‍♂️ INICIANDO ANÁLISIS AVANZADO DE MENSAJES..." + Style.RESET_ALL)
                            analysis_results = await analyze_messages(entity, paths)
                            
                            if analysis_results:
                                # Mostrar alertas importantes basadas en los resultados
                                if any(pattern in analysis_results['patterns'] for pattern in ['onion', 'darkweb', 'btc']):
                                    print(Fore.RED + "\n🚨 ALERTA: Se encontraron elementos de alto riesgo" + Style.RESET_ALL)
                                
                                if 'peligrosas' in analysis_results['keywords']:
                                    total = sum(len(ctx) for ctx in analysis_results['keywords']['peligrosas'].values())
                                    print(Fore.YELLOW + f"⚠️ Se encontraron {total} palabras peligrosas" + Style.RESET_ALL)
    

            except Exception as e:
                print(f"⚠️ Error durante el procesamiento: {e}")
                continue
                
    except Exception as e:
        print(f"⚠️ Error crítico en la aplicación: {e}")
    finally:
        try:
            await client.disconnect()
        except:
            pass
        print("🔌 Sesión de Telegram cerrada.")

if __name__ == "__main__":
    asyncio.run(main())