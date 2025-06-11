import flet as ft
from ui.views import main_view

def main(page: ft.Page):
    page.title = "Distribuidor de Glosas"
    page.scroll = ft.ScrollMode.ADAPTIVE

    page.window_icon = "icono.ico"  

    def on_connect(e):
        page.window_maximized = True
        page.update()

    page.on_connect = on_connect

    main_view(page)

ft.app(target=main)