import pandas as pd
from collections import defaultdict

def distribuir_facturas(df, nombres_personas):
    # <-- PUNTO 4: Validación de las columnas del archivo Excel.
    REQUIRED_COLS = ["Tercero", "Factura", "Valor Glosa", "Tipificación", "Tipo"]
    missing_cols = [col for col in REQUIRED_COLS if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Formato de Excel incorrecto. Faltan columnas: {', '.join(missing_cols)}")

    df = df.copy()
    df["Valor Glosa"] = pd.to_numeric(df["Valor Glosa"], errors="coerce").fillna(0)
    
    grupos = df.groupby(["Tercero", "Factura", "Valor Glosa", "Tipificación", "Tipo"])
    items = [grupo for _, grupo in grupos]
    items.sort(key=lambda g: g["Valor Glosa"].sum(), reverse=True)

    montos = defaultdict(float)
    conteos = defaultdict(int)
    asignaciones = []

    for grupo in items:
        valor_grupo = grupo["Valor Glosa"].sum()
        if valor_grupo > 0:
            persona = min(nombres_personas, key=lambda p: montos[p])
        else:
            persona = min(nombres_personas, key=lambda p: conteos[p])
        
        grupo_copy = grupo.copy()
        grupo_copy["Responsable"] = persona
        asignaciones.append(grupo_copy)
        montos[persona] += valor_grupo
        conteos[persona] += len(grupo)

    df_final = pd.concat(asignaciones)
    return df_final, montos