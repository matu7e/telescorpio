from datetime import datetime
import matplotlib.pyplot as plt
from collections import defaultdict
import numpy as np
from core.client import client
from core.progress import show_progress

async def get_date_range(entity):
    """
    Solicita al usuario un rango de fechas y devuelve tupla (start_date, end_date) o None
    """
    print("\n⏳ Configuración del análisis temporal:")
    print("1. Analizar TODO el historial (sin límites)")
    print("2. Especificar rango de fechas (YYYY-MM-DD)")
    date_choice = input("Seleccione opción (1/2): ")
    
    if date_choice == "2":
        try:
            start_date = input("Fecha inicial (YYYY-MM-DD): ")
            end_date = input("Fecha final (YYYY-MM-DD): ")
            
            # Convertir a datetime naive primero
            start_date = datetime.strptime(start_date, "%Y-%m-%d")
            end_date = datetime.strptime(end_date, "%Y-%m-%d")
            
            # Obtener la zona horaria de un mensaje de ejemplo
            async for message in client.iter_messages(entity, limit=1):
                tz = message.date.tzinfo  # Zona horaria de los mensajes
                break
            
            # Aplicar la misma zona horaria a las fechas ingresadas
            start_date = start_date.replace(tzinfo=tz)
            end_date = end_date.replace(tzinfo=tz)
            
            if end_date < start_date:
                print("⚠️ La fecha final es anterior a la inicial. Se intercambiarán.")
                start_date, end_date = end_date, start_date
                
            print(f"🔍 Filtrando mensajes entre {start_date.date()} y {end_date.date()}")
            return start_date, end_date
        except ValueError:
            print("⚠️ Formato de fecha inválido. Analizando todo el historial")
    
    return None

async def analyze_activity_patterns(entity):
    """
    Analiza patrones horarios de actividad con filtrado por fecha
    """
    date_filter = await get_date_range(entity)
    
    hourly_activity = defaultdict(int)
    total_messages = 0
    processed = 0
    
    # Configurar progreso
    if date_filter:
        total_count = None  # No sabemos cuántos mensajes hay en el rango
        print("\n📊 Analizando patrones de actividad horaria...")
    else:
        total_count = min((await client.get_messages(entity, limit=0)).total, 5000)
        print("\n📊 Analizando patrones de actividad horaria...")
        show_progress(0, total_count, prefix="Progreso:", suffix="0/0 mensajes")
    
    async for message in client.iter_messages(entity, limit=5000):
        if message.date:
            # Aplicar filtro de fecha si existe
            if date_filter:
                if not (date_filter[0] <= message.date <= date_filter[1]):
                    continue
            
            hour = message.date.hour
            hourly_activity[hour] += 1
            total_messages += 1
        
        if total_count:  # Solo mostrar progreso si sabemos el total
            processed += 1
            show_progress(processed, total_count, 
                        prefix="Progreso:", 
                        suffix=f"{processed}/{total_count} mensajes")

    if not hourly_activity:
        print("\n⚠️ No se encontraron mensajes en el rango especificado")
        return None

    sorted_hours = dict(sorted(hourly_activity.items()))
    avg_messages = total_messages / 24 if total_messages > 0 else 0
    peak_hour, peak_count = max(hourly_activity.items(), key=lambda x: x[1]) if hourly_activity else (-1, 0)
    quiet_hour, quiet_count = min(hourly_activity.items(), key=lambda x: x[1]) if hourly_activity else (-1, 0)
    
    # Mostrar resumen estadístico
    date_range_info = f"entre {date_filter[0].date()} y {date_filter[1].date()}" if date_filter else "en todo el historial"
    print(f"\n📌 Resumen de actividad {date_range_info}:")
    print(f"• Total mensajes analizados: {total_messages}")
    print(f"• Promedio mensajes/hora: {avg_messages:.1f}")
    print(f"• Hora pico: {peak_hour}:00 ({peak_count} mensajes)")
    print(f"• Hora más tranquila: {quiet_hour}:00 ({quiet_count} mensajes)")
    
    return {
        'hourly': sorted_hours,
        'metrics': {
            'total': total_messages,
            'avg': avg_messages,
            'peak': {'hour': peak_hour, 'count': peak_count},
            'quiet': {'hour': quiet_hour, 'count': quiet_count}
        },
        'date_range': date_filter if date_filter else "Todo el historial"
    }

async def detect_activity_spikes(entity, threshold=3):
    """
    Detecta picos de actividad con filtrado por fecha
    """
    date_filter = await get_date_range(entity)
    
    daily_activity = defaultdict(int)
    processed = 0
    
    # Configuración diferente según elección
    if date_filter:
        total_count = None  # No sabemos cuántos hay en el rango
    else:
        total_count = (await client.get_messages(entity, limit=0)).total
    
    print("\n📈 Detectando picos de actividad...")
    
    async for message in client.iter_messages(entity, limit=None):  # Sin límite artificial
        if message.date:
            # Aplicar filtro de fecha si existe
            if date_filter:
                if not (date_filter[0] <= message.date <= date_filter[1]):
                    continue
            
            day = message.date.strftime('%Y-%m-%d')
            daily_activity[day] += 1
        
        if total_count:  # Solo mostrar progreso si sabemos el total
            processed += 1
            if processed % 100 == 0:  # Actualizar cada 100 mensajes
                show_progress(processed, total_count,
                            prefix="Progreso:",
                            suffix=f"{processed}/{total_count} mensajes")

    # Resultados
    if not daily_activity:
        print("\n⚠️ No se encontraron mensajes en el rango especificado")
        return None

    values = list(daily_activity.values())
    mean = np.mean(values)
    std = np.std(values)
    
    spikes = [(day, count) for day, count in daily_activity.items() 
              if count > mean + threshold*std]
    
    date_range_info = f"entre {date_filter[0].date()} y {date_filter[1].date()}" if date_filter else "en todo el historial"
    print(f"\n📌 Resumen estadístico {date_range_info}:")
    print(f"• Días analizados: {len(daily_activity)}")
    print(f"• Mensajes totales: {sum(values)}")
    print(f"• Promedio mensajes/día: {mean:.1f} ± {std:.1f}")
    print(f"• Umbral para picos: > {mean + threshold*std:.1f} mensajes")
    
    if spikes:
        print("\n🚨 Picos detectados (ordenados por fecha):")
        for date, count in sorted(spikes):
            print(f"  - {date}: {count} mensajes")
    else:
        print("\n✅ No se detectaron picos significativos")
    
    return {
        'spikes': sorted(spikes),
        'stats': {
            'date_range': date_filter if date_filter else "Todo el historial",
            'mean_activity': mean,
            'std_dev': std,
            'threshold': mean + threshold*std
        }
    }

async def plot_activity(activity_data, output_path):
    """Genera gráfico de actividad"""
    if not activity_data:
        print("⚠️ No hay datos para graficar")
        return
    
    plt.figure(figsize=(12, 6))
    
    if 'hourly' in activity_data:  # Datos de análisis horario
        hours = list(activity_data['hourly'].keys())
        counts = list(activity_data['hourly'].values())
        
        plt.bar(hours, counts, color='skyblue')
        plt.title('Actividad por Hora del Día')
        plt.xlabel('Hora del día')
        plt.ylabel('Número de mensajes')
        plt.xticks(range(0, 24))
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        
        # Resaltar hora pico
        peak = activity_data['metrics']['peak']
        plt.axvline(x=peak['hour'], color='red', linestyle='--', alpha=0.5)
        plt.text(peak['hour'], peak['count'], f"Pico: {peak['hour']}:00", 
                ha='center', va='bottom', color='red')
    
    elif 'spikes' in activity_data:  # Datos de picos de actividad
        dates = [datetime.strptime(d[0], '%Y-%m-%d') for d in activity_data['spikes']]
        counts = [d[1] for d in activity_data['spikes']]
        
        plt.plot(dates, counts, 'ro-')
        plt.title('Picos de Actividad')
        plt.xlabel('Fecha')
        plt.ylabel('Número de mensajes')
        plt.grid(True, linestyle='--', alpha=0.7)
        
        # Línea de umbral
        threshold = activity_data['stats']['threshold']
        plt.axhline(y=threshold, color='orange', linestyle='--', label=f'Umbral: {threshold:.1f}')
        plt.legend()
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✅ Gráfico guardado en {output_path}")