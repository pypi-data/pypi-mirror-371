# cprint

Imprime texto en consola con colores, permitiendo resaltar variables o expresiones dentro de llaves.

## Instalación

```bash
pip install cprint
```

## Uso básico

```python
from cprint import cprint

nombre = 'Juan'
edad = 30
cprint('Mi nombre es {nombre} y tengo {edad} años', text_color='yellow', var_color='blue')
```

## Opciones de color
- `text_color`: Color del texto general. Ej: 'red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white', 'black'.
- `var_color`: Color de las variables/expresiones.
- `bright`: Si es `True`, usa colores intensos (91, 92, etc).

## Expresiones avanzadas

Puedes usar expresiones dentro de las llaves:

```python
a = 5
b = 3
cprint('Suma: {a + b}', text_color='green', var_color='magenta')
```

## Licencia
MIT
