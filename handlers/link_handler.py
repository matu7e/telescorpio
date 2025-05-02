import re
import os
from datetime import datetime
from collections import defaultdict
from core.client import client 
from telethon.tl.types import MessageEntityUrl
from core.progress import show_progress

# Expresión regular mejorada para detectar URLs
URL_PATTERN = re.compile(
    r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|'
    r'[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
)

# Patrones para clasificar enlaces de Telegram
TELEGRAM_PATTERNS = {
    'user_profile': re.compile(r'(?:t\.me|telegram\.me)/([^/]+)$'),
    'web_user': re.compile(r'web\.telegram\.org/[kz]/#@([^/]+)'),
    'group_invite': re.compile(r't\.me/joinchat/([^/]+)'),
    'phone_number': re.compile(r't\.me/\+\d+'),
    'channel_preview': re.compile(r'(?:t\.me|telegram\.me)/s/([^/]+)'),
    'bot_command': re.compile(r't\.me/[^/]+\?start=[^/]+')
}

async def get_links(entity, limit=500):
    """Obtiene y clasifica enlaces compartidos en la entidad"""
    links = []
    stats = {
        'total': 0,
        'by_source': {'entity': 0, 'text': 0},
        'telegram': defaultdict(int),
        'domains': defaultdict(int),
        'unique': set(),
        'duplicates': 0
    }
    
    try:
        print("\n🔗 Buscando y clasificando enlaces...")
        total_messages = 0
        last_progress = 0
        
        async for message in client.iter_messages(entity, limit=limit):
            total_messages += 1
            progress = int((total_messages / limit) * 100)
            if progress != last_progress:
                show_progress(total_messages, limit, prefix="Progreso:", suffix=f"{total_messages}/{limit} mensajes")
                last_progress = progress
            
            try:
                # Detección por entidades (metadatos)
                if message.entities:
                    for entity in message.entities:
                        if isinstance(entity, MessageEntityUrl):
                            link = message.text[entity.offset:entity.offset + entity.length]
                            stats['by_source']['entity'] += 1
                            process_link(link, message, links, stats)
                
                # Detección por regex en texto plano
                if message.text:
                    found_urls = URL_PATTERN.findall(message.text)
                    for url in found_urls:
                        stats['by_source']['text'] += 1
                        process_link(url, message, links, stats)
                            
            except Exception as e:
                continue
        
        stats['total'] = len(links)
        stats['unique_count'] = len(stats['unique'])
        stats['duplicates'] = stats['total'] - stats['unique_count']
        
        print("\n📊 Estadísticas de enlaces:")
        print(f"• Total: {stats['total']}")
        print(f"• Únicos: {stats['unique_count']}")
        print(f"• Duplicados: {stats['duplicates']}")
        print(f"• Por origen: Entidades={stats['by_source']['entity']}, Texto={stats['by_source']['text']}")
        
        if stats['telegram']:
            print("\n🔍 Enlaces de Telegram clasificados:")
            for category, count in stats['telegram'].items():
                print(f"• {category.replace('_', ' ').title()}: {count}")
        
        if stats['domains']:
            print("\n🌐 Dominios más frecuentes:")
            for domain, count in sorted(stats['domains'].items(), key=lambda x: x[1], reverse=True)[:3]:
                print(f"• {domain}: {count} apariciones")
        
        return links, stats
    except Exception as e:
        print(f"\n⚠️ Error al obtener enlaces: {e}")
        return [], {}

def process_link(url, message, links, stats):
    """Procesa y clasifica un enlace encontrado"""
    link_info = create_link_info(url, message)
    is_duplicate = url in stats['unique']
    
    if not is_duplicate:
        stats['unique'].add(url)
    else:
        stats['duplicates'] += 1
    
    # Clasificar enlaces de Telegram
    if 't.me' in url or 'telegram.me' in url or 'web.telegram.org' in url:
        classified = False
        for category, pattern in TELEGRAM_PATTERNS.items():
            if pattern.search(url):
                link_info['telegram_type'] = category
                stats['telegram'][category] += 1
                classified = True
                break
        
        if not classified:
            link_info['telegram_type'] = 'other_telegram'
            stats['telegram']['other_telegram'] += 1
    
    # Estadísticas de dominios
    domain = extract_domain(url)
    if domain:
        stats['domains'][domain] += 1
    
    links.append(link_info)

def extract_domain(url):
    """Extrae el dominio principal de una URL"""
    domain = re.search(r'https?://([^/]+)', url)
    return domain.group(1) if domain else None

def create_link_info(url, message):
    """Crea el diccionario con la información del enlace"""
    return {
        'url': url,
        'sender_id': getattr(message, 'sender_id', 'Desconocido'),
        'date': getattr(message, 'date', datetime.now()).strftime('%Y-%m-%d %H:%M:%S'),
        'message_id': getattr(message, 'id', 'N/A'),
        'source': 'entity' if hasattr(message, 'entities') else 'text',
        'telegram_type': None
    }

async def save_links(links, stats, paths):
    """Guarda los enlaces encontrados y las estadísticas"""
    if not paths:
        print("⚠️ Rutas no definidas")
        return None
        
    try:
        # Guardar enlaces en CSV
        csv_file = os.path.join(paths['links'], 'enlaces.csv')
        with open(csv_file, 'w', encoding='utf-8') as f:
            f.write("URL,ID Mensaje,ID Usuario,Fecha,Origen,Tipo Telegram\n")
            for link in links:
                f.write(f"{link.get('url', 'N/A')},"
                        f"{link.get('message_id', 'N/A')},"
                        f"{link.get('sender_id', 'N/A')},"
                        f"{link.get('date', 'N/A')},"
                        f"{link.get('source', 'N/A')},"
                        f"{link.get('telegram_type', 'N/A')}\n")
        
        # Guardar reporte detallado
        detailed_file = os.path.join(paths['links'], 'reporte_detallado.txt')
        with open(detailed_file, 'w', encoding='utf-8') as f:
            # Sección de estadísticas
            f.write("📊 REPORTE DE ENLACES 📊\n")
            f.write("="*40 + "\n\n")
            f.write("ESTADÍSTICAS GENERALES\n")
            f.write("-"*40 + "\n")
            f.write(f"• Total de enlaces: {stats['total']}\n")
            f.write(f"• Enlaces únicos: {stats['unique_count']}\n")
            f.write(f"• Enlaces duplicados: {stats['duplicates']}\n")
            f.write(f"• Detectados por entidades: {stats['by_source']['entity']}\n")
            f.write(f"• Detectados en texto: {stats['by_source']['text']}\n\n")
            
            # Sección Telegram
            if stats['telegram']:
                f.write("CLASIFICACIÓN DE ENLACES TELEGRAM\n")
                f.write("-"*40 + "\n")
                for category, count in stats['telegram'].items():
                    f.write(f"• {category.replace('_', ' ').title()}: {count}\n")
                f.write("\n")
            
            # Top dominios
            if stats['domains']:
                f.write("DOMINIOS MÁS FRECUENTES\n")
                f.write("-"*40 + "\n")
                for domain, count in sorted(stats['domains'].items(), key=lambda x: x[1], reverse=True)[:3]:
                    f.write(f"• {domain}: {count} apariciones\n")
                f.write("\n")
            
            # Listado detallado de enlaces
            f.write("DETALLE DE ENLACES\n")
            f.write("="*40 + "\n")
            for idx, link in enumerate(links, 1):
                f.write(f"🔗 ENLACE #{idx}\n")
                f.write("-"*30 + "\n")
                f.write(f"🌐 URL: {link.get('url', 'N/A')}\n")
                f.write(f"📌 Tipo Telegram: {link.get('telegram_type', 'No aplica')}\n")
                f.write(f"📩 ID Mensaje: {link.get('message_id', 'N/A')}\n")
                f.write(f"👤 ID Usuario: {link.get('sender_id', 'N/A')}\n")
                f.write(f"📅 Fecha: {link.get('date', 'N/A')}\n")
                f.write(f"🔍 Origen: {link.get('source', 'N/A')}\n\n")
        
        return csv_file, detailed_file
    except Exception as e:
        print(f"⚠️ Error al guardar enlaces: {e}")
        return None