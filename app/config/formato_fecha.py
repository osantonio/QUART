from datetime import datetime, date, time as dtime

def formato_fecha(value):
    """
    Devuelve una representación de fecha en formato DD-MM-AAAA.
    
    Parámetros:
    - value: Puede ser datetime, date o str. Las cadenas se intentan parsear con
      formatos comunes: 'YYYY-MM-DD', 'DD/MM/YYYY', 'DD-MM-YYYY'. Si no es posible
      parsear, se retorna el valor original como str.
    
    Retorna:
    - str: Fecha formateada como 'DD-MM-AAAA', o '' si el valor es vacío.
    """
    if not value:
        return ""
    try:
        if isinstance(value, datetime):
            return value.strftime("%d-%m-%Y")
        if isinstance(value, date):
            return value.strftime("%d-%m-%Y")
        if isinstance(value, str):
            s = value.strip()
            for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"):
                try:
                    dt = datetime.strptime(s[:10], fmt)
                    return dt.strftime("%d-%m-%Y")
                except:
                    pass
            return s
    except:
        return str(value)

def formato_fecha_hora(value):
    """
    Devuelve una representación de fecha y hora en formato DD-MM-AAAA HH:MM AM/PM.
    
    Parámetros:
    - value: Puede ser datetime o str. Las cadenas se intentan parsear con
      formatos comunes: 'YYYY-MM-DD HH:MM:SS', 'YYYY-MM-DDTHH:MM:SS', 
      'YYYY-MM-DD HH:MM', 'YYYY-MM-DDTHH:MM', 'YYYY-MM-DD'.
    
    Retorna:
    - str: Fecha y hora formateadas como 'DD-MM-AAAA HH:MM AM/PM', o '' si el valor es vacío.
    """
    if not value:
        return ""
    try:
        if isinstance(value, datetime):
            return value.strftime("%d-%m-%Y %I:%M %p")
        if isinstance(value, str):
            s = value.strip()
            for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%dT%H:%M", "%Y-%m-%d"):
                try:
                    dt = datetime.strptime(s, fmt)
                    return dt.strftime("%d-%m-%Y %I:%M %p")
                except:
                    pass
            return s
    except:
        return str(value)

def formato_hora(value):
    """
    Devuelve una representación de hora en formato HH:MM AM/PM.
    
    Parámetros:
    - value: Puede ser datetime, time o str. Las cadenas se intentan parsear con
      formatos comunes: 'HH:MM:SS', 'HH:MM'.
    
    Retorna:
    - str: Hora formateada como 'HH:MM AM/PM', o '' si el valor es vacío.
    """
    if not value:
        return ""
    try:
        if isinstance(value, datetime):
            return value.strftime("%I:%M %p")
        if isinstance(value, dtime):
            return value.strftime("%I:%M %p")
        if isinstance(value, str):
            s = value.strip()
            for fmt in ("%H:%M:%S", "%H:%M"):
                try:
                    t = datetime.strptime(s, fmt)
                    return t.strftime("%I:%M %p")
                except:
                    pass
            return s
    except:
        return str(value)
