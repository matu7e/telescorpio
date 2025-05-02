def show_progress(current, total, prefix="", suffix=""):
    """Muestra una barra de progreso en la consola"""
    bar_length = 40
    progress = float(current) / float(total) if total > 0 else 0
    arrow = '=' * int(round(progress * bar_length) - 1) + '>'
    spaces = ' ' * (bar_length - len(arrow))
    
    print(f"\r{prefix} [{arrow + spaces}] {int(progress * 100)}% {suffix}", end='')
    if current == total: 
        print()