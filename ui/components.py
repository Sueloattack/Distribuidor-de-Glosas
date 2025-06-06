import flet as ft

def crear_nombre_input(numero: int, error_style=None, on_change_handler=None) -> ft.TextField:
    """
    Crea un campo de texto para el nombre de una persona.
    Ahora acepta un manejador 'on_change' para validación en tiempo real.
    """
    return ft.TextField(
        label=f"Nombre persona #{numero}",
        border_radius=8,
        border_color="#444c5c",
        error_style=error_style,
        on_change=on_change_handler # <-- NUEVO: Conectar el manejador de eventos.
    )