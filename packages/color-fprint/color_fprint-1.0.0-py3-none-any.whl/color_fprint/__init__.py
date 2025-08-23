import re

def cprint(text, **args):
    """
    Imprime texto en consola con colores, permitiendo resaltar variables dentro de llaves.

    El texto puede contener variables o expresiones entre llaves (por ejemplo: {nombre}, {datos["edad"]}, {a + b}).
    Las variables se reemplazan por su valor en el contexto llamador y se colorean con `var_color`.
    El resto del texto se imprime con el color `text_color`.

    Args:
        text (str): Texto a imprimir, puede contener variables/expresiones entre llaves.
        text_color (str): Color del texto general. Opciones: black, red, green, yellow, blue, magenta, cyan, white.
        var_color (str): Color de las variables/expresiones. Opciones: black, red, green, yellow, blue, magenta, cyan, white.
        bright (bool): Si es True, usa los colores "intensos" (91, 92, etc). Por defecto es False (colores normales 31, 32, etc).

    Ejemplo:
        nombre = 'Juan'
        edad = 30
        cprint('Mi nombre es {nombre} y tengo {edad} años', text_color='yellow', var_color='blue')

    También soporta expresiones:
        a = 5
        b = 3
        cprint('Suma: {a + b}', text_color='green', var_color='magenta')
    """

    # Mapeo de colores a códigos ANSI
    text_color = args.get('text_color', 'white')
    var_color = args.get('var_color')
    bright = args.get('bright', False)
    if bright:
        colors = {
            'black': '\033[90m',
            'red': '\033[91m',
            'green': '\033[92m',
            'yellow': '\033[93m',
            'blue': '\033[94m',
            'magenta': '\033[95m',
            'cyan': '\033[96m',
            'white': '\033[97m',
            'reset': '\033[0m'
        }
    else:
        colors = {
            'black': '\033[30m',
            'red': '\033[31m',
            'green': '\033[32m',
            'yellow': '\033[33m',
            'blue': '\033[34m',
            'magenta': '\033[35m',
            'cyan': '\033[36m',
            'white': '\033[37m',
            'reset': '\033[0m'
        }
    var_color = text_color if var_color is None else var_color
    def replacer(match):
        expr = match.group(1)
        try:
            # Evalúa la expresión usando el contexto llamador
            value = str(eval(expr, {}, kwargs))
        except Exception:
            value = '{' + expr + '}'
        return (
            colors.get(var_color, colors['cyan']) + value +
            colors.get(text_color, colors['white'])
        )

    import inspect
    # Obtener variables del contexto llamador
    frame = inspect.currentframe().f_back
    kwargs = frame.f_locals.copy()

    # Reemplazar variables y colorear
    pattern = re.compile(r'\{(.*?)\}')
    # Inicia el texto con el color general
    result = colors.get(text_color, colors['white']) + pattern.sub(replacer, text) + colors['reset']
    print(result)

# Ejemplo de uso:
if __name__ == '__main__':
    nombre = 'Juan'
    edad = 30
    cprint('mi nombre es {nombre} y tengo {edad} años', text_color='yellow', var_color='blue')