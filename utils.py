# utils.py

def fstring(template: str, **kwargs):
    """
    Safe and reusable string interpolation using .format().
    Example: fstring("This is {name}", name="Lakshman")
    """
    return template.format(**kwargs)
