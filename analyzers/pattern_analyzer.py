import re
from datetime import datetime
from collections import defaultdict
import json
import os
from core.client import client
from colorama import Fore, Style, init
init()

# Configuración avanzada de patrones
PATTERNS = {
    # Información de contacto
    'emails': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
    'phones': r'(?:\+)?(?:[0-9] ?){6,14}[0-9]',
    
    # Criptomonedas
    'btc': r'\b[13][a-km-zA-HJ-NP-Z1-9]{25,34}\b',
    'eth': r'\b0x[a-fA-F0-9]{40}\b',
    'xmr': r'\b4[0-9AB][1-9A-HJ-NP-Za-km-z]{93}\b',
    
    # Datos financieros
    'cbu': r'\b[0-9]{22}\b',
    'cvu': r'\b[0-9]{22}\b',
    'iban': r'\b[A-Z]{2}\d{2}[A-Z0-9]{11,30}\b',
    'credit_card': r'\b(?:\d[ -]*?){13,16}\b',
    
    # Documentos personales
    'dni': r'\b[0-9]{7,8}\b',
    'cuit': r'\b(20|23|27|30|33)[0-9]{8}[0-9]\b',
    'cuil': r'\b(20|23|27|30|33)[0-9]{8}[0-9]\b',
    
    # Enlaces especiales
    'onion': r'\b[a-z2-7]{16,56}\.onion\b',
    'darkweb': r'\b(?:https?://)?(?:www\.)?[a-z2-7]{16,56}\.onion\b',
    'urls': r'(https?://[^\s]+)',
    
    # Otra información sensible
    'ipv4': r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b',
    'ipv6': r'\b(?:[A-F0-9]{1,4}:){7}[A-F0-9]{1,4}\b',
    'mac': r'\b(?:[0-9A-Fa-f]{2}[:-]){5}(?:[0-9A-Fa-f]{2})\b'
}

# Listas de palabras clave
KEYWORDS = {
    'peligrosas': ['contraseña', 'clave', 'acceso', 'hack', 'exploit', 'virus', 'malware', 
                  'phishing', 'estafa', 'fraude', 'suicidio', 'droga', 'arma', 'pornografía'],
    
    'importantes': ['urgente', 'importante', 'confidencial', 'secreto', 'privado', 
                   'reservado', 'oficial', 'legal', 'judicial', 'policía'],
    
    'temas_interes': ['perro', 'gato', 'animal', 'paisaje', 'naturaleza', 'arte', 
                     'música', 'deporte', 'tecnología', 'ciencia']
}

def format_entry_header(pattern_type, value, count):
    """Formatea el encabezado de cada entrada"""
    emoji = {
        'urls': '🌐',
        'onion': '🧅',
        'darkweb': '🕶️',
        'emails': '📧',
        'btc': '₿',
        'eth': 'Ξ',
        'xmr': '🪙',
        'credit_card': '💳'
    }.get(pattern_type, '🔍')
    
    return f"\n{emoji} {pattern_type.upper()} #{count}\n{'='*40}"

def format_user_info(sender_id, username=None, first_name=None):
    """Formatea la información del usuario"""
    user_info = f"👤 ID Usuario: {sender_id}"
    if username:
        user_info += f" (@{username})"
    elif first_name:
        user_info += f" ({first_name})"
    return user_info

async def analyze_messages(entity, paths, limit=5000):
    """
    Analiza mensajes buscando patrones sensibles y palabras clave
    Genera reportes detallados con información contextual mejorada
    """
    if not paths or 'info' not in paths:
        print(Fore.RED + "Error: No se encontró el directorio para guardar reportes" + Style.RESET_ALL)
        return None
    
    output_dir = paths['info']
    os.makedirs(output_dir, exist_ok=True)
    
    # Estructuras para almacenar resultados
    results = {
        'patterns': defaultdict(lambda: defaultdict(list)),
        'keywords': defaultdict(lambda: defaultdict(list)),
        'metadata': {
            'total_messages': 0,
            'analyzed_messages': 0,
            'start_time': datetime.now().isoformat(),
            'entity': str(entity)
        }
    }
    
    print(Fore.LIGHTGREEN_EX + f"\n🔍 Analizando hasta {limit} mensajes..." + Style.RESET_ALL)
    
    try:
        async for message in client.iter_messages(entity, limit=limit):
            results['metadata']['total_messages'] += 1
            
            if not message.text:
                continue
                
            results['metadata']['analyzed_messages'] += 1
            msg_date = message.date.strftime('%Y-%m-%d %H:%M:%S')
            sender = getattr(message.sender, 'username', None)
            first_name = getattr(message.sender, 'first_name', None)
            sender_id = message.sender_id
            
            # Buscar todos los patrones
            for pattern_name, pattern in PATTERNS.items():
                matches = re.findall(pattern, message.text, re.IGNORECASE)
                if matches:
                    for match in matches:
                        results['patterns'][pattern_name][match].append({
                            'sender': sender,
                            'first_name': first_name,
                            'sender_id': sender_id,
                            'date': msg_date,
                            'message_id': message.id,
                            'context': message.text[:100] + '...' if len(message.text) > 100 else message.text
                        })
            
            # Buscar palabras clave
            for category, words in KEYWORDS.items():
                for word in words:
                    if re.search(rf'\b{word}\b', message.text, re.IGNORECASE):
                        results['keywords'][category][word].append({
                            'sender': sender,
                            'first_name': first_name,
                            'sender_id': sender_id,
                            'date': msg_date,
                            'message_id': message.id,
                            'context': message.text[:100] + '...' if len(message.text) > 100 else message.text
                        })
        
        # Generar reportes
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_files = []
        
        # 1. Reporte completo en JSON
        json_report = os.path.join(output_dir, f"message_analysis_{timestamp}.json")
        with open(json_report, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        report_files.append(json_report)
        
        # 2. Reporte resumido en TXT (formato mejorado)
        txt_report = os.path.join(output_dir, f"message_analysis_{timestamp}.txt")
        with open(txt_report, 'w', encoding='utf-8') as f:
            f.write("=== ANÁLISIS AVANZADO DE MENSAJES ===\n\n")
            f.write(f"📅 Fecha de análisis: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"🔍 Entidad analizada: {results['metadata']['entity']}\n")
            f.write(f"📊 Mensajes totales: {results['metadata']['total_messages']}\n")
            f.write(f"💬 Mensajes analizados: {results['metadata']['analyzed_messages']}\n")
            f.write("="*40 + "\n\n")
            
            # Sección de patrones encontrados
            f.write("🔎 PATRONES ENCONTRADOS:\n")
            for pattern_type, matches in results['patterns'].items():
                f.write(f"\n📌 {pattern_type.upper()} ({len(matches)} coincidencias)\n")
                
                count = 1
                for value, contexts in matches.items():
                    f.write(format_entry_header(pattern_type, value, count))
                    f.write(f"\n• Valor: {value}\n")
                    
                    for ctx in contexts[:3]:  # Mostrar hasta 3 contextos
                        f.write(f"\n📩 ID Mensaje: {ctx['message_id']}\n")
                        f.write(format_user_info(ctx['sender_id'], ctx['sender'], ctx['first_name']) + "\n")
                        f.write(f"📅 Fecha: {ctx['date']}\n")
                        f.write(f"💬 Contexto: \"{ctx['context']}\"\n")
                    
                    if len(contexts) > 3:
                        f.write(f"\n🔄 {len(contexts)-3} apariciones más...\n")
                    f.write("="*40 + "\n")
                    count += 1
            
            # Sección de palabras clave
            f.write("\n\n🔎 PALABRAS CLAVE ENCONTRADAS:\n")
            for category, words in results['keywords'].items():
                f.write(f"\n📌 {category.upper()}:\n")
                
                for word, contexts in words.items():
                    f.write(f"\n• Palabra: '{word}' ({len(contexts)} apariciones)\n")
                    f.write("─"*30 + "\n")
                    
                    for ctx in contexts[:2]:  # Mostrar hasta 2 contextos
                        f.write(f"📩 ID Mensaje: {ctx['message_id']}\n")
                        f.write(format_user_info(ctx['sender_id'], ctx['sender'], ctx['first_name']) + "\n")
                        f.write(f"📅 Fecha: {ctx['date']}\n")
                        f.write(f"💬 Contexto: \"{ctx['context']}\"\n")
                        f.write("─"*30 + "\n")
                    
                    if len(contexts) > 2:
                        f.write(f"🔄 {len(contexts)-2} apariciones más...\n")
        
        report_files.append(txt_report)
        
        # 3. CSV para análisis externo
        csv_report = os.path.join(output_dir, f"message_analysis_{timestamp}.csv")
        with open(csv_report, 'w', encoding='utf-8') as f:
            f.write("category,type,value,count,message_id,user_id,username,first_name,date,context\n")
            
            # Escribir patrones
            for pattern, matches in results['patterns'].items():
                for value, contexts in matches.items():
                    first_ctx = contexts[0]
                    f.write(f"pattern,{pattern},{value},{len(contexts)},{first_ctx['message_id']},{first_ctx['sender_id']},")
                    f.write(f"\"{first_ctx['sender'] or ''}\",\"{first_ctx['first_name'] or ''}\",")
                    f.write(f"\"{first_ctx['date']}\",\"{first_ctx['context'].replace('"', "'")}\"\n")
            
            # Escribir palabras clave
            for category, words in results['keywords'].items():
                for word, contexts in words.items():
                    first_ctx = contexts[0]
                    f.write(f"keyword,{category},{word},{len(contexts)},{first_ctx['message_id']},{first_ctx['sender_id']},")
                    f.write(f"\"{first_ctx['sender'] or ''}\",\"{first_ctx['first_name'] or ''}\",")
                    f.write(f"\"{first_ctx['date']}\",\"{first_ctx['context'].replace('"', "'")}\"\n")
        
        report_files.append(csv_report)
        
        # Mostrar resumen en consola
        print(Fore.LIGHTGREEN_EX + "\n✅ ANÁLISIS COMPLETADO" + Style.RESET_ALL)
        print(f"📊 Mensajes analizados: {results['metadata']['analyzed_messages']}")
        
        # Resumen de patrones encontrados
        print("\n🔍 PATRONES ENCONTRADOS:")
        for pattern, matches in results['patterns'].items():
            total = sum(len(v) for v in matches.values())
            print(f"  • {pattern}: {total} coincidencias")
        
        # Resumen de palabras clave
        print("\n🔍 PALABRAS CLAVE ENCONTRADAS:")
        for category, words in results['keywords'].items():
            total = sum(len(v) for v in words.values())
            print(f"  • {category}: {total} coincidencias")
        
        print(Fore.LIGHTGREEN_EX + "\n📄 REPORTES GUARDADOS EN:" + Style.RESET_ALL)
        for file in report_files:
            print(f"  • {file}")
        
        return results
        
    except Exception as e:
        print(Fore.RED + f"\n⚠️ ERROR DURANTE EL ANÁLISIS: {str(e)}" + Style.RESET_ALL)
        return None