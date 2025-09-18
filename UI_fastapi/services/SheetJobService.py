import requests
from requests.exceptions import RequestException
from ..app.config import settings

def schedule_sheet_job(sheet_url: str):
    payload = {
        'project': settings.SCRAPYD_PROJECT,
        'spider': 'product_list',
        'sheet_url': sheet_url
    }

    scrapyd_url = f"{settings.SCRAPYD_URL}/schedule.json"

    try:
        response = requests.post(scrapyd_url, data=payload)
        response.raise_for_status()
        return response.json()
    except RequestException as e:
        return ConnectionError("Could not connect to scrapyd.\nDetails: {e}")