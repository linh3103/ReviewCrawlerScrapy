import requests
from requests.exceptions import RequestException
from ..app.config import settings

def schedule_specific_job(spider_name: str, params: dict):
    payload = {
        'project': settings.SCRAPYD_PROJECT,
        'spider': spider_name,
        **params
    }

    schedule_url = f"{settings.SCRAPYD_URL}/schedule.json"

    try:
        response = requests.post(schedule_url, data=payload)
        response.raise_for_status()
        return response.json()
    except RequestException as e:
        raise ConnectionError(f"Could not connect to scrapyd.\nDetail: {e}")



