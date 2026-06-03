import base64
import os
from urllib.request import urlopen


LAST_IMAGE_STATUS = "Generacion de imagen no solicitada"


def get_last_image_status() -> str:
    return LAST_IMAGE_STATUS


def generate_rug_image(description: str, width: float, height: float) -> bytes | None:
    global LAST_IMAGE_STATUS

    if not os.getenv("OPENAI_API_KEY"):
        LAST_IMAGE_STATUS = "No se genero imagen: falta OPENAI_API_KEY"
        return None

    try:
        from openai import OpenAI
    except ImportError as error:
        LAST_IMAGE_STATUS = f"No se genero imagen: falta instalar openai ({error})"
        return None

    prompt = f"""
Dibuja una imagen clara y presentable de una alfombra personalizada vista desde arriba.

Solicitud del cliente:
{description}

Medidas aproximadas: {width:.2f} metros de ancho por {height:.2f} metros de alto.

Requisitos visuales:
- Debe parecer una alfombra real o un diseno profesional de alfombra.
- Debe verse centrada, completa, sin texto, sin marcas de agua y sin fondo distractor.
- Usa una vista superior tipo catalogo para cliente.
- Si el cliente pide un personaje, animal, emoji, balon, flor, nube u objeto, representalo claramente como motivo principal de la alfombra.
- Mantén bordes definidos y colores coherentes con la solicitud.
"""

    try:
        client = OpenAI()
        response = client.responses.create(
            model=os.getenv("OPENAI_IMAGE_MODEL", "gpt-5-nano"),
            input=prompt,
            tools=[
                {
                    "type": "image_generation",
                    "size": "1024x1024",
                    "quality": "medium",
                    "background": "opaque",
                }
            ],
            tool_choice={"type": "image_generation"},
        )
        image_data = [output.result for output in response.output if output.type == "image_generation_call"]
        if not image_data:
            LAST_IMAGE_STATUS = "OpenAI respondio, pero no devolvio imagen"
            return None

        LAST_IMAGE_STATUS = "Imagen generada con OpenAI"
        return base64.b64decode(image_data[0])
    except Exception as error:
        fallback = _generate_with_images_api(client, prompt)
        if fallback:
            return fallback
        LAST_IMAGE_STATUS = f"No se pudo generar imagen: {type(error).__name__}: {error}"
        return None


def _generate_with_images_api(client, prompt: str) -> bytes | None:
    global LAST_IMAGE_STATUS

    try:
        response = client.images.generate(
            model=os.getenv("OPENAI_IMAGE_FALLBACK_MODEL", "dall-e-3"),
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1,
            response_format="b64_json",
        )
        image_base64 = response.data[0].b64_json
        if image_base64:
            LAST_IMAGE_STATUS = "Imagen generada con OpenAI mediante modelo alternativo"
            return base64.b64decode(image_base64)

        image_url = response.data[0].url
        if image_url:
            LAST_IMAGE_STATUS = "Imagen generada con OpenAI mediante URL alternativa"
            with urlopen(image_url, timeout=30) as result:
                return result.read()
    except Exception as error:
        LAST_IMAGE_STATUS = f"Tambien fallo el modelo alternativo de imagen: {type(error).__name__}: {error}"

    return None
