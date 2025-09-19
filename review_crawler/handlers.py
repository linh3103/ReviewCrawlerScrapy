from twisted.internet import threads
from scrapy.core.downloader.handlers.http11 import HTTP11DownloadHandler
from scrapy.http import TextResponse 
import requests
from requests.exceptions import Timeout, RequestException
from scrapy.exceptions import IgnoreRequest
import logging

class RequestsDownloadHandler(HTTP11DownloadHandler):
    
    def __init__(self, settings, *args, **kwargs):
        super(RequestsDownloadHandler, self).__init__(settings, *args, **kwargs)
        # Mặc định 30 giây nếu không set trong settings
        self.download_timeout = settings.getfloat('DOWNLOAD_TIMEOUT', 30.0)
        self.logger = logging.getLogger(__name__)

    def download_request(self, request, spider):
        return threads.deferToThread(self._download_request, request, spider)

    def _download_request(self, request, spider):
        kwargs = {
            'method': request.method,
            'url': request.url,
            'headers': dict(request.headers.to_unicode_dict()),
            'data': request.body or None,
            'timeout': self.download_timeout,  # Timeout 30 giây
            'allow_redirects': False,
            'verify': True
        }

        try:
            session = request.meta.get('requests_session') or requests.Session()
            
            self.logger.info(f"Making request to {request.url} with timeout {self.download_timeout}s")
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
            
        except Timeout as e:
            self.logger.error(f"Timeout after {self.download_timeout}s for {request.url}")
            # Signal spider to close
            spider.crawler.engine.close_spider(spider, f'Request timeout after {self.download_timeout}s')
            raise IgnoreRequest(f"Timeout after {self.download_timeout}s: {e}")
            
        except RequestException as e:
            self.logger.error(f"Request failed for {request.url}: {e}")
            spider.crawler.engine.close_spider(spider, f'Request failed: {e}')
            raise IgnoreRequest(f"Request failed: {e}")