import requests
from requests.exceptions import RequestException
from ..app.config import settings

def schedule_sheet_job(sheet_url: str):

    spider = 'product_list'

    payload = {
        'project': settings.SCRAPYD_PROJECT,
        'spider': spider,
        'sheet_url': sheet_url
    }

    scrapyd_url = f"{settings.SCRAPYD_URL}/schedule.json"

    try:
        response = requests.post(scrapyd_url, data=payload)
        response.raise_for_status()
        result = response.json()
        result['spider'] = spider
        return result
    except RequestException as e:
        return ConnectionError("Could not connect to scrapyd.\nDetails: {e}")