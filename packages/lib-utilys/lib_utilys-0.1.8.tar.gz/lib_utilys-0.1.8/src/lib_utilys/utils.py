import re
import json
import logging
from pathlib import Path
from datetime import date, datetime

logger = logging.getLogger(__name__)

def clean_special_characters(string):
        """Replaces special characters in a string with a hyphen."""
        special_chars = ["/", "\\", ":", "*", "?", "\"", "<", ">", "|"]
        for char in special_chars:
            string = string.replace(char, "-")
        return string

def read_json(path: Path) -> dict:
    """Reads a JSON file and returns its content as a dictionary."""
    try:
        with open(path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except Exception:
        logger.exception("Failed to read JSON file at %s", path)
        return {}

def write_json(path, data):
    def _default(o):
        if isinstance(o, (date, datetime)):
            return o.isoformat()
        raise TypeError(f"Type {type(o)} not serializable")

    with open(path, "w") as f:
        json.dump(data, f, indent=4, default=_default)

def extract_business(email_adress: str) -> str | None:
    """Extracts the business name from an email address."""
    match = re.search(r'[\w\.-]+@[\w\.-]+', email_adress)
    extracted_email = match.group(0) if match else email_adress
    email_parts = extracted_email.split("@")
    if len(email_parts) == 2:
        domain_parts = email_parts[1].split(".")
        if len(domain_parts) > 1:
            business_name = domain_parts[0]
            return business_name
    return None

def clean_xml(text: str) -> str:
    return re.sub(r'&(?!amp;|lt;|gt;|quot;|apos;|#\d+;)', '&amp;', text)

