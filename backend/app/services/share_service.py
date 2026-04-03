from io import BytesIO

from PIL import Image, ImageDraw, ImageFont

from app.core.config import get_settings
from app.schemas.compare import CompareResponse


def _safe_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    try:
        return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", size=size)
    except OSError:
        return ImageFont.load_default()


def generate_comparison_image(compare_data: CompareResponse) -> bytes:
    settings = get_settings()
    image = Image.new("RGB", (settings.share_image_width, settings.share_image_height), "#F4F1EA")
    draw = ImageDraw.Draw(image)

    title_font = _safe_font(56)
    heading_font = _safe_font(42)
    body_font = _safe_font(28)

    draw.rectangle((0, 0, settings.share_image_width, 150), fill="#083D77")
    draw.text((60, 42), "Pulso Civico | Comparador", font=title_font, fill="white")

    draw.rectangle((40, 220, 500, 1240), outline="#083D77", width=4)
    draw.rectangle((580, 220, 1040, 1240), outline="#DA4167", width=4)

    left = compare_data.left_candidate
    right = compare_data.right_candidate
    draw.text((70, 260), left.name, font=heading_font, fill="#083D77")
    draw.text((70, 320), f"{left.party} | {left.region}", font=body_font, fill="#333333")
    draw.text((610, 260), right.name, font=heading_font, fill="#DA4167")
    draw.text((610, 320), f"{right.party} | {right.region}", font=body_font, fill="#333333")

    y_left = 400
    for proposal in compare_data.left_proposals[:6]:
        draw.text((70, y_left), f"{proposal.axis}: {proposal.title}", font=body_font, fill="#111111")
        y_left += 110

    y_right = 400
    for proposal in compare_data.right_proposals[:6]:
        draw.text((610, y_right), f"{proposal.axis}: {proposal.title}", font=body_font, fill="#111111")
        y_right += 110

    draw.text((60, 1280), "Fuente: Pulso Civico con datos documentados", font=body_font, fill="#555555")

    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()

