from math import ceil
import io

from django.conf import settings
from django.http import FileResponse
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from .constants import (FONT_REG, FONT_MED, BIG_FONT, SMALL_FONT,
                        PAGE_FONT, ROWS_PER_PAGE, ROW_STEP)

basedir = settings.BASE_DIR / 'api' / 'static' / 'api'
pdfmetrics.registerFont(TTFont(FONT_MED, str(
    basedir / 'fonts' / f'{FONT_MED}.ttf')))
pdfmetrics.registerFont(TTFont(FONT_REG, str(
    basedir / 'fonts' / f'{FONT_REG}.ttf')))
image = str(basedir / 'images' / 'logo.jpeg')


def save_shopping_file(ingredients):
    buffer = io.BytesIO()
    cart_file = canvas.Canvas(buffer)
    pages = ceil(len(ingredients) / ROWS_PER_PAGE)
    for page in range(1, pages + 1):
        start = (page - 1) * ROWS_PER_PAGE
        ingredients_on_page = ingredients[start:start + ROWS_PER_PAGE]
        cart_file.setFont(FONT_MED, BIG_FONT)
        x, y = 70, 770
        cart_file.drawString(x, y, f'Список покупок из{' ' * 26}:')
        cart_file.setFont(FONT_REG, SMALL_FONT)
        y -= ROW_STEP
        for name, amount in ingredients_on_page:
            y -= ROW_STEP
            cart_file.drawString(x, y, f'● {name}')
            cart_file.drawString(430, y, f'{amount}')
        cart_file.drawInlineImage(image, 317, 766.4, width=120, height=35)
        cart_file.drawInlineImage(image, 200, 50, width=200, height=60)
        cart_file.setFont(FONT_REG, PAGE_FONT)
        cart_file.drawString(300, 100, f'Страница {page} из {pages}')
        cart_file.showPage()
    cart_file.save()
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename="shopping.pdf")
