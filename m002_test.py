"""
exceptions.py
Benutzerdefinierte Ausnahmen für das Projekt.
Hier werden eigene Exception-Klassen definiert.
"""

class CustomError(Exception):
    pass

class ValidationError(CustomError):
    pass

import argparse

def process_string(input_string: str):
    """
    Verarbeitet einen übergebenen String und gibt ihn aus.

    :param input_string: Der zu verarbeitende String.
    """
    print(f"Verarbeiteter String: {input_string}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Verarbeitet eine übergebene URL.")
    parser.add_argument("--url", required=True, help="Die zu verarbeitende URL.")
    args = parser.parse_args()

    process_string(args.url)
