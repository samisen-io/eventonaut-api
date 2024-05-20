import http.client
from urllib.parse import urlparse
import logging
import re

def check_url(url):
    try:
        parsed_url = urlparse(url)
        conn = http.client.HTTPSConnection(parsed_url.netloc) if parsed_url.scheme == 'https' else http.client.HTTPConnection(parsed_url.netloc)
        conn.request("GET", parsed_url.path)
        response = conn.getresponse()
        if re.match(r'^[23]\d{2}$', str(response.status)):
            return True
        else:
            return False
    except Exception as e:
        logging.error(f"Error: {e}")
        raise e