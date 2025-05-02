from colorama import Fore, Style

async def show_entity_menu(entity, entity_name):
    """Muestra el menú para una entidad específica con estilo hacker"""

    try:
        print("\n" + Fore.GREEN + "=" * 100)
        
        title = f"[💀] ACCEDIENDO A: {entity_name.upper()} [💀]"
        print(Fore.GREEN + title.center(100))
        
        print(Fore.GREEN + "=" * 100)

        menu_items = [
            ("\t[1]", "Información general"),
            ("[2]", "Listado de usuarios"),
            ("[3]", "Enlaces compartidos"),
            ("\t[4]", "Descargar imágenes"),
            ("[5]", "Descargar videos"),
            ("[6]", "Descargar audios"),
            ("\t[7]", "Descargar Stickers"),
            ("[8]", "Descargar Archivos"),
            ("[9]", "Full recolección"),
            ("\t[10]", "Patrones Horarios"),
            ("[11]", "Estadísticas"),
            ("[12]", "Análisis de dominios"),
            ("\t[13]", "Patrones en mensj"),
            ("[0]", "Menú principal")
        ]

        col_width = 36   # Más espacio por la tabulación extra

        for i in range(0, len(menu_items), 3):
            row = menu_items[i:i+3]
            line = "\t"  # Agregamos una tabulación inicial
            for number, description in row:
                strong_number = Fore.LIGHTCYAN_EX + number + Fore.CYAN
                text = f"{strong_number} {description}"
                line += text.ljust(col_width)
            print(Fore.GREEN + line.strip())

        print(Fore.GREEN + "=" * 100)

        while True:
            choice = input("\n\033[95m[?]\033[0m Seleccione una opción >>> ").strip()
            if choice in [str(i) for i in range(14)]:
                return choice
            print("\033[91m[⚠️] Opción inválida. Intente nuevamente.\033[0m")

    except Exception as e:
        print(f"\033[91m[⚠️] Error al mostrar menú de entidad: {e}\033[0m")
        return "0"
