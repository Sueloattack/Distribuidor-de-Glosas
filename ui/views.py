# /ui/views.py

import flet as ft
from services.excel_handler import leer_excel, escribir_excel
from controllers.distributor import distribuir_facturas
from utils.helpers import fecha_actual
import os
from ui.components import crear_nombre_input
from collections import defaultdict

def main_view(page: ft.Page):
    page.title = "Distribuidor de Glosas"; page.theme_mode = ft.ThemeMode.DARK; page.bgcolor = "#1f2630"; page.padding = 20
    page.vertical_alignment = ft.MainAxisAlignment.START; page.horizontal_alignment = ft.CrossAxisAlignment.CENTER; page.scroll = ft.ScrollMode.ADAPTIVE

    ERROR_COLOR = ft.Colors.RED; SUCCESS_COLOR = ft.Colors.GREEN_400; DEFAULT_BORDER_COLOR = "#444c5c"

    def reset_save_path_ui():
        archivo_guardado.value = None; save_status.value = "No configurada"
        save_selection_container.bgcolor, save_selection_container.border = "#2a3341", ft.border.all(1, DEFAULT_BORDER_COLOR)
        save_text_display.value = "Aún no se ha seleccionado una ruta"; save_button.disabled = True

    def on_dialog_result(e: ft.FilePickerResultEvent):
        if e.files:
            ruta, nombre = e.files[0].path, e.files[0].name; archivo_path.value, archivo_status.value = ruta, nombre
            file_selection_container.bgcolor, file_selection_container.border = "#1a3b2a", ft.border.all(1, SUCCESS_COLOR)
            file_text_display.value = nombre; reset_save_path_ui(); save_button.disabled = False
            page.update()

    def on_save_result(e: ft.FilePickerResultEvent):
        if e.path:
            ruta = e.path if e.path.lower().endswith(".xlsx") else f"{e.path}.xlsx"; archivo_guardado.value = ruta
            save_selection_container.bgcolor, save_selection_container.border = "#1a3b2a", ft.border.all(1, SUCCESS_COLOR)
            nombre_archivo_guardado = os.path.basename(ruta); save_text_display.value, save_status.value = nombre_archivo_guardado, nombre_archivo_guardado
            page.update()

    def open_save_dialog(e):
        if not archivo_path.value:
            page.snack_bar = ft.SnackBar(ft.Text("Por favor, seleccione primero el archivo Excel a distribuir."), bgcolor=ft.Colors.ORANGE_700); page.snack_bar.open = True; page.update(); return
        base, _ = os.path.splitext(os.path.basename(archivo_path.value)); save_picker.save_file(file_name=f"{base}_distribuida.xlsx", allowed_extensions=["xlsx"])

    file_picker, save_picker = ft.FilePicker(on_result=on_dialog_result), ft.FilePicker(on_result=on_save_result); page.overlay.extend([file_picker, save_picker])
    archivo_path, archivo_guardado, nombres_controls = ft.TextField(visible=False), ft.TextField(visible=False), []
    archivo_status, save_status, personas_status = ft.Text("Ninguno"), ft.Text("No configurada"), ft.Text("No configurado")
    estado_status = ft.Text("Listo", color=ft.Colors.TEAL_ACCENT_400); error_style = ft.TextStyle(color=ERROR_COLOR)
    file_text_display = ft.Text("Aún no se ha seleccionado un archivo", color=ft.Colors.WHITE70)
    file_selection_container = ft.Container(padding=20, border=ft.border.all(1, DEFAULT_BORDER_COLOR), border_radius=8, bgcolor="#2a3341", content=ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[file_text_display, ft.ElevatedButton("Seleccionar Archivo", icon=ft.Icons.UPLOAD_FILE, on_click=lambda _: file_picker.pick_files(allow_multiple=False, allowed_extensions=["xlsx"]))]))
    save_button = ft.ElevatedButton("Seleccionar Ruta", icon=ft.Icons.SAVE_AS_OUTLINED, on_click=open_save_dialog, disabled=True)
    save_text_display = ft.Text("Aún no se ha seleccionado una ruta", color=ft.Colors.WHITE70, expand=True)
    save_selection_container = ft.Container(padding=20, border=ft.border.all(1, DEFAULT_BORDER_COLOR), border_radius=8, bgcolor="#2a3341", content=ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[save_text_display, save_button]))
    
    def on_cantidad_change(e):
        ctrl, val = e.control, e.control.value; val_limpio = "".join(filter(str.isdigit, val)); final_val = val_limpio
        if val_limpio and int(val_limpio) > 15:
            final_val = "15"; page.snack_bar = ft.SnackBar(ft.Text("El número máximo de personas es 15. Se ha ajustado automáticamente."), bgcolor=ft.Colors.ORANGE_700); page.snack_bar.open = True
        if ctrl.value != final_val: ctrl.value = final_val
        if final_val and (0 < int(final_val) <= 15): ctrl.border_color, ctrl.error_text = SUCCESS_COLOR, None
        else: ctrl.border_color, ctrl.error_text = DEFAULT_BORDER_COLOR, None
        generar_campos_nombres(final_val); page.update()

    def on_name_change(e):
        ctrl = e.control
        if ctrl.value.strip(): ctrl.border_color, ctrl.error_text = SUCCESS_COLOR, None
        else: ctrl.border_color, ctrl.error_text = DEFAULT_BORDER_COLOR, None
        page.update()

    cantidad_input = ft.TextField(label="¿En cuántas personas se divide?", on_change=on_cantidad_change, border_color=DEFAULT_BORDER_COLOR, error_style=error_style)
    nombres_container, resultados_container = ft.Column(spacing=10), ft.Column(spacing=10)

    def generar_campos_nombres(val_str):
        nombres_container.controls.clear(); nombres_controls.clear(); cantidad = int(val_str) if val_str else 0
        if 0 < cantidad <= 15:
            for i in range(cantidad):
                nombres_container.controls.append(crear_nombre_input(i + 1, error_style=error_style, on_change_handler=on_name_change))
                nombres_controls.append(nombres_container.controls[-1])
        personas_status.value = f"{cantidad} Personas" if cantidad > 0 else "No configurado"

    def reset_ui_for_new_operation():
        reset_save_path_ui(); save_button.disabled = True; archivo_path.value = None; archivo_status.value = "Ninguno"
        file_selection_container.bgcolor, file_selection_container.border = "#2a3341", ft.border.all(1, DEFAULT_BORDER_COLOR)
        file_text_display.value = "Aún no se ha seleccionado un archivo"; cantidad_input.value = ""; cantidad_input.border_color = DEFAULT_BORDER_COLOR
        generar_campos_nombres("")

    def reset_error_states():
        file_selection_container.border = ft.border.all(1, SUCCESS_COLOR) if archivo_path.value else ft.border.all(1, DEFAULT_BORDER_COLOR)
        save_selection_container.border = ft.border.all(1, SUCCESS_COLOR) if archivo_guardado.value else ft.border.all(1, DEFAULT_BORDER_COLOR)
        if cantidad_input.value and 0 < int(cantidad_input.value) <= 15:
            cantidad_input.border_color, cantidad_input.error_text = SUCCESS_COLOR, None
        else:
            cantidad_input.border_color = DEFAULT_BORDER_COLOR
        estado_status_card.border = None
        for ctrl in nombres_controls: ctrl.error_text, ctrl.border_color = None, (SUCCESS_COLOR if ctrl.value else DEFAULT_BORDER_COLOR)
        page.update()

    def procesar(e):
        card_resultados.visible = False; reset_error_states(); is_valid = True
        
        if not archivo_path.value: file_selection_container.border, is_valid = ft.border.all(2, ERROR_COLOR), False
        if not archivo_guardado.value: save_selection_container.border, is_valid = ft.border.all(2, ERROR_COLOR), False
        if not cantidad_input.value or int(cantidad_input.value) <= 0: cantidad_input.border_color, cantidad_input.error_text, is_valid = ERROR_COLOR, "Debe ser mayor a 0", False
        
        for ctrl in nombres_controls:
            if not ctrl.value.strip(): ctrl.border_color, ctrl.error_text, is_valid = ERROR_COLOR, "El nombre es requerido", False
        if nombres_controls:
            nombres_list = [ctrl.value.strip().lower() for ctrl in nombres_controls]; name_counts = defaultdict(int)
            for name in nombres_list:
                if name: name_counts[name] += 1
            duplicates = {name for name, count in name_counts.items() if count > 1}
            if duplicates:
                is_valid = False
                for ctrl in nombres_controls:
                    if ctrl.value.strip().lower() in duplicates: ctrl.border_color, ctrl.error_text = ERROR_COLOR, "Nombre repetido"

        if not is_valid: page.snack_bar = ft.SnackBar(ft.Text("Por favor, corrija los campos marcados en rojo."), bgcolor=ERROR_COLOR); page.snack_bar.open = True; page.update(); return

        estado_status.value, estado_status.color = "Procesando...", ft.Colors.ORANGE
        nombres = [ctrl.value.strip() for ctrl in nombres_controls]; page.update()
        
        try:
            df, montos = distribuir_facturas(leer_excel(archivo_path.value), nombres)
            escribir_excel(df, archivo_guardado.value)
            total_glosa = sum(montos.values())
            
            resultados_container.controls.clear()
            resultados_container.controls.append(ft.Row([ft.Text("Resultados de la División", size=18, weight=ft.FontWeight.BOLD)], alignment=ft.MainAxisAlignment.CENTER))
            resultados_container.controls.append(ft.Divider())
            resultados_container.controls.append(ft.Row(controls=[ft.Text(f"Distribución realizada el {fecha_actual()}", text_align=ft.TextAlign.LEFT, expand=True), ft.Text(f"Monto total: ${total_glosa:,.2f}", weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER), ft.Text(f"Total Facturas: {len(df)}", weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.RIGHT, expand=True)]))
            for nombre in nombres:
                monto_persona, cantidad_filas = montos.get(nombre, 0), len(df[df["Responsable"] == nombre])
                progreso = monto_persona / total_glosa if total_glosa > 0 else 0
                resultados_container.controls.append(ft.Container(padding=10, border_radius=8, bgcolor="#2a3341", margin=ft.margin.only(top=10), content=ft.Column([ft.Text(nombre, weight=ft.FontWeight.BOLD),ft.ProgressBar(value=progreso, color="#a16eff", bgcolor="#3a4351", height=10, border_radius=5),ft.Row(alignment=ft.MainAxisAlignment.END, controls=[ft.Text(f"${monto_persona:,.2f} | {cantidad_filas} facturas", color=ft.Colors.WHITE)])])))
            
            card_resultados.visible = True; estado_status.value, estado_status.color = "Completado", ft.Colors.GREEN
            estado_status_card.border = ft.border.all(2, SUCCESS_COLOR)
            page.snack_bar = ft.SnackBar(ft.Text("Proceso finalizado. El archivo ha sido guardado.", color=ft.Colors.WHITE), bgcolor=ft.Colors.GREEN)
            reset_ui_for_new_operation()

        except Exception as ex:
            estado_status.value, estado_status.color = "Error, Excel incompatible", ERROR_COLOR
            estado_status_card.border = ft.border.all(2, ERROR_COLOR)
            # --- ÚLTIMO CAMBIO ---
            # Ahora, el contenedor del archivo de entrada también se marca en rojo.
            file_selection_container.border = ft.border.all(2, ERROR_COLOR)
            page.snack_bar = ft.SnackBar(ft.Text(f"{ex}"), bgcolor=ERROR_COLOR)
        
        page.snack_bar.open = True; page.update()

    def create_status_card(title, value_control, icon, icon_color):
        return ft.Container(padding=15, border_radius=8, bgcolor="#2a3341", expand=True, content=ft.Row(spacing=15, controls=[ft.Icon(name=icon, color=icon_color), ft.Column([ft.Text(title, size=12, color=ft.Colors.WHITE70), value_control])]))

    estado_status_card = create_status_card("Estado", estado_status, ft.Icons.PLAY_CIRCLE_OUTLINE, ft.Colors.TEAL_ACCENT_400)
    card_resultados = ft.Card(visible=False, content=ft.Container(padding=20, content=resultados_container))
    exportar_boton = ft.ElevatedButton(text="Exportar Excel Repartido", icon=ft.Icons.PLAY_ARROW, on_click=procesar, height=50, style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8), bgcolor="#a16eff", color=ft.Colors.WHITE))
    
    page.add(ft.Column(expand=True, spacing=25, alignment=ft.MainAxisAlignment.START, horizontal_alignment=ft.CrossAxisAlignment.CENTER, controls=[
                ft.Text("Distribuidor de Glosas", size=32, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
                ft.Row(spacing=20, controls=[create_status_card("Archivo Seleccionado", archivo_status, ft.Icons.FOLDER_OPEN, icon_color=ft.Colors.BLUE_300), create_status_card("Ruta de Guardado", save_status, ft.Icons.SAVE, icon_color=ft.Colors.AMBER_300), create_status_card("Personas a Dividir", personas_status, ft.Icons.PEOPLE_OUTLINE, icon_color=ft.Colors.PURPLE_ACCENT_100), estado_status_card]),
                ft.Card(content=ft.Container(padding=20, content=ft.Column([ft.Text("1. Archivos", size=18, weight=ft.FontWeight.BOLD), ft.Text("Selecciona el archivo Excel y la ubicación donde se guardará el resultado."), ft.Divider(), ft.Text("Archivo Excel", weight=ft.FontWeight.BOLD), file_selection_container, ft.Container(content=ft.Text("Ruta de Guardado", weight=ft.FontWeight.BOLD), margin=ft.margin.only(top=15)), save_selection_container]))),
                ft.Card(content=ft.Container(padding=20, content=ft.Column([ft.Text("2. Configuración", size=18, weight=ft.FontWeight.BOLD), ft.Text("Define el número de personas y asigna sus nombres para la distribución."), ft.Divider(), cantidad_input, nombres_container]))),
                ft.Row(alignment=ft.MainAxisAlignment.CENTER, controls=[exportar_boton]),
                card_resultados]))