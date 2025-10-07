"""
exceptions.py
Benutzerdefinierte Ausnahmen für das Projekt.
Hier werden eigene Exception-Klassen definiert.
"""
from linkedin_api.clients.restli.client import RestliClient
from env_config import Config

client = RestliClient()
response = client.get(
    resource_path="/me",
    access_token=Config.linkedin.linkedin_access_token
)

print(response)
