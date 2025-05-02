from urllib.parse import urlparse
from collections import Counter
from core.client import client
import tldextract
import asyncio
import json
import os
from colorama import Fore, Style
from datetime import datetime



async def analyze_domains(links, paths):
    """
    Analiza dominios de enlaces compartidos co   funcionalidad extendida
    Retorna: dict con estadísticas completas y guarda archivos de reporte
    en el directorio de enlaces (paths['links'])
    """
    # Verificar si tenemos el directorio de enlaces
    if not paths or 'links' not in paths:
        print(Fore.RED + "Error: No se encontró el directorio para guardar enlaces" + Style.RESET_ALL)
        return None
    
    output_dir = paths['links']
    
    # Preparar estructuras de datos
    domains = []
    full_urls = []
    domain_counter = Counter()
    tld_counter = Counter()
    protocol_counter = Counter()
    path_lengths = []
    suspicious_domains = set()
    
    # Lista de TLDs sospechosos
    risky_tlds = ['.xyz', '.top', '.gq', '.ml', '.tk', '.club', 
                 '.bid', '.win', '.loan', '.men', '.date', '.wang']
    
    # Lista de palabras clave sospechosas en dominios
    suspicious_keywords = ['free', 'click', 'win', 'prize', 'offer',
                         'discount', 'deal', 'bonus', 'cash', 'reward']
    
    for link in links:
        try:
            url = link['url']
            full_urls.append(url)
            
            # Extraer información de la URL
            parsed = urlparse(url)
            ext = tldextract.extract(url)
            domain = f"{ext.domain}.{ext.suffix}"
            
            # Contar dominios y TLDs
            domains.append(domain)
            domain_counter[domain] += 1
            tld_counter[f".{ext.suffix}"] += 1
            protocol_counter[parsed.scheme] += 1
            
            # Analizar longitud de paths
            path_lengths.append(len(parsed.path.split('/')))
            
            # Detección de dominios sospechosos
            is_suspicious = (
                any(tld in domain for tld in risky_tlds) or
                any(keyword in ext.domain.lower() for keyword in suspicious_keywords) or
                (len(ext.domain) > 15 and sum(c.isdigit() for c in ext.domain) > 3)
            )
            
            if is_suspicious:
                suspicious_domains.add(domain)
                
        except Exception as e:
            continue
    
    # Generar estadísticas
    stats = {
        'total_links': len(links),
        'unique_domains': len(domain_counter),
        'most_common_domains': list(domain_counter.most_common(10)),
        'most_common_tlds': list(tld_counter.most_common(5)),
        'protocol_distribution': dict(protocol_counter),
        'avg_path_length': sum(path_lengths)/len(path_lengths) if path_lengths else 0,
        'suspicious_domains': list(suspicious_domains),
        'suspicious_domain_count': len(suspicious_domains),
        'analysis_date': datetime.now().isoformat()
    }
    
    # Generar archivos de reporte
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    try:
        # 1. Reporte completo en JSON
        json_report = os.path.join(output_dir, f"domain_analysis_{timestamp}.json")
        with open(json_report, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)
        
        # 2. Reporte legible en texto
        txt_report = os.path.join(output_dir, f"domain_analysis_{timestamp}.txt")
        with open(txt_report, 'w', encoding='utf-8') as f:
            f.write("=== ANÁLISIS DE DOMINIOS ===\n\n")
            f.write(f"📊 Total de enlaces analizados: {stats['total_links']}\n")
            f.write(f"🌐 Dominios únicos encontrados: {stats['unique_domains']}\n")
            f.write(f"⚠️ Dominios sospechosos detectados: {stats['suspicious_domain_count']}\n\n")
            
            f.write("\nTOP 10 DOMINIOS MÁS FRECUENTES:\n")
            for domain, count in stats['most_common_domains']:
                suspicious_flag = " (⚠️ SOSPECHOSO)" if domain in stats['suspicious_domains'] else ""
                f.write(f"• {domain}: {count} enlaces{suspicious_flag}\n")
            
            f.write("\nTOP 5 TLDs MÁS FRECUENTES:\n")
            for tld, count in stats['most_common_tlds']:
                f.write(f"• {tld}: {count} enlaces\n")
            
            f.write("\nDISTRIBUCIÓN DE PROTOCOLOS:\n")
            for proto, count in stats['protocol_distribution'].items():
                f.write(f"• {proto}: {count} enlaces\n")
            
            f.write(f"\nLONGITUD PROMEDIO DE PATH: {stats['avg_path_length']:.1f}\n")
            
            if stats['suspicious_domains']:
                f.write("\n🚨 DOMINIOS SOSPECHOSOS DETECTADOS:\n")
                for domain in stats['suspicious_domains']:
                    f.write(f"• {domain} ({domain_counter[domain]} enlaces)\n")
        
        # 3. CSV de dominios para análisis externo
        csv_report = os.path.join(output_dir, f"domains_{timestamp}.csv")
        with open(csv_report, 'w', encoding='utf-8') as f:
            f.write("domain,count,is_suspicious\n")
            for domain, count in domain_counter.most_common():
                is_susp = "1" if domain in suspicious_domains else "0"
                f.write(f"{domain},{count},{is_susp}\n")
        
        print(Fore.LIGHTGREEN_EX + "✅ Reportes de dominios guardados en: " +
              Fore.LIGHTCYAN_EX + f"{output_dir}" + Style.RESET_ALL)
        print(Fore.LIGHTCYAN_EX + f"• {json_report}")
        print(f"• {txt_report}")
        print(f"• {csv_report}" + Style.RESET_ALL)
        
        return domain_counter
        
    except Exception as e:
        print(Fore.RED + f"⚠️ Error al guardar reportes: {e}" + Style.RESET_ALL)
        return None


def get_risk_domains(domain_counter, extended=False):
    """
    Identifica dominios sospechosos con opción extendida
    """
    risky_tlds = ['.xyz', '.top', '.gq', '.ml', '.tk', '.club', 
                 '.bid', '.win', '.loan', '.men', '.date', '.wang']
    
    suspicious_keywords = ['free', 'click', 'win', 'prize', 'offer', 
                         'discount', 'deal', 'bonus', 'cash', 'reward']
    
    if not extended:
        return {dom: count for dom, count in domain_counter.items()
                if any(tld in dom for tld in risky_tlds)}
    
    # Análisis extendido
    risky_domains = {}
    for domain, count in domain_counter.items():
        ext = tldextract.extract(domain)
        
        # Verificar TLD riesgoso
        tld_risk = any(tld in domain for tld in risky_tlds)
        
        # Verificar palabras clave sospechosas en el dominio
        keyword_risk = any(keyword in ext.domain.lower() for keyword in suspicious_keywords)
        
        # Verificar dominios con muchos números (posiblemente aleatorios)
        number_risk = len(ext.domain) > 15 and sum(c.isdigit() for c in ext.domain) > 3
        
        if tld_risk or keyword_risk or number_risk:
            risky_domains[domain] = {
                'count': count,
                'flags': []
            }
            if tld_risk: risky_domains[domain]['flags'].append('risky_tld')
            if keyword_risk: risky_domains[domain]['flags'].append('suspicious_keyword')
            if number_risk: risky_domains[domain]['flags'].append('high_number_count')
    
    return risky_domains