import pandas as pd
from openpyxl.utils import get_column_letter

def leer_excel(path):
    return pd.read_excel(path)

def escribir_excel(df, ruta_salida):
    # Crear un objeto ExcelWriter usando el motor openpyxl
    with pd.ExcelWriter(ruta_salida, engine='openpyxl') as writer:
        # Escribir el DataFrame en una hoja llamada 'Distribucion'
        df.to_excel(writer, index=False, sheet_name='Distribucion')

        # Obtener el objeto de la hoja de trabajo para poder manipularlo
        worksheet = writer.sheets['Distribucion']

        # --- Lógica para aplicar el formato de contabilidad ---
        
        # 1. Definir el formato: Símbolo de peso, separador de miles, sin decimales.
        accounting_format = '"$"#,##0'
        
        # 2. Encontrar la letra de la columna "Valor Glosa"
        try:
            # get_loc devuelve el índice basado en 0, Excel es basado en 1, por eso +1
            col_idx = df.columns.get_loc("Valor Glosa") + 1
            col_letter = get_column_letter(col_idx)
            
            # 3. Aplicar el formato a toda la columna
            # Iteramos desde la fila 2 para no afectar la cabecera
            for cell in worksheet[col_letter][1:]:
                cell.number_format = accounting_format
                
            # Opcional: Ajustar el ancho de la columna para que se vea bien
            worksheet.column_dimensions[col_letter].width = 15

        except KeyError:
            # Si la columna "Valor Glosa" no existe, no hacemos nada.
            print("Advertencia: La columna 'Valor Glosa' no fue encontrada en el DataFrame. No se aplicó formato.")