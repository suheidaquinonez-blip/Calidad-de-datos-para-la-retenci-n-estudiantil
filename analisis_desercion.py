from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

pd.set_option("display.width", 200)
pd.set_option("display.max_columns", 30)

RAW = Path(__file__).parent / "Data" / "raw" / "datos_estudiantes.csv"
PROCESSED = Path(__file__).parent / "Data" / "processed"
GRAFICOS = PROCESSED / "graficos"

# Valores válidos de cada columna categórica (la forma correcta de escribirlos).
VALIDOS = {
    "programa": ["Administración de Empresas", "Contaduría Pública", "Derecho", "Psicología",
                 "Ingeniería de Sistemas", "Ingeniería Industrial", "Enfermería", "Diseño Gráfico"],
    "jornada": ["Diurna", "Nocturna", "Fin de semana"],
    "genero": ["Femenino", "Masculino"],
    "ciudad_procedencia": ["Bogotá", "Medellín", "Cali", "Bucaramanga", "Rionegro",
                           "Barranquilla", "Otra ciudad"],
}

DECISIONES = []


def registrar(paso, columna, accion, filas, justificacion):
    """Guarda una decisión para la tabla de decisiones. Ya está escrita: solo úsala."""
    DECISIONES.append({
        "paso": paso, "columna": columna, "accion": accion,
        "filas_afectadas": int(filas), "justificacion": justificacion,
    })


def explorar(df):
    """Paso 1 del Word: primera mirada al dataset.

    Muestra la forma, los tipos y los nulos de cada columna, las estadísticas
    numéricas, y los valores de las columnas programa, jornada, genero y estado.
    Pregunta: ¿alguna columna numérica aparece como texto? ¿Por qué crees que pasa?
    """
    # TODO 1: imprimir shape, info(), describe() y value_counts() de las columnas indicadas.
    print(df.shape)
    df.info()
    print(df.describe())
    for col in ["programa", "jornada", "genero", "estado"]:
        print(df[col].value_counts())


def auditar(df):
    """Paso 2 del Word: buscar problemas sin corregirlos todavía.

    Revisa: nulos reales, faltantes disfrazados ('-', 999), valores imposibles
    (edad, promedio, horas), duplicados y formatos de fecha.
    Pregunta: ¿cuál de estos problemas afecta más el análisis? ¿Por qué?
    """
    # TODO 2: imprimir cada uno de los conteos de problemas.
    print("\n=== AUDITORÍA DE CALIDAD ===")

    print("\n--- Nulos reales por columna ---")
    print(df.isnull().sum())

    print("\n--- Faltantes disfrazados ---")
    print("Guiones en asistencia_pct:", (df["asistencia_pct"] == "-").sum())
    print("Guiones en horas_trabajo_semana:", (df["horas_trabajo_semana"] == "-").sum())
    print("Valores 999 en distancia_km:", (df["distancia_km"] == 999).sum())
    print("Celdas de asistencia_pct con el símbolo %:",
          df["asistencia_pct"].str.contains("%", regex=False).sum())

    print("\n--- Valores imposibles ---")
    print("Promedio mayor a 5:", (df["promedio_acumulado"] > 5).sum())
    print("Edad fuera de 15 a 60:", ((df["edad"] < 15) | (df["edad"] > 60)).sum())
    horas = pd.to_numeric(df["horas_trabajo_semana"], errors="coerce")
    print("Horas de trabajo mayores a 100:", (horas > 100).sum())

    print("\n--- Duplicados ---")
    print("Filas duplicadas:", df.duplicated().sum())

    print("\n--- Formatos de fecha ---")
    print("Fechas en formato DD/MM/AAAA:",
          df["fecha_matricula"].str.contains("/", regex=False).sum())
    pass


def convertir_numericos(df):
    """Paso 3 del Word: columnas que deberían ser numéricas, pero llegan como texto.

    Pistas: quitar el símbolo % con str.replace; reemplazar '-' por nulo;
    convertir con pd.to_numeric(..., errors="coerce"); reemplazar 999 por nulo en distancia_km.
    Registra cada conversión con registrar().
    """
    # TODO 3: convertir asistencia_pct, horas_trabajo_semana y distancia_km a número.
        # --- asistencia_pct ---
    n = (df["asistencia_pct"] == "-").sum()
    registrar("convertir_numericos", "asistencia_pct",
              "quitar % y cambiar '-' por nulo", n,
              "El guion es un faltante disfrazado y el % impide calcular promedios")
    df["asistencia_pct"] = df["asistencia_pct"].str.replace("%", "", regex=False)
    df["asistencia_pct"] = pd.to_numeric(df["asistencia_pct"].replace("-", np.nan), errors="coerce")

    # --- horas_trabajo_semana ---
    n = (df["horas_trabajo_semana"] == "-").sum()
    registrar("convertir_numericos", "horas_trabajo_semana",
              "cambiar '-' por nulo y convertir a número", n,
              "El guion significa que no hay dato; se trata en el paso 8")
    df["horas_trabajo_semana"] = pd.to_numeric(df["horas_trabajo_semana"].replace("-", np.nan), errors="coerce")

    # --- distancia_km ---
    n = (df["distancia_km"] == 999).sum()
    registrar("convertir_numericos", "distancia_km",
              "cambiar 999 por nulo", n,
              "999 es un código de 'sin dato', no una distancia real")
    df["distancia_km"] = df["distancia_km"].replace(999, np.nan)
    return df


def unificar_categorias(df):
    """Paso 4 del Word: errores tipográficos en columnas categóricas.

    Pistas: primero df[col].str.strip().str.lower(); después .replace(diccionario)
    con las variantes que encontraste con value_counts(). Los valores correctos están en VALIDOS.
    Pregunta: ¿qué variantes son el mismo valor? ¿Hay alguna que no debas unificar?
    """
    # TODO 4: unificar las escrituras de programa, jornada, genero y ciudad_procedencia.
        # Variantes que encontramos con value_counts(), en minúsculas y sin espacios
    variantes = {
        "programa": {"ingenieria de sistemas": "Ingeniería de Sistemas",
                     "psicologia": "Psicología"},
        "jornada": {},
        "genero": {"m": "Masculino", "f": "Femenino"},
        "ciudad_procedencia": {"bogota": "Bogotá", "medellin": "Medellín"},
    }

    for col in ["programa", "jornada", "genero", "ciudad_procedencia"]:
        # 1. Contar cuántas filas están mal escritas (antes de cambiar nada)
        n = (df[col].notnull() & ~df[col].isin(VALIDOS[col])).sum()

        # 2. Normalizar: quitar espacios y pasar a minúsculas
        df[col] = df[col].str.strip().str.lower()

        # 3. Diccionario: cada valor correcto en minúsculas -> su forma correcta
        diccionario = {v.lower(): v for v in VALIDOS[col]}
        diccionario.update(variantes[col])
        df[col] = df[col].replace(diccionario)

        # 4. Registrar la decisión
        registrar("unificar_categorias", col,
                  "normalizar con strip/lower y unificar variantes", n,
                  "La misma categoría escrita distinto se contaría como grupos separados")
    return df


def convertir_fechas(df):
    """Paso 5 del Word: fechas escritas en dos formatos.

    Pista: intenta el formato AAAA-MM-DD y luego DD/MM/AAAA, cada uno con errors="coerce",
    y junta los resultados con fillna(). Registra cuántas fechas tenían el segundo formato.
    """
    # TODO 5: convertir fecha_matricula a fecha con los dos formatos.
        # 1. Contar cuántas fechas están en el segundo formato (antes de cambiar)
    n = df["fecha_matricula"].str.contains("/", regex=False).sum()
    registrar("convertir_fechas", "fecha_matricula",
              "unificar dos formatos (AAAA-MM-DD y DD/MM/AAAA) en una fecha", n,
              "Pandas no puede interpretar dos formatos a la vez; con formato explícito se evita confundir día y mes")

    # 2. Intentar cada formato por separado
    iso = pd.to_datetime(df["fecha_matricula"], format="%Y-%m-%d", errors="coerce")
    dmy = pd.to_datetime(df["fecha_matricula"], format="%d/%m/%Y", errors="coerce")

    # 3. Juntar: donde el primero falló (NaT), usar el segundo
    df["fecha_matricula"] = iso.fillna(dmy)
    return df


def eliminar_duplicados(df):
    """Paso 6 del Word: filas repetidas.

    Pregunta: ¿podrían existir dos estudiantes distintos con todos los datos iguales?
    Pista: duplicated() y drop_duplicates(), con reset_index(drop=True).
    """
    # TODO 6: eliminar duplicados, registrar la decisión y devolver el dataframe.
        # 1. Contar los duplicados (antes de eliminarlos)
    n = df.duplicated().sum()

    # 2. Eliminar y renumerar el índice
    df = df.drop_duplicates().reset_index(drop=True)

    # 3. Registrar la decisión
    registrar("eliminar_duplicados", "todas las columnas",
              "eliminar filas idénticas y conservar la primera aparición", n,
              "Un id_estudiante identifica a una sola persona; repetirlo cuenta al mismo estudiante dos veces y distorsiona las tasas")
    
    return df


def tratar_faltantes(df):
    """Paso 7 del Word: decidir qué hacer con los nulos reales.

    Preguntas:
    - ¿Puedes inventar una nota? ¿Qué pasa si imputas el promedio?
    - Para ciudad o tipo de colegio, ¿conviene eliminar la fila o marcar el dato como 'Sin dato'?
    - motivo_retiro tiene muchos nulos. ¿Son errores? (Pista: ¿para quiénes aplica esa columna?)
    """
    # TODO 7: tratar los nulos de promedio_acumulado, ciudad_procedencia y tipo_colegio.
        # --- promedio_acumulado: eliminar filas (no se inventa una nota) ---
    n = df["promedio_acumulado"].isnull().sum()
    registrar("tratar_faltantes", "promedio_acumulado",
              "eliminar filas con nulo", n,
              "Una nota no se puede inventar; imputar el promedio escondería la variación real de cada estudiante")
    df = df.dropna(subset=["promedio_acumulado"]).reset_index(drop=True)

    # --- ciudad_procedencia y tipo_colegio: marcar como 'Sin dato' ---
    for col in ["ciudad_procedencia", "tipo_colegio"]:
        n = df[col].isnull().sum()
        registrar("tratar_faltantes", col,
                  "reemplazar nulo por 'Sin dato'", n,
                  "Es una categoría: eliminar la fila perdería al estudiante, y así queda visible que el dato falta")
        df[col] = df[col].fillna("Sin dato")
    return df


def tratar_imposibles(df):
    """Paso 8 del Word: valores que no pueden existir.

    Preguntas:
    - La escala del promedio es de 0 a 5. ¿Qué harías con un 45?
    - Una edad de 150 años es un error. ¿Qué valor pondrías en su lugar?
    - Si el estudiante no trabaja, ¿cuántas horas de trabajo tiene? ¿Cómo lo aplicas en código?
    """
    # TODO 8: tratar edad, promedio_acumulado y horas_trabajo_semana, con sus justificaciones.
        # --- promedio_acumulado: fuera de 0-5 -> eliminar filas ---
    mask = df["promedio_acumulado"] > 5
    registrar("tratar_imposibles", "promedio_acumulado",
              "eliminar filas con promedio mayor a 5", mask.sum(),
              "La escala es 0 a 5; valores como 62 o 78 siguen fuera de escala aun dividiéndolos, y una nota no se inventa")
    df = df[~mask].reset_index(drop=True)

    # --- edad: fuera de 15-60 -> nulo -> mediana ---
    mask = (df["edad"] < 15) | (df["edad"] > 60)
    mediana_edad = df.loc[~mask, "edad"].median()
    registrar("tratar_imposibles", "edad",
              "reemplazar edades fuera de 15-60 por la mediana", mask.sum(),
              "Edades de 150 o 12 años son errores de registro; la mediana no se ve afectada por extremos")
    df.loc[mask, "edad"] = mediana_edad

    # --- horas_trabajo_semana: regla 1, si no trabaja -> 0 ---
    mask = (df["trabaja"] == "no") & df["horas_trabajo_semana"].isnull()
    registrar("tratar_imposibles", "horas_trabajo_semana",
              "poner 0 horas a quien no trabaja", mask.sum(),
              "Quien no trabaja tiene 0 horas; el guion original no era un dato faltante sino un cero")
    df.loc[mask, "horas_trabajo_semana"] = 0

    # --- horas_trabajo_semana: regla 2, mayor a 100 -> mediana de quienes trabajan ---
    mask = df["horas_trabajo_semana"] > 100
    df.loc[mask, "horas_trabajo_semana"] = np.nan
    mediana_horas = df.loc[df["trabaja"] == "sí", "horas_trabajo_semana"].median()
    registrar("tratar_imposibles", "horas_trabajo_semana",
              "reemplazar horas mayores a 100 por la mediana de quienes trabajan", mask.sum(),
              "Una semana tiene 168 horas y más de 100 de trabajo es un error; se usa la mediana de quienes trabajan, no de todos")
    df.loc[mask, "horas_trabajo_semana"] = mediana_horas
    return df


def crear_variables(df):
    """Paso 9 del Word: variables nuevas para el análisis.

    Crea:
    - desertor: True si estado es 'desertor', False si no.
    - cuartil_asistencia: divide asistencia_pct en cuatro grupos iguales con pd.qcut.
    Pregunta: ¿por qué conviene usar cuartiles y no valores exactos de asistencia?
    """
    # TODO 9: crear las columnas desertor y cuartil_asistencia.
        # --- desertor: True si el estado es 'desertor' ---
    df["desertor"] = df["estado"].eq("desertor")
    registrar("crear_variables", "desertor",
              "crear columna booleana a partir de estado", df["desertor"].sum(),
              "Con True/False el promedio de la columna es directamente la tasa de deserción")

    # --- cuartil_asistencia: cuatro grupos de igual tamaño ---
    df["cuartil_asistencia"] = pd.qcut(df["asistencia_pct"], 4, labels=["Q1", "Q2", "Q3", "Q4"])
    registrar("crear_variables", "cuartil_asistencia",
              "dividir asistencia_pct en cuatro grupos con qcut", df["cuartil_asistencia"].notnull().sum(),
              "Los cuartiles dan grupos del mismo tamaño y permiten comparar tasas sin depender de valores exactos")
    return df


def grafico_faltantes(df):
    """Gráfico 1: mapa de faltantes del dataset original.

    Pista: sns.heatmap(df.isnull(), cbar=False)
    """
    # TODO 10: dibujar, guardar en GRAFICOS / "mapa_faltantes.png" y mostrar.

    GRAFICOS.mkdir(parents=True, exist_ok=True)
    plt.figure(figsize=(12, 6))
    sns.heatmap(df.isnull(), cbar=False)
    plt.title("Mapa de faltantes del dataset original")
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.savefig(GRAFICOS / "mapa_faltantes.png", bbox_inches="tight")
    plt.show()
    pass


def grafico_distribuciones(antes, despues):
    """Gráfico 2: boxplots de promedio_acumulado y edad, antes y después de limpiar.

    Pregunta: ¿qué cambió en cada distribución? ¿Por qué?
    """
    # TODO 11: dibujar los cuatro boxplots, guardar en GRAFICOS / "distribuciones_antes_despues.png" y mostrar.

    GRAFICOS.mkdir(parents=True, exist_ok=True)
    fig, ejes = plt.subplots(2, 2, figsize=(12, 8))
    sns.boxplot(x=antes["promedio_acumulado"], ax=ejes[0, 0])
    ejes[0, 0].set_title("promedio_acumulado (antes)")
    sns.boxplot(x=despues["promedio_acumulado"], ax=ejes[0, 1])
    ejes[0, 1].set_title("promedio_acumulado (después)")
    sns.boxplot(x=antes["edad"], ax=ejes[1, 0])
    ejes[1, 0].set_title("edad (antes)")
    sns.boxplot(x=despues["edad"], ax=ejes[1, 1])
    ejes[1, 1].set_title("edad (después)")
    plt.tight_layout()
    plt.savefig(GRAFICOS / "distribuciones_antes_despues.png", bbox_inches="tight")
    plt.show()
    pass


def grafico_tasa_programa(df):
    """Gráfico 3: tasa de deserción por programa.

    Pista: df.groupby("programa")["desertor"].mean()
    """
    # TODO 12: dibujar la tasa por programa, guardar en GRAFICOS / "tasa_desercion_por_programa.png" y mostrar.

    GRAFICOS.mkdir(parents=True, exist_ok=True)
    tasa = df.groupby("programa")["desertor"].mean().sort_values(ascending=False)
    plt.figure(figsize=(10, 6))
    tasa.plot(kind="bar")
    plt.title("Tasa de deserción por programa")
    plt.ylabel("Tasa de deserción")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(GRAFICOS / "tasa_desercion_por_programa.png", bbox_inches="tight")
    plt.show()
    pass


def grafico_tasa_asistencia(df):
    """Gráfico 4: tasa de deserción por cuartil de asistencia.

    Pista: df.groupby("cuartil_asistencia", observed=True)["desertor"].mean()
    """
    # TODO 13: dibujar la tasa por cuartil, guardar en GRAFICOS / "tasa_desercion_por_asistencia.png" y mostrar.


    GRAFICOS.mkdir(parents=True, exist_ok=True)
    tasa = df.groupby("cuartil_asistencia", observed=True)["desertor"].mean()
    plt.figure(figsize=(8, 6))
    tasa.plot(kind="bar")
    plt.title("Tasa de deserción por cuartil de asistencia")
    plt.xlabel("Cuartil de asistencia (Q1 = menor asistencia)")
    plt.ylabel("Tasa de deserción")
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.savefig(GRAFICOS / "tasa_desercion_por_asistencia.png", bbox_inches="tight")
    plt.show()
    pass


def responder_preguntas(df):
    """Paso 10 del Word: las cinco preguntas de la institución.

    Cada pregunta debe imprimir el resultado con el número de estudiantes por grupo.
    Pregunta 1: ¿Qué programa presenta la tasa de deserción más alta?
    Pregunta 2: ¿Hay diferencia en la deserción entre becados y no becados?
    Pregunta 3: ¿Qué jornada tiene el menor promedio acumulado?
    Pregunta 4: ¿Cuántas materias reprobadas tienen en promedio los desertores frente a los activos?
                (Excluye a los graduados.)
    Pregunta 5: ¿La deserción aumenta conforme baja la asistencia?
                (Usa cuartil_asistencia.)
    """
    # TODO 14: responder las cinco preguntas con groupby() y agg().
        # --- Pregunta 1: ¿qué programa tiene la tasa de deserción más alta? ---
    print("\n=== Pregunta 1: tasa de deserción por programa ===")
    p1 = df.groupby("programa").agg(
        tasa=("desertor", "mean"),
        estudiantes=("desertor", "size"),
    ).sort_values("tasa", ascending=False)
    print(p1.round(3))

    # --- Pregunta 2: ¿hay diferencia entre becados y no becados? ---
    print("\n=== Pregunta 2: tasa de deserción según beca ===")
    p2 = df.groupby("beca").agg(
        tasa=("desertor", "mean"),
        estudiantes=("desertor", "size"),
    )
    print(p2.round(3))

    # --- Pregunta 3: ¿qué jornada tiene el menor promedio acumulado? ---
    print("\n=== Pregunta 3: promedio acumulado por jornada ===")
    p3 = df.groupby("jornada").agg(
        promedio=("promedio_acumulado", "mean"),
        estudiantes=("promedio_acumulado", "size"),
    ).sort_values("promedio")
    print(p3.round(3))

    # --- Pregunta 4: materias reprobadas, desertores vs activos (sin graduados) ---
    print("\n=== Pregunta 4: materias reprobadas, desertores vs activos ===")
    sin_graduados = df[df["estado"] != "graduado"]
    p4 = sin_graduados.groupby("estado").agg(
        reprobadas_promedio=("materias_reprobadas", "mean"),
        estudiantes=("materias_reprobadas", "size"),
    )
    print(p4.round(3))

    # --- Pregunta 5: ¿la deserción aumenta al bajar la asistencia? ---
    print("\n=== Pregunta 5: tasa de deserción por cuartil de asistencia ===")
    p5 = df.groupby("cuartil_asistencia", observed=True).agg(
        tasa=("desertor", "mean"),
        estudiantes=("desertor", "size"),
        asistencia_promedio=("asistencia_pct", "mean"),
    )
    print(p5.round(3))
    pass


def guardar(df):
    """Paso 11 del Word: guardar el dataset limpio y la tabla de decisiones. Ya está escrito."""
    PROCESSED.mkdir(parents=True, exist_ok=True)
    df.to_csv(PROCESSED / "dataset_limpio.csv", index=False)
    pd.DataFrame(DECISIONES).to_csv(PROCESSED / "decisiones.csv", index=False)
    print(f"\nDataset limpio guardado: {df.shape[0]} filas, {df.shape[1]} columnas.")


def main():
    original = pd.read_csv(RAW)
    df = original.copy()

    explorar(df)
    auditar(df)
    grafico_faltantes(df)

    df = convertir_numericos(df)
    df = unificar_categorias(df)
    df = convertir_fechas(df)
    df = eliminar_duplicados(df)
    df = tratar_faltantes(df)
    df = tratar_imposibles(df)
    df = crear_variables(df)

    grafico_distribuciones(original, df)
    grafico_tasa_programa(df)
    grafico_tasa_asistencia(df)

    responder_preguntas(df)
    print("\nTabla de decisiones:")
    print(pd.DataFrame(DECISIONES))
    guardar(df)


if __name__ == "__main__":
    main()
