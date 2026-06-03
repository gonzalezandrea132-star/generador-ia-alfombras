# Generador IA de Alfombras

Aplicacion en Python para generar diseños personalizados de alfombras a partir de descripciones textuales. El prototipo interpreta colores, forma, estilo y complejidad del diseño, crea una representacion visual y calcula un costo estimado segun tamaño y dificultad.

## Funcionalidades

- Procesamiento basico de lenguaje natural para detectar caracteristicas del texto.
- Generacion visual de alfombras con patrones geometricos, florales, clasicos o abstractos.
- Interfaz interactiva creada con Tkinter.
- Estimacion de costos con base en area, forma y complejidad.

## Requisitos

- Python 3.10 o superior.
- No requiere librerias externas.

## Ejecucion

Aplicacion de escritorio:

```powershell
python app.py
```

Interfaz web para presentar al cliente:

```powershell
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## Configurar IA con OpenAI

La aplicacion funciona de dos formas:

- Sin API: usa reglas locales de procesamiento de lenguaje natural.
- Con API: usa OpenAI para interpretar descripciones mas libres y naturales.

Por seguridad, la API key no debe escribirse dentro del codigo. En Windows PowerShell se configura asi:

```powershell
$env:OPENAI_API_KEY="tu_api_key_nueva"
```

Luego ejecuta:

```powershell
streamlit run streamlit_app.py
```

Si quieres dejarla guardada permanentemente en Windows:

```powershell
setx OPENAI_API_KEY "tu_api_key_nueva"
```

Despues de usar `setx`, cierra y vuelve a abrir PowerShell.

## Ejemplos de descripciones

- `Alfombra rectangular moderna azul y dorada con patrones geometricos para una sala elegante`
- `Alfombra redonda roja y beige con flores detalladas para dormitorio`
- `Alfombra ovalada minimalista gris y blanco para oficina`
- `Alfombra clasica cafe y dorada con arabescos complejos`

## Relacion con los objetivos del proyecto

El sistema cumple el objetivo general al ofrecer una aplicacion Python que transforma una descripcion textual en un diseño visual de alfombra. Ademas, incorpora los objetivos especificos mediante un modulo de interpretacion de texto, un modulo de generacion de imagenes en pantalla, una interfaz grafica y un estimador de costos basado en tamaño y complejidad.

## Como se aplica la inteligencia artificial

En este prototipo la inteligencia artificial se aplica como un sistema basico de procesamiento de lenguaje natural basado en reglas. El programa analiza la descripcion escrita por el usuario, identifica palabras clave como colores, forma, estilo, habitacion y nivel de detalle, y convierte esa informacion en parametros de diseño.

Flujo del sistema:

1. El cliente escribe una descripcion en lenguaje natural.
2. El modulo de NLP interpreta colores, estilo, forma y complejidad.
3. El generador visual crea una representacion de la alfombra.
4. El estimador calcula el costo con base en area, forma y complejidad.

Ejemplo:

`Alfombre en forma de margarita rosa y azul para dormitorio niña`

El sistema interpreta:

- `margarita`: diseño floral y forma de flor.
- `rosa` y `azul`: paleta principal.
- `dormitorio niña`: estilo infantil.
- `forma`: activa una silueta especial.

Para una version mas avanzada, este modulo podria conectarse con un modelo de IA generativa de imagenes o con una API de lenguaje natural, pero para el alcance academico actual funciona como una IA simbolica o sistema experto simple.

## Publicacion gratuita recomendada

Para una entrega academica, la opcion mas simple es publicar `streamlit_app.py` en Streamlit Community Cloud. Esta plataforma genera un enlace publico gratuito con formato `nombre-del-proyecto.streamlit.app`.

Pasos generales:

1. Subir estos archivos a un repositorio de GitHub.
2. Entrar a Streamlit Community Cloud.
3. Crear una nueva app desde el repositorio.
4. Seleccionar `streamlit_app.py` como archivo principal.
5. Compartir el enlace generado.

Si se necesita un dominio propio, la opcion gratuita mas realista para estudiantes es solicitar GitHub Student Developer Pack y usar el beneficio de dominio estudiantil, por ejemplo un dominio `.me` por un año cuando este disponible. Si no se cuenta con ese beneficio, lo mas practico para una entrega sin presupuesto es usar el subdominio gratuito de Streamlit.
