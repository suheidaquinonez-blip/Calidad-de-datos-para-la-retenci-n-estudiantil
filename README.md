# Taller práctico proyecto integrador: calidad de datos para la retención estudiantil

Una institución de educación superior quiere entender qué factores están asociados a la deserción, para diseñar estrategias de retención tempranas. Antes de responder preguntas de análisis, el equipo de datos debe garantizar que la información sea confiable. Este taller trabaja justo ese paso: auditar, limpiar y documentar los datos, y después responder cinco preguntas con esos datos limpios.

Los datos son sintéticos. Fueron generados para el taller y no corresponden a estudiantes reales.

## Requisitos

- Python 3.10 o superior
- Git
- Lo visto en los talleres de Pandas y de limpieza de datos

## Cómo empezar

1. Clona el repositorio y entra a la carpeta del proyecto:

```
git clone <URL-DEL-REPOSITORIO>
cd <NOMBRE-DE-LA-CARPETA>
```

2. Crea y activa un ambiente virtual. Las instrucciones para Windows y Mac/Linux están en `LEEME_ambiente.txt`.
3. Instala las librerías:

```
pip install -r requirements.txt
```

4. Ejecuta el script desde la carpeta del proyecto:

```
python analisis_desercion.py
```

## Estructura del proyecto

```
proyecto/
├── analisis_desercion.py   Script principal. Tiene un TODO por cada paso.
├── requirements.txt        Versiones de las librerías.
├── LEEME_ambiente.txt      Pasos para crear el ambiente virtual.
├── README.md               Este archivo.
├── .gitignore              Archivos que Git no debe subir.
└── Data/
    ├── raw/
    │   └── datos_estudiantes.csv   Dataset original. No lo modifiques.
    └── processed/
        ├── .gitkeep                Mantiene la carpeta en el repositorio.
        ├── dataset_limpio.csv      Lo genera el script. No se sube (está en .gitignore).
        ├── decisiones.csv          Lo genera el script. Sí se sube.
        └── graficos/               Lo genera el script. Sí se sube.
```

## Qué debes hacer

Completa los TODO de `analisis_desercion.py` en orden. Cada función tiene un docstring con preguntas: respóndelas antes de escribir el código. Cada decisión que tomes debe quedar registrada con `registrar()`.

Cuando termines, el script produce:

- `Data/processed/dataset_limpio.csv`: el dataset limpio.
- `Data/processed/decisiones.csv`: la tabla de decisiones.
- `Data/processed/graficos/`: los cuatro gráficos.

---

## Mis decisiones y respuestas

### 0. Diccionario de datos

| Columna | Tipo | Descripción | Rol |
|---|---|---|---|
| id_estudiante | Texto | Código único que identifica a cada estudiante | Identificación |
| programa | Categórica | Programa académico en el que está matriculado (8 programas) | Explicativa |
| facultad | Categórica | Facultad a la que pertenece el programa | Explicativa |
| jornada | Categórica | Horario de estudio: diurna, nocturna o fin de semana | Explicativa |
| semestre | Numérica | Semestre que cursa el estudiante (de 1 a 10) | Explicativa |
| promedio_acumulado | Numérica | Promedio de notas acumulado, en escala de 0 a 5 | Explicativa |
| creditos_aprobados | Numérica | Cantidad de créditos que ha aprobado | Explicativa |
| materias_reprobadas | Numérica | Cantidad de materias que ha reprobado | Explicativa |
| asistencia_pct | Numérica | Porcentaje de asistencia a clase (llegó como texto, con % y guiones) | Explicativa |
| sesiones_tutoria | Numérica | Número de sesiones de tutoría a las que asistió | Explicativa |
| cambios_programa | Numérica | Cuántas veces cambió de programa (0 o 1) | Explicativa |
| estrato | Categórica | Estrato socioeconómico del estudiante (de 1 a 6) | Explicativa |
| beca | Categórica | Indica si el estudiante recibe una beca (sí o no) | Explicativa |
| trabaja | Categórica | Indica si el estudiante trabaja (sí o no) | Explicativa |
| horas_trabajo_semana | Numérica | Horas que trabaja por semana; 0 si no trabaja (llegó como texto, con guiones) | Explicativa |
| distancia_km | Numérica | Distancia en kilómetros entre su vivienda y la institución | Explicativa |
| edad | Numérica | Edad del estudiante en años | Explicativa |
| genero | Categórica | Género del estudiante: masculino o femenino | Explicativa |
| ciudad_procedencia | Categórica | Ciudad de la que viene el estudiante | Explicativa |
| tipo_colegio | Categórica | Tipo de colegio en el que estudió antes de entrar: público o privado | Explicativa |
| fecha_matricula | Fecha | Fecha en la que el estudiante se matriculó | Explicativa |
| estado | Categórica | Situación del estudiante: activo, graduado o desertor | Resultado |
| motivo_retiro | Categórica | Razón por la que se retiró: económico, académico, personal, cambio de institución, laboral o salud; solo tiene valor en los desertores | Resultado |

### 1. Diagnóstico de calidad

El dataset original tiene 10.150 filas y 23 columnas. Estos son los problemas que encontré antes de limpiar:

| Tipo de problema | Columna | Cantidad |
|---|---|---|
| Formato inconsistente (texto con símbolo) | asistencia_pct | 300 celdas con el signo % |
| Faltante disfrazado | asistencia_pct | 202 guiones |
| Faltante disfrazado | horas_trabajo_semana | 2.822 guiones |
| Faltante disfrazado | distancia_km | 152 valores 999 |
| Nulo real | promedio_acumulado | 304 |
| Nulo real | distancia_km | 199 |
| Nulo real | tipo_colegio | 152 |
| Nulo real | ciudad_procedencia | 103 |
| Nulo esperado (no es error) | motivo_retiro | 6.877 (solo tiene valor en los desertores) |
| Duplicados | toda la fila | 150 |
| Error tipográfico | programa | 260 filas (por ejemplo "Ingenieria de Sistemas" y "Psicologia" sin tilde) |
| Error tipográfico | jornada | 485 filas (diurna, nocturna, NOCTURNA) |
| Error tipográfico | genero | 559 filas (M, F, femenino) |
| Error tipográfico | ciudad_procedencia | 542 filas (mayúsculas, minúsculas y tildes distintas) |
| Formato inconsistente (fechas) | fecha_matricula | 3.052 fechas en formato DD/MM/AAAA |
| Valor imposible | promedio_acumulado | 17 mayores a 5 (por ejemplo 45, 62 y 78) |
| Valor imposible | edad | 12 fuera de 15 a 60 (8 con 150 años y 4 con 12 años) |
| Valor imposible | horas_trabajo_semana | 30 mayores a 100 (se ven después de pasar la columna a número) |

La columna `estado` no tiene errores de escritura (solo activo, desertor y graduado), por eso no la modifiqué.

### 2. Decisiones de limpieza

Cada decisión quedó registrada con `registrar()` en `Data/processed/decisiones.csv`.

| Paso | Columna | Acción | Filas | Justificación |
|---|---|---|---|---|
| convertir_numericos | asistencia_pct | Quitar % y cambiar "-" por nulo | 202 | El guion es un faltante disfrazado y el signo % impide calcular promedios. |
| convertir_numericos | horas_trabajo_semana | Cambiar "-" por nulo y pasar a número | 2.822 | El guion significa que no hay dato; como nulo real se puede tratar después. |
| convertir_numericos | distancia_km | Cambiar 999 por nulo | 152 | 999 es un código de "sin dato", no una distancia real. |
| unificar_categorias | programa | Normalizar con strip/lower y unificar variantes | 260 | La misma categoría escrita distinto se contaría como dos grupos. |
| unificar_categorias | jornada | Normalizar con strip/lower y unificar variantes | 485 | La misma categoría escrita distinto se contaría como dos grupos. |
| unificar_categorias | genero | Normalizar con strip/lower y unificar variantes | 559 | La misma categoría escrita distinto se contaría como dos grupos. |
| unificar_categorias | ciudad_procedencia | Normalizar con strip/lower y unificar variantes | 542 | La misma categoría escrita distinto se contaría como dos grupos. |
| convertir_fechas | fecha_matricula | Unificar los dos formatos (AAAA-MM-DD y DD/MM/AAAA) | 3.052 | Pandas no puede interpretar dos formatos a la vez; con formato explícito no se confunden día y mes. |
| eliminar_duplicados | todas las columnas | Eliminar filas idénticas y conservar la primera | 150 | Un id_estudiante identifica a una sola persona; la misma fila repetida contaría dos veces al mismo estudiante. |
| tratar_faltantes | promedio_acumulado | Eliminar filas con nulo | 298 | Una nota no se puede inventar; imputar la mediana daría un dato falso. |
| tratar_faltantes | ciudad_procedencia | Reemplazar nulo por "Sin dato" | 96 | Es una categoría; eliminar la fila perdería al estudiante por un dato que no afecta el resto. |
| tratar_faltantes | tipo_colegio | Reemplazar nulo por "Sin dato" | 145 | Es una categoría; eliminar la fila perdería al estudiante por un dato que no afecta el resto. |
| tratar_imposibles | promedio_acumulado | Eliminar filas con promedio mayor a 5 | 15 | La escala es de 0 a 5; valores como 62 o 78 no son notas posibles y no se pueden adivinar. |
| tratar_imposibles | edad | Reemplazar edades fuera de 15 a 60 por la mediana | 12 | Edades de 150 o 12 años son errores de registro; la mediana no se afecta por valores extremos. |
| tratar_imposibles | horas_trabajo_semana | Poner 0 horas a quien no trabaja | 2.703 | Quien no trabaja tiene 0 horas; el guion original no era un dato perdido. |
| tratar_imposibles | horas_trabajo_semana | Reemplazar horas mayores a 100 por la mediana de quienes trabajan | 29 | Una semana tiene 168 horas y más de 100 de trabajo, además de estudiar, no es realista. |
| crear_variables | desertor | Crear columna True/False a partir de estado | 3.136 | Con True/False el promedio de la columna es directamente la tasa de deserción. |
| crear_variables | cuartil_asistencia | Dividir asistencia_pct en cuatro grupos con qcut | 9.490 | Los cuartiles dan grupos del mismo tamaño y permiten ver si la deserción cambia al bajar la asistencia. |

**Por qué las cifras del diagnóstico y las de las decisiones no coinciden.** Primero se eliminaron los duplicados y las filas sin promedio, y esas filas ya no entraron a los pasos siguientes. Por eso, por ejemplo, había 2.822 guiones en horas pero solo 2.703 quedaron en 0, y había 17 promedios mayores a 5 pero se eliminaron 15.

**Resultado final.** El dataset limpio tiene 9.687 filas (10.150 − 150 duplicados − 298 sin promedio − 15 con promedio imposible) y 25 columnas: las 23 originales más `desertor` y `cuartil_asistencia`.

### 3. Respuestas a las cinco preguntas

Todas las respuestas salen del dataset limpio (9.687 estudiantes). En cada una incluyo cuántos estudiantes hay por grupo, porque una tasa sin ese número no se puede interpretar.

#### Pregunta 1: ¿Qué programa tiene la tasa de deserción más alta?

| Programa | Tasa de deserción | Estudiantes |
|---|---|---|
| Ingeniería Industrial | 40,2 % | 1.271 |
| Ingeniería de Sistemas | 38,2 % | 1.386 |
| Diseño Gráfico | 35,6 % | 848 |
| Enfermería | 31,3 % | 1.132 |
| Derecho | 30,5 % | 1.447 |
| Administración de Empresas | 29,7 % | 1.304 |
| Contaduría Pública | 27,0 % | 1.162 |
| Psicología | 26,0 % | 1.137 |

**Respuesta:** Ingeniería Industrial tiene la tasa más alta: 40,2 % entre 1.271 estudiantes. Ingeniería de Sistemas queda muy cerca (38,2 % entre 1.386) y Psicología es la más baja (26,0 %). Ningún programa tiene pocos estudiantes: el más pequeño es Diseño Gráfico con 848, así que las tasas son confiables. Eso sí, la diferencia entre el primero y el segundo es de solo 2 puntos, por lo que no se puede afirmar con seguridad cuál de los dos es peor.

#### Pregunta 2: ¿Hay diferencia entre becados y no becados?

| Beca | Tasa de deserción | Estudiantes |
|---|---|---|
| No | 36,4 % | 7.004 |
| Sí | 21,9 % | 2.683 |

**Respuesta:** Sí hay diferencia. Los no becados es 36,4 % y los becados 21,9 %, es decir, 14,5 puntos menos.

**¿Prueba que la beca causa la permanencia?** No. Solo muestra que las dos cosas van juntas. Puede que la beca se la den a estudiantes que ya eran buenos o más comprometidos, y esos se habrían quedado de todas formas. Con esta tabla no se puede separar una cosa de la otra.

#### Pregunta 3: ¿Qué jornada tiene el menor promedio acumulado?

| Jornada | Promedio acumulado | Estudiantes |
|---|---|---|
| Nocturna | 3,464 | 2.666 |
| Fin de semana | 3,704 | 949 |
| Diurna | 3,725 | 6.072 |

**Respuesta:** La jornada nocturna tiene el menor promedio: 3,464 entre 2.666 estudiantes, unos 0,26 puntos por debajo de la diurna (3,725). Fin de semana y diurna quedan casi iguales (0,02 de diferencia). Todos los grupos son grandes; el más pequeño tiene 949 estudiantes.

#### Pregunta 4: ¿Cuántas materias reprobadas tienen, en promedio, los desertores frente a los activos?

| Estado | Materias reprobadas (promedio) | Estudiantes |
|---|---|---|
| Activo | 0,623 | 5.692 |
| Desertor | 3,066 | 3.136 |

**Respuesta:** Los desertores reprobaron en promedio 3,066 materias y los activos 0,623, unas 5 veces más.

**¿Por qué se excluyeron los graduados?** La pregunta compara a los que se fueron con los que siguen estudiando. Un graduado ya terminó, así que no pertenece a ninguno de los dos grupos y distorsionaría la comparación. Se excluyeron 859 graduados (9.687 − 5.692 − 3.136).

#### Pregunta 5: ¿La deserción aumenta cuando baja la asistencia?

| Cuartil de asistencia | Tasa de deserción | Estudiantes | Asistencia promedio |
|---|---|---|---|
| Q1 (la más baja) | 61,9 % | 2.385 | 73,9 % |
| Q2 | 36,7 % | 2.386 | 84,4 % |
| Q3 | 20,7 % | 2.348 | 91,3 % |
| Q4 (la más alta) | 9,4 % | 2.371 | 98,7 % |

**Respuesta:** Sí. La deserción baja en cada escalón: de 61,9 % en quienes menos asisten a 9,4 % en quienes más asisten, unas 6 veces menos. Los cuatro grupos tienen un tamaño parecido (alrededor de 2.400), así que la comparación es justa. Quedaron fuera 197 estudiantes sin dato de asistencia (por eso los grupos suman 9.490 y no 9.687).

**¿Es una prueba de causa?** No. Puede que faltar a clase lleve a desertar, pero también puede ser al revés: quien ya piensa irse deja de asistir antes de retirarse. Con estos datos no se sabe cuál ocurre.

### 4. Preguntas sobre los gráficos

**Mapa de faltantes.** Los huecos más visibles están en `motivo_retiro`, porque está vacía en los 6.877 estudiantes que no desertaron. Ese nulo es esperado, no es un error. También se ven huecos pequeños en `promedio_acumulado` (304), `distancia_km` (199), `tipo_colegio` (152) y `ciudad_procedencia` (103). Sí coinciden con los nulos que conté en la auditoría.

**Boxplots antes y después.** Antes de limpiar había promedios de hasta 78 y edades de 150 años, que estiraban el gráfico y hacían que la caja se viera aplastada. Después de limpiar, el promedio queda dentro de la escala de 0 a 5 y la edad entre 15 y 60. Los puntos sueltos que puedan quedar los dejé porque son valores posibles (por ejemplo, estudiantes de más edad o promedios bajos), no errores de registro.

**Tasa por programa.** Ingeniería Industrial tiene la tasa más alta (40,2 % de 1.271 estudiantes). El programa más pequeño es Diseño Gráfico con 848 estudiantes, un grupo grande, así que no hay programas con pocos estudiantes que haya que mirar con cuidado.

### 5. Reflexiones

**Reflexión 1: asociación y causalidad.**
Los becados desertan menos (21,9 % frente a 36,4 % de los no becados), pero eso no prueba que la beca cause la permanencia. Puede que la beca se dé a estudiantes con buen promedio o más comprometidos, que de todas formas se habrían quedado. También puede influir algo que no medimos, como el apoyo de la familia. Para distinguir una causa de una asociación habría que comparar becados y no becados con promedio y condiciones parecidas, o dar la beca al azar y ver qué pasa.

**Reflexión 2: variables que no deberían usarse para predecir.**
No se puede usar `motivo_retiro` para predecir la deserción, porque solo existe después de que el estudiante se va. Tiene valor en 3.273 estudiantes (los que desertaron) y está vacía en los demás, así que el modelo "vería la respuesta" y no serviría con estudiantes activos. Sí sirve para entender por qué se van: el motivo más frecuente es el económico (1.011 de 3.273 retiros). Algo parecido pasa con `estado`, que es el resultado mismo. También hay que tener cuidado con columnas como `semestre` o `creditos_aprobados` si se registraron en el momento del retiro, porque ya incluirían información de la salida. Para predecir se deben usar datos que se conozcan antes, como la asistencia, el promedio o las materias reprobadas.

**Reflexión 3: variables sensibles.**
Género, estrato y ciudad de procedencia pueden reflejar desigualdades sociales. Aunque aparezcan asociadas a la deserción, no deberían usarse para decidir quién recibe apoyo, porque se podría tratar peor a un grupo por su origen y no por su situación real. Además, etiquetar a alguien como "de riesgo" por su estrato puede estigmatizarlo. Es más justo usar variables sobre las que se puede actuar, como la asistencia: el 25 % que menos asiste deserta 61,9 %, frente a 9,4 % del 25 % que más asiste. Si se usan variables sensibles, que sea para revisar si algún grupo recibe menos ayuda, no para negársela.
