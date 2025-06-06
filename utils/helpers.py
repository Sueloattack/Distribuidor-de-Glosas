from datetime import datetime

def fecha_actual():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")