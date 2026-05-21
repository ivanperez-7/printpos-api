import os

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain_community.agent_toolkits.sql.base import create_sql_agent
from langchain_community.utilities import SQLDatabase
from sqlalchemy import create_engine, MetaData

TABLAS_PERMITIDAS = {
    'movimiento', 'movimientoitem', 'detalle_salida', 'detalle_entrada',
    'producto', 'cliente', 'equipocliente', 'lote', 'unidad',
    'equipo', 'marca', 'categoria', 'proveedor', 'sucursal',
}

_agente = None


def _build_schema_info(engine):
    metadata = MetaData()
    metadata.reflect(bind=engine)

    lines = []
    for table in metadata.sorted_tables:
        if table.name not in TABLAS_PERMITIDAS:
            continue
        cols = [f"  - {c.name} ({c.type})" for c in table.columns]
        lines.append(f"Tabla: {table.name}\n" + "\n".join(cols))

    return "\n\n".join(lines)


def obtener_agente():
    global _agente
    if _agente is not None:
        return _agente

    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        raise RuntimeError('GEMINI_API_KEY no configurada en el entorno.')

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=api_key,
        temperature=0
    )

    engine = create_engine(os.getenv('DATABASE_URL'))
    schema_info = _build_schema_info(engine)

    prefix = (
        f"Eres un asistente de base de datos para PrintPOS, un sistema de control de inventario.\n"
        f"El schema de las tablas relevantes es:\n\n{schema_info}\n\n"
        f"Genera únicamente consultas SELECT. No modifiques datos bajo ninguna circunstancia.\n"
        f"Responde en español de forma clara y concisa, basándote en los resultados de las consultas."
    )

    db = SQLDatabase(engine)
    toolkit = SQLDatabaseToolkit(db=db, llm=llm)

    _agente = create_sql_agent(
        llm=llm,
        toolkit=toolkit,
        prefix=prefix,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=10,
        early_stopping_method="generate",
    )

    return _agente
