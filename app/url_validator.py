import requests
import re
def check_url(url):
    try:
        response = requests.get(url)
        if re.match(r'^2\d{2}$', str(response.status_code)):
            return True
        else:
            return False
    except requests.exceptions.RequestException:
        return False