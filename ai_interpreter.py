import json
import os


LAST_API_STATUS = "API no configurada"

ALLOWED_COLORS = [
    "rojo",
    "azul",
    "verde",
    "amarillo",
    "dorado",
    "negro",
    "blanco",
    "gris",
    "morado",
    "rosa",
    "naranja",
    "beige",
    "cafe",
    "lila",
    "violeta",
    "turquesa",
    "celeste",
    "plateado",
    "crema",
]

ALLOWED_STYLES = ["moderno", "minimalista", "clasico", "bohemio", "geometrico", "floral", "infantil", "abstracto", "deportivo"]
ALLOWED_SHAPES = ["rectangular", "redonda", "ovalada", "flor", "nube"]
ALLOWED_MOTIFS = ["ninguno", "carita_feliz", "balon", "flores", "nubes", "estrellas", "corazones", "naturaleza", "fantasia"]


RUG_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "colors": {
            "type": "array",
            "items": {"type": "string", "enum": ALLOWED_COLORS},
            "minItems": 1,
            "maxItems": 4,
        },
        "style": {"type": "string", "enum": ALLOWED_STYLES},
        "shape": {"type": "string", "enum": ALLOWED_SHAPES},
        "complexity": {"type": "integer", "minimum": 1, "maximum": 5},
        "motif": {"type": "string", "enum": ALLOWED_MOTIFS},
    },
    "required": ["colors", "style", "shape", "complexity", "motif"],
}


def get_last_api_status() -> str:
    return LAST_API_STATUS


def interpret_with_openai(description: str) -> dict | None:
    global LAST_API_STATUS
    if not os.getenv("OPENAI_API_KEY"):
        LAST_API_STATUS = "API no configurada: falta OPENAI_API_KEY"
        return None

    try:
        from openai import OpenAI
    except ImportError as error:
        LAST_API_STATUS = f"API no disponible: falta instalar openai ({error})"
        return None

    system_prompt = """
Eres un modulo de IA para una fabrica de alfombras personalizadas.
Tu trabajo es interpretar cualquier solicitud escrita por un cliente y convertirla en parametros de diseno que esta aplicacion pueda dibujar.

Reglas de interpretacion:
- Si el cliente pide una forma que no existe en la lista permitida, elige la forma permitida mas cercana.
- Si pide animales, objetos, personajes, estrellas, planetas, carros, comida o temas fantasia, conserva la idea mediante style y colores, pero usa una forma permitida.
- Si pide flor, margarita o petalos, usa shape "flor" y style "floral".
- Si pide nube o nubes, usa shape "nube" y style "infantil".
- Si pide balon, pelota, futbol o deporte, usa shape "redonda" y style "deportivo".
- Si pide emoji, cara feliz, sonrisa o carita, usa shape "redonda", style "infantil" y motif "carita_feliz".
- Usa motif para conservar la idea principal del cliente cuando la forma permitida no sea suficiente.
- Si pide dormitorio infantil, bebe, nina o nino, usa style "infantil" salvo que haya una instruccion mas especifica.
- Si no menciona colores, elige colores coherentes con la solicitud.
- Complexity: 1 simple, 2 pocos detalles, 3 varios elementos, 4 muy detallado, 5 altamente complejo.
"""

    try:
        client = OpenAI()
        response = client.responses.create(
            model=os.getenv("OPENAI_MODEL", "gpt-5-mini"),
            input=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": description},
            ],
            text={
                "format": {
                    "type": "json_schema",
                    "name": "rug_design_interpretation",
                    "strict": True,
                    "schema": RUG_SCHEMA,
                }
            },
        )
        data = json.loads(response.output_text)
        LAST_API_STATUS = "OpenAI activo con salida estructurada"
    except Exception as error:
        LAST_API_STATUS = f"API fallo: {type(error).__name__}: {error}"
        data = _interpret_with_json_fallback(description)
        if data is None:
            return None

    colors = [color for color in data.get("colors", []) if color in ALLOWED_COLORS]
    style = data.get("style") if data.get("style") in ALLOWED_STYLES else "moderno"
    shape = data.get("shape") if data.get("shape") in ALLOWED_SHAPES else "rectangular"
    motif = data.get("motif") if data.get("motif") in ALLOWED_MOTIFS else "ninguno"

    try:
        complexity = int(data.get("complexity", 1))
    except (TypeError, ValueError):
        complexity = 1

    return {
        "colors": colors[:4] or ["azul", "blanco", "dorado"],
        "style": style,
        "shape": shape,
        "complexity": max(1, min(5, complexity)),
        "motif": motif,
    }


def _interpret_with_json_fallback(description: str) -> dict | None:
    global LAST_API_STATUS
    try:
        from openai import OpenAI

        client = OpenAI()
        response = client.responses.create(
            model=os.getenv("OPENAI_MODEL", "gpt-5-mini"),
            input=(
                "Interpreta esta solicitud de alfombra y responde solo JSON valido. "
                f"Colores permitidos: {ALLOWED_COLORS}. "
                f"Estilos permitidos: {ALLOWED_STYLES}. "
                f"Formas permitidas: {ALLOWED_SHAPES}. "
                f"Motivos permitidos: {ALLOWED_MOTIFS}. "
                "Estructura exacta: "
                '{"colors":["azul","blanco"],"style":"moderno","shape":"rectangular","complexity":1,"motif":"ninguno"}. '
                f"Solicitud: {description}"
            ),
            text={"format": {"type": "json_object"}},
        )
        LAST_API_STATUS = "OpenAI activo con modo JSON de respaldo"
        return json.loads(response.output_text)
    except Exception as error:
        LAST_API_STATUS = f"API fallo tambien en respaldo: {type(error).__name__}: {error}"
        return None
