import pandas as pd


def limpiar_columnas(df):
    """
    Limpia nombres de columnas.
    """
    if df is None:
        return df

    df = df.copy()
    df.columns = df.columns.astype(str).str.strip()
    return df


def buscar_columna(df, opciones):
    """
    Busca una columna usando varias opciones posibles.
    Acepta espacios, guiones bajos y mayúsculas/minúsculas.
    """
    if df is None:
        return None

    opciones_limpias = [
        str(op).upper().strip().replace(" ", "").replace("_", "")
        for op in opciones
    ]

    for col in df.columns:
        nombre = str(col).upper().strip().replace(" ", "").replace("_", "")

        if nombre in opciones_limpias:
            return col

    return None

def contar_estado(df, columna, estado):
    """
    Cuenta filas donde una columna tiene cierto estado.
    """
    if df is None or columna is None:
        return 0

    return len(
        df[
            df[columna]
            .astype(str)
            .str.upper()
            .str.strip() == estado.upper().strip()
        ]
    )


def sumar_columna(df, columna):
    """
    Suma una columna numérica de forma segura.
    """
    if df is None or columna is None:
        return 0

    return pd.to_numeric(
        df[columna],
        errors="coerce"
    ).fillna(0).sum()


def promedio_columna(df, columna):
    """
    Promedia una columna numérica de forma segura.
    """
    if df is None or columna is None:
        return 0

    valor = pd.to_numeric(
        df[columna],
        errors="coerce"
    ).mean()

    if pd.isna(valor):
        return 0

    return valor
