import streamlit as st
from pathlib import Path

st.title("🔎 Buscar referencias a ERP")

patrones = [
    'get_db_path("erp")',
    "get_db_path('erp')",
    "erp.db",
    '"erp"',
    "'erp'",
]

base = Path(__file__).resolve().parent

archivos = list(base.glob("*.py"))

encontrados = []

for archivo in archivos:
    try:
        texto = archivo.read_text(encoding="utf-8")
    except Exception:
        continue

    for patron in patrones:
        if patron in texto:
            lineas = texto.splitlines()
            for i, linea in enumerate(lineas, start=1):
                if patron in linea:
                    encontrados.append(
                        {
                            "archivo": archivo.name,
                            "linea": i,
                            "patron": patron,
                            "codigo": linea.strip(),
                        }
                    )

if encontrados:
    st.success(f"Encontradas {len(encontrados)} referencias")
    st.dataframe(encontrados, use_container_width=True)
else:
    st.success("No se encontraron referencias a ERP")
