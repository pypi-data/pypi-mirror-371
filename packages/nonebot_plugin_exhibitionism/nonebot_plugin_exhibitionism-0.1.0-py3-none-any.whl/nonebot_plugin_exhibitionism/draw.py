import io
from functools import lru_cache
from pathlib import Path

from pygments import highlight
from pygments.lexers import Python3Lexer
from pygments.formatters import ImageFormatter
from pygments.styles import get_style_by_name
from PIL import Image

PYGMENTS_LEXER = Python3Lexer()
STYLE_NAME = 'one-dark'
STYLE = get_style_by_name(STYLE_NAME)
BACKGROUND_COLOR = STYLE.background_color
font_path = Path(__file__).parent / "font.ttf"


@lru_cache(maxsize=16)
def code_to_jpeg(code_string: str) -> bytes:
    pygments_formatter = ImageFormatter(
        style=STYLE,
        font_name=str(font_path),
        font_size=22,
        line_numbers=True,
        line_number_bg=BACKGROUND_COLOR,
        line_number_fg="#8f908a",
        line_pad=15,
        image_pad=30,
        image_format="PNG"
    )

    highlighted_code_bytes = highlight(
        code_string.strip(), PYGMENTS_LEXER, pygments_formatter)

    png_image = Image.open(io.BytesIO(highlighted_code_bytes))

    if png_image.mode == 'RGBA':
        background = Image.new('RGB', png_image.size, (255, 255, 255))
        background.paste(png_image, mask=png_image.split()[3])
        rgb_image = background
    else:
        rgb_image = png_image.convert('RGB')

    jpeg_buffer = io.BytesIO()
    rgb_image.save(jpeg_buffer, format='JPEG', quality=85)

    jpeg_bytes = jpeg_buffer.getvalue()

    return jpeg_bytes
