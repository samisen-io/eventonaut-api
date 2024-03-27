import requests
import re
def check_url(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }
    try:
        print(url)
        response = requests.get(url, headers=headers)
        print(response.status_code)
        if re.match(r'^2\d{2}$', str(response.status_code)):
            return True
        else:
            return False
    except requests.exceptions.RequestException:
        return False