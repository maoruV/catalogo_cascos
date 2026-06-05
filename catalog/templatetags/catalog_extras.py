from django import template
from django.template.defaultfilters import floatformat

register = template.Library()


@register.filter
def cop_price(value):
    """Formatea un valor numérico como precio en pesos colombianos (COP).

    Ejemplos:
        1200000.00  → $ 1.200.000
        25000.50    → $ 25.000
        0           → $ 0
    """
    if value is None:
        return "$ 0"

    try:
        # Redondear a entero (COP no usa decimales en display)
        entero = int(round(float(value)))
    except (ValueError, TypeError):
        return f"$ {value}"

    # Formatear con separador de miles: .
    if entero < 0:
        return f"- $ {abs(entero):,}".replace(",", ".")
    return f"$ {entero:,}".replace(",", ".")
