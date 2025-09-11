from twisted.internet import threads
from scrapy.core.downloader.handlers.http11 import HTTP11DownloadHandler
from scrapy.http import TextResponse 
import requests

class RequestsDownloadHandler(HTTP11DownloadHandler):
    
    def __init__(self, settings, *args, **kwargs):
        super(RequestsDownloadHandler, self).__init__(settings, *args, **kwargs)
        self.download_timeout = settings.getfloat('DOWNLOAD_TIMEOUT')

    def download_request(self, request, spider):
        return threads.deferToThread(self._download_request, request, spider)

    def _download_request(self, request, spider):
        kwargs = {
            'method': request.method,
            'url': request.url,
            'headers': dict(request.headers.to_unicode_dict()),
            'data': request.body or None,
            'timeout': self.download_timeout,
            'allow_redirects': False,
            'verify': True
        }

        session = request.meta.get('requests_session') or requests.Session()
        response = session.request(**kwargs)
        
        response_headers = dict(response.headers)
        if 'Content-Encoding' in response_headers:
            del response_headers['Content-Encoding']
        if 'content-encoding' in response_headers:
            del response_headers['content-encoding']
            
        return TextResponse(
            url=response.url,
            status=response.status_code,
            headers=response_headers,
            body=response.content,
            encoding=response.encoding or 'utf-8', 
            request=request
        )