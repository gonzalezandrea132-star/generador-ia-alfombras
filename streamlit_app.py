import html
import math
import re
from dataclasses import dataclass
from difflib import get_close_matches
from unicodedata import normalize

import streamlit as st
import streamlit.components.v1 as components

from ai_interpreter import get_last_api_status, interpret_with_openai
from image_generator import generate_rug_image, get_last_image_status


LOGO_PATH = "logo.PNG"

COLORS = {
    "rojo": "#b23a48",
    "azul": "#2f67b1",
    "verde": "#3f8f5f",
    "amarillo": "#e0b83f",
    "dorado": "#c79b39",
    "negro": "#222222",
    "blanco": "#f3f0e8",
    "gris": "#7f858f",
    "morado": "#7a4ca0",
    "rosa": "#d26f9d",
    "naranja": "#d96c35",
    "beige": "#c9b79c",
    "cafe": "#76523a",
    "marron": "#76523a",
    "lila": "#9c6ac4",
    "violeta": "#7a4ca0",
    "turquesa": "#2aa6a1",
    "celeste": "#80bfe8",
    "plateado": "#b7bcc6",
    "crema": "#eadcc4",
}

COLOR_ALIASES = {
    "fucsia": "rosa",
    "rosada": "rosa",
    "azulado": "azul",
    "azulada": "azul",
    "menta": "verde",
    "esmeralda": "verde",
    "vino": "rojo",
    "bordo": "rojo",
    "terracota": "naranja",
    "chocolate": "cafe",
    "madera": "cafe",
    "arena": "beige",
    "perla": "blanco",
}

STYLES = {
    "moderno": "moderno",
    "minimalista": "minimalista",
    "clasico": "clasico",
    "clásico": "clasico",
    "bohemio": "bohemio",
    "geometrico": "geometrico",
    "geométrico": "geometrico",
    "floral": "floral",
    "infantil": "infantil",
    "abstracto": "abstracto",
    "deportivo": "deportivo",
    "deportiva": "deportivo",
    "futbol": "deportivo",
    "fútbol": "deportivo",
    "balon": "deportivo",
    "balón": "deportivo",
    "elegante": "clasico",
    "lujoso": "clasico",
    "lujosa": "clasico",
    "juvenil": "moderno",
    "divertido": "infantil",
    "divertida": "infantil",
    "romantico": "floral",
    "romantica": "floral",
    "natural": "bohemio",
    "rustico": "bohemio",
    "rustica": "bohemio",
}

SHAPES = {
    "rectangular": "rectangular",
    "redonda": "redonda",
    "redondo": "redonda",
    "circular": "redonda",
    "ovalada": "ovalada",
    "ovalado": "ovalada",
    "flor": "flor",
    "floral": "flor",
    "margarita": "flor",
    "estrella": "redonda",
    "corazon": "redonda",
    "corazón": "redonda",
    "nube": "nube",
    "balon": "redonda",
    "balón": "redonda",
    "pelota": "redonda",
}

THEME_HINTS = {
    "sala": "moderno",
    "comedor": "clasico",
    "oficina": "minimalista",
    "habitacion": "minimalista",
    "habitación": "minimalista",
    "dormitorio": "infantil",
    "nina": "infantil",
    "niña": "infantil",
    "nino": "infantil",
    "niño": "infantil",
    "bebe": "infantil",
    "bebé": "infantil",
    "jardin": "floral",
    "jardín": "floral",
    "playa": "bohemio",
    "naturaleza": "bohemio",
}


@dataclass
class RugDesign:
    description: str
    colors: list[str]
    color_names: list[str]
    style: str
    shape: str
    width: float
    height: float
    complexity: int
    source: str = "local"
    motif: str = "ninguno"

    @property
    def area(self) -> float:
        return self.width * self.height


class RugNLP:
    def analyze(self, description: str, width: float, height: float) -> RugDesign:
        ai_result = interpret_with_openai(description)
        if ai_result:
            colors = [COLORS.get(color, "#2f67b1") for color in ai_result["colors"]]
            color_names = ai_result["colors"]
            if len(colors) == 1:
                colors.append("#f3f0e8")
                color_names.append("blanco")
            return RugDesign(
                description=description,
                colors=colors[:4],
                color_names=color_names[:4],
                style=ai_result["style"],
                shape=ai_result["shape"],
                width=width,
                height=height,
                complexity=ai_result["complexity"],
                source="OpenAI",
                motif=ai_result.get("motif", "ninguno"),
            )

        text = description.lower()
        text = self._normalize_text(text)
        tokens = self._tokens(text)
        color_pairs = self._detect_colors(tokens)
        colors = [color for name, color in color_pairs]
        color_names = [name for name, color in color_pairs]
        style = self._detect_value(tokens, STYLES, "moderno")
        shape = self._detect_value(tokens, SHAPES, "rectangular")

        for word, hinted_style in THEME_HINTS.items():
            if self._has_word(tokens, word) and style == "moderno":
                style = hinted_style

        if any(word in text for word in ["margarita", "flor", "flores", "petalos", "pétalos"]):
            style = "floral"
            shape = "flor" if "forma" in text else shape
        if "nube" in text or "nubes" in text:
            shape = "nube"
            style = "infantil" if style == "moderno" else style
        if any(word in text for word in ["balon", "balón", "pelota", "futbol", "fútbol"]):
            shape = "redonda"
            style = "deportivo"
        motif = "ninguno"
        if any(word in text for word in ["emoji", "cara", "feliz", "sonrisa", "carita"]):
            shape = "redonda"
            style = "infantil"
            motif = "carita_feliz"
        if any(word in text for word in ["nina", "niña", "infantil", "dormitorio"]):
            style = "infantil" if style == "moderno" else style

        if not colors:
            colors = ["#d26f9d", "#2f67b1", "#f3f0e8"]
            color_names = ["rosa", "azul", "blanco"]
        elif len(colors) == 1:
            colors.append("#f3f0e8")
            color_names.append("blanco")

        complexity_words = [
            "detallado",
            "detallada",
            "complejo",
            "compleja",
            "patrones",
            "figuras",
            "flores",
            "arabescos",
            "mandala",
            "geometrico",
            "geométrico",
            "abstracto",
        ]
        complexity = 1 + min(4, sum(1 for word in complexity_words if word in text))

        return RugDesign(
            description=description,
            colors=colors[:4],
            color_names=color_names[:4],
            style=style,
            shape=shape,
            width=width,
            height=height,
            complexity=complexity,
            source="local",
            motif=motif,
        )

    def _normalize_text(self, text: str) -> str:
        replacements = {
            "alfombre": "alfombra",
            "geometrica": "geometrico",
            "geométrica": "geométrico",
            "petalos": "pétalos",
        }
        for wrong, right in replacements.items():
            text = text.replace(wrong, right)
        text = normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
        return text

    def _tokens(self, text: str) -> list[str]:
        return re.findall(r"[a-zA-ZñÑ]+", text)

    def _has_word(self, tokens: list[str], word: str) -> bool:
        normalized = self._normalize_text(word)
        if normalized in tokens:
            return True
        return bool(get_close_matches(normalized, tokens, n=1, cutoff=0.86))

    def _detect_value(self, tokens: list[str], options: dict[str, str], default: str) -> str:
        normalized_options = {self._normalize_text(key): value for key, value in options.items()}
        for token in tokens:
            if token in normalized_options:
                return normalized_options[token]
            close = get_close_matches(token, normalized_options.keys(), n=1, cutoff=0.86)
            if close:
                return normalized_options[close[0]]
        return default

    def _detect_colors(self, tokens: list[str]) -> list[tuple[str, str]]:
        normalized_colors = {self._normalize_text(key): (key, value) for key, value in COLORS.items()}
        detected = []
        for token in tokens:
            color_name = COLOR_ALIASES.get(token, token)
            if color_name in normalized_colors:
                detected.append(normalized_colors[color_name])
                continue
            close = get_close_matches(color_name, normalized_colors.keys(), n=1, cutoff=0.84)
            if close:
                detected.append(normalized_colors[close[0]])
        return list(dict.fromkeys(detected))


class CostEstimator:
    BASE_PRICE_PER_M2 = 85000
    COMPLEXITY_FACTOR = 0.18

    def estimate(self, design: RugDesign) -> int:
        base = design.area * self.BASE_PRICE_PER_M2
        complexity_charge = base * (design.complexity - 1) * self.COMPLEXITY_FACTOR
        shape_charge = base * 0.08 if design.shape != "rectangular" else 0
        return round(base + complexity_charge + shape_charge)


def shape_markup(design: RugDesign) -> str:
    if design.shape == "redonda":
        return """
        <ellipse cx="300" cy="215" rx="220" ry="170" class="base"/>
        <ellipse cx="300" cy="215" rx="190" ry="140" class="border"/>
        """
    if design.shape == "ovalada":
        return """
        <ellipse cx="300" cy="215" rx="245" ry="135" class="base"/>
        <ellipse cx="300" cy="215" rx="210" ry="105" class="border"/>
        """
    if design.shape == "flor":
        petals = []
        for index in range(10):
            angle = (2 * math.pi / 10) * index
            cx = 300 + math.cos(angle) * 120
            cy = 215 + math.sin(angle) * 82
            petals.append(f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="78" ry="52" class="base"/>')
        petals.append('<ellipse cx="300" cy="215" rx="105" ry="80" class="base"/>')
        petals.append('<ellipse cx="300" cy="215" rx="74" ry="52" class="border"/>')
        return "\n".join(petals)
    if design.shape == "nube":
        return """
        <g class="cloud-shape">
          <ellipse cx="155" cy="235" rx="92" ry="58" class="base"/>
          <ellipse cx="230" cy="188" rx="98" ry="76" class="base"/>
          <ellipse cx="325" cy="168" rx="112" ry="86" class="base"/>
          <ellipse cx="430" cy="215" rx="98" ry="66" class="base"/>
          <ellipse cx="300" cy="260" rx="210" ry="72" class="base"/>
          <path d="M118 252 C128 181 188 154 234 171 C263 113 358 97 401 164 C470 159 514 206 495 264 C484 308 446 330 394 330 L195 330 C137 330 102 297 118 252 Z" class="border"/>
        </g>
        """
    return """
    <rect x="65" y="55" width="470" height="320" rx="10" class="base"/>
    <rect x="92" y="82" width="416" height="266" rx="7" class="border"/>
    """


def pattern_markup(design: RugDesign) -> str:
    palette = design.colors[1:] or ["#f3f0e8"]
    pieces = []

    if design.motif == "carita_feliz":
        pieces.append('<circle cx="300" cy="215" r="132" fill="#ffd84d" stroke="#2b2b2b" stroke-width="5"/>')
        pieces.append('<circle cx="252" cy="182" r="15" fill="#2b2b2b"/>')
        pieces.append('<circle cx="348" cy="182" r="15" fill="#2b2b2b"/>')
        pieces.append('<path d="M235 235 C258 286 342 286 365 235" fill="none" stroke="#2b2b2b" stroke-width="12" stroke-linecap="round"/>')
        pieces.append('<circle cx="300" cy="215" r="116" fill="none" stroke="#fff3a3" stroke-width="10" opacity=".7"/>')
    elif design.style == "deportivo":
        pieces.append('<circle cx="300" cy="215" r="132" fill="#f3f0e8" stroke="#222222" stroke-width="5"/>')
        center_points = []
        for index in range(5):
            angle = -math.pi / 2 + index * 2 * math.pi / 5
            center_points.append(f"{300 + math.cos(angle) * 42:.1f},{215 + math.sin(angle) * 42:.1f}")
        pieces.append(f'<polygon points="{" ".join(center_points)}" fill="#222222"/>')
        for index in range(5):
            angle = -math.pi / 2 + index * 2 * math.pi / 5
            px = 300 + math.cos(angle) * 98
            py = 215 + math.sin(angle) * 82
            patch_points = []
            for side in range(5):
                patch_angle = angle + side * 2 * math.pi / 5
                patch_points.append(f"{px + math.cos(patch_angle) * 26:.1f},{py + math.sin(patch_angle) * 26:.1f}")
            pieces.append(f'<polygon points="{" ".join(patch_points)}" fill="#222222"/>')
            pieces.append(f'<line x1="300" y1="215" x2="{px:.1f}" y2="{py:.1f}" stroke="#222222" stroke-width="3" opacity=".7"/>')
    elif design.shape == "nube":
        decorations = [(235, 205, 9), (300, 235, 7), (365, 198, 8), (415, 258, 6), (190, 260, 6)]
        for index, (x, y, radius) in enumerate(decorations):
            color = palette[index % len(palette)]
            pieces.append(f'<circle cx="{x}" cy="{y}" r="{radius}" fill="{color}" opacity=".55"/>')
        pieces.append('<path d="M218 285 C268 306 337 306 388 285" fill="none" stroke="#ffffff" stroke-width="7" stroke-linecap="round" opacity=".72"/>')
    elif design.style in ("geometrico", "moderno", "minimalista"):
        columns = 3 + design.complexity
        rows = 2 + design.complexity
        for row in range(rows):
            for col in range(columns):
                color = palette[(row + col) % len(palette)]
                x = 110 + col * (380 / columns)
                y = 105 + row * (210 / rows)
                size = min(48, 180 / rows)
                if (row + col) % 2 == 0:
                    pieces.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{size:.1f}" height="{size:.1f}" fill="{color}" opacity=".9"/>')
                else:
                    pieces.append(f'<circle cx="{x + size / 2:.1f}" cy="{y + size / 2:.1f}" r="{size / 2:.1f}" fill="{color}" opacity=".9"/>')
    elif design.style == "floral":
        flowers = 4 + design.complexity * 2
        for index in range(flowers):
            angle = (2 * math.pi / flowers) * index
            cx = 300 + math.cos(angle) * (50 + design.complexity * 16)
            cy = 215 + math.sin(angle) * (35 + design.complexity * 13)
            color = palette[index % len(palette)]
            for petal in range(6):
                petal_angle = (2 * math.pi / 6) * petal
                px = cx + math.cos(petal_angle) * 16
                py = cy + math.sin(petal_angle) * 16
                pieces.append(f'<ellipse cx="{px:.1f}" cy="{py:.1f}" rx="14" ry="8" fill="{color}" opacity=".9"/>')
            pieces.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="7" fill="#f3f0e8"/>')
    elif design.style == "clasico":
        color = palette[0]
        for offset in range(0, design.complexity * 16, 16):
            pieces.append(f'<rect x="{125 + offset}" y="{115 + offset}" width="{350 - offset * 2}" height="{200 - offset * 2}" rx="8" fill="none" stroke="{color}" stroke-width="3"/>')
        for index in range(8 + design.complexity * 2):
            x = 115 + index * (370 / max(1, 7 + design.complexity * 2))
            pieces.append(f'<path d="M{x:.1f},125 Q{x + 20:.1f},92 {x + 40:.1f},125" fill="none" stroke="{color}" stroke-width="3"/>')
            pieces.append(f'<path d="M{x:.1f},305 Q{x + 20:.1f},338 {x + 40:.1f},305" fill="none" stroke="{color}" stroke-width="3"/>')
    else:
        for index in range(6 + design.complexity * 3):
            color = palette[index % len(palette)]
            x = 105 + (index * 41) % 365
            y = 105 + (index * 59) % 205
            pieces.append(f'<ellipse cx="{x}" cy="{y}" rx="48" ry="24" fill="{color}" opacity=".58"/>')

    return "\n".join(pieces)


def render_svg(design: RugDesign) -> str:
    main = design.colors[0]
    border = design.colors[1]
    if design.motif == "carita_feliz":
        main = "#ffd84d"
        border = "#2b2b2b"
    elif design.style == "deportivo":
        main = "#f3f0e8"
        border = "#222222"
    if design.shape == "nube":
        main = "#dff3ff" if main == "#80bfe8" else main
        border = "#80bfe8"
    escaped_description = html.escape(design.description)
    return f"""
    <div class="preview-shell">
      <svg viewBox="0 0 600 430" role="img" aria-label="Vista previa de alfombra generada">
        <defs>
          <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
            <feDropShadow dx="0" dy="12" stdDeviation="12" flood-color="#2b2924" flood-opacity=".18"/>
          </filter>
          <style>
            .base {{ fill: {main}; stroke: {border}; stroke-width: 12; filter: url(#shadow); }}
            .border {{ fill: none; stroke: {border}; stroke-width: 4; opacity: .95; }}
          </style>
        </defs>
        {shape_markup(design)}
        {pattern_markup(design)}
      </svg>
      <p>{escaped_description}</p>
    </div>
    """


def app_styles() -> None:
    st.markdown(
        """
        <style>
          .stApp {
            background: #eef5ff;
            color: #0b1f3a;
          }
          .block-container {
            max-width: 1120px;
            padding-top: 32px;
          }
          section[data-testid="stSidebar"] {
            background: #e8f1ff;
            border-right: 1px solid #bdd2f2;
          }
          section[data-testid="stSidebar"] h2,
          section[data-testid="stSidebar"] label {
            color: #162326;
          }
          h1 {
            font-size: 2.35rem;
            line-height: 1.05;
            color: #071b36;
            margin-bottom: 4px;
          }
          div.stButton > button {
            background: #123fbd;
            border: 1px solid #123fbd;
            color: #ffffff;
            border-radius: 8px;
            font-weight: 700;
          }
          div.stButton > button:hover {
            background: #0d2f91;
            border-color: #0d2f91;
            color: #ffffff;
          }
          div[data-testid="stMetric"] {
            background: #ffffff;
            border: 1px solid #c9d8ee;
            border-radius: 8px;
            padding: 14px 16px;
          }
          .preview-shell {
            background: #f8fbff;
            border: 1px solid #c9d8ee;
            border-radius: 8px;
            padding: 12px;
          }
          .preview-shell p {
            margin: 0 8px 6px;
            color: #233a5a;
            font-size: 14px;
          }
          .brand-row {
            display: flex;
            align-items: center;
            gap: 18px;
            margin-bottom: 18px;
          }
          .brand-row img {
            width: 128px;
            height: auto;
          }
          .brand-copy p {
            margin: 6px 0 0;
            color: #4f5f5c;
            font-size: 16px;
          }
          div[data-testid="stAlert"] {
            border-radius: 8px;
          }
          .stNumberInput button {
            color: #123fbd;
          }
        </style>
        """,
        unsafe_allow_html=True,
    )


def main() -> None:
    st.set_page_config(page_title="Generador IA de Alfombras", layout="wide")
    app_styles()

    logo_col, title_col = st.columns([0.16, 0.84], vertical_alignment="center")
    with logo_col:
        st.image(LOGO_PATH, width=130)
    with title_col:
        st.title("Generador IA de Alfombras")
        st.write("Disena una alfombra personalizada a partir de una descripcion del cliente y calcula un valor estimado.")

    default_description = "Alfombra rectangular moderna azul y dorada con patrones geometricos para una sala elegante"
    with st.sidebar:
        st.image(LOGO_PATH, width=190)
        st.header("Solicitud del cliente")
        description = st.text_area("Descripcion", value=default_description, height=160)
        width_col, height_col = st.columns(2)
        with width_col:
            width = st.number_input("Ancho (m)", min_value=0.5, max_value=10.0, value=2.0, step=0.1)
        with height_col:
            height = st.number_input("Alto (m)", min_value=0.5, max_value=10.0, value=1.5, step=0.1)
        generate = st.button("Interpretar diseño", type="primary", use_container_width=True)
        generate_ai_image = st.button("Generar imagen IA", use_container_width=True)
        st.caption("La imagen IA usa creditos de OpenAI. La vista previa tecnica no consume creditos.")

    if generate_ai_image:
        with st.spinner("Generando imagen clara con OpenAI..."):
            st.session_state["generated_rug_image"] = generate_rug_image(description, width, height)
            st.session_state["generated_rug_description"] = description
    elif generate:
        st.session_state.pop("generated_rug_image", None)
        st.session_state.pop("generated_rug_description", None)

    design = RugNLP().analyze(description, width, height)
    cost = CostEstimator().estimate(design)

    left, right = st.columns([1.35, 1])
    with left:
        generated_image = st.session_state.get("generated_rug_image")
        generated_description = st.session_state.get("generated_rug_description")
        if generated_image and generated_description == description:
            st.image(generated_image, caption=description, use_container_width=True)
        else:
            components.html(render_svg(design), height=520)

    with right:
        st.subheader("Interpretacion del sistema")
        st.info(f"Motor: {design.source} | Estado: {get_last_api_status()}")
        st.caption(get_last_image_status())
        st.metric("Costo estimado", f"${cost:,.0f} COP")
        st.metric("Area", f"{design.area:.2f} m²")
        st.metric("Complejidad", f"{design.complexity}/5")
        st.write(f"**Estilo detectado:** {design.style}")
        st.write(f"**Forma detectada:** {design.shape}")
        st.write(f"**Colores detectados:** {', '.join(design.color_names)}")
        st.write(f"**Motivo detectado:** {design.motif}")

        st.subheader("Parametros del calculo")
        st.write("Precio base: $85.000 COP por m²")
        st.write("Ajuste por complejidad: 18% por nivel adicional")
        st.write("Ajuste por forma especial: 8% si no es rectangular")

    if generate:
        st.toast("Diseño generado correctamente")


if __name__ == "__main__":
    main()
