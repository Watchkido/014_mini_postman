"""
exceptions.py
Benutzerdefinierte Ausnahmen für das Projekt.
Hier werden eigene Exception-Klassen definiert.
"""

class CustomError(Exception):
    pass

class ValidationError(CustomError):
    pass
