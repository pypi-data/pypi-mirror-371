import time
import mycdp
from loguru import logger


class XHRListener:
    def __init__(self):
        self.xhr_requests = []
        self.last_xhr_request = None
        self.page = None

    def listenXHR(self, page):
        # Reset requests and timestamp
        self.xhr_requests = []
        self.last_xhr_request = None
        self.page = page

        async def handler(evt):
            # Get AJAX requests
            if evt.type_ in [mycdp.network.ResourceType.XHR,
                             mycdp.network.ResourceType.FETCH,
                             mycdp.network.ResourceType.PREFETCH,
                             # mycdp.network.ResourceType.PREFLIGHT,
                             ]:
                logger.debug(f"XHR request received: {evt} - {evt.response.url}")
                self.xhr_requests.append([evt.response.url, evt.request_id])
                self.last_xhr_request = time.time()
        page.add_handler(mycdp.network.ResponseReceived, handler)
        logger.debug(f"Listening XHR on page: {page}")

    @logger.catch
    async def receiveXHR(self, page=None):
        if page is None:
            page = self.page
        logger.debug(f'receiveXHR: {self.xhr_requests}')
        logger.debug(f"Receiving XHR on page: {page}")
        responses = []
        retries = 0
        max_retries = 3
        # Wait at least 2 seconds after last XHR request for more
        while True:
            if self.last_xhr_request is None or retries > max_retries:
                break
            if time.time() - self.last_xhr_request <= 2:
                retries = retries + 1
                time.sleep(2)
                continue
            else:
                break
        await page
        # Loop through gathered requests and get response body
        logger.debug(f'receiveXHR Loop through gathered requests and get response body')
        for request in self.xhr_requests:
            try:
                logger.debug(f"Fetching response body for request ID: {request[1]}")
                res = await page.send(mycdp.network.get_response_body(request[1]))
                logger.debug(f'receiveXHR res: {res}')
                if res is None:
                    logger.warning(f"No response body for request ID: {request[1]}")
                    continue
                responses.append({
                    "url": request[0],
                    "body": res[0],
                    "is_base64": res[1],
                })
            except Exception as e:
                logger.debug("Error getting response:", e)
        logger.debug(f'receiveXHR responses: {responses}')
        return responses

#
# xhr_requests = []
# last_xhr_request = None
#
# def listenXHR(page):
#     global xhr_requests
#     global last_xhr_request
#     xhr_requests = []
#     last_xhr_request = None
#
#     async def handler(evt):
#         # Get AJAX requests
#         if evt.type_ in [mycdp.network.ResourceType.XHR, mycdp.network.ResourceType.FETCH, mycdp.network.ResourceType.PREFETCH]:
#             logger.debug(f"XHR request received: {evt} - {evt.response.url}")
#             xhr_requests.append([evt.response.url, evt.request_id])
#             global last_xhr_request
#             last_xhr_request = time.time()
#     page.add_handler(mycdp.network.ResponseReceived, handler)
#     logger.debug(f"Listening XHR on page: {page}")
#
# @logger.catch
# async def receiveXHR(page, requests):
#     logger.debug(f'receiveXHR: {requests}')
#     logger.debug(f"Receiving XHR on page: {page}")
#     responses = []
#     retries = 0
#     max_retries = 3
#     # Wait at least 2 seconds after last XHR request for more
#     while True:
#         if last_xhr_request is None or retries > max_retries:
#             break
#         if time.time() - last_xhr_request <= 2:
#             retries = retries + 1
#             time.sleep(2)
#             continue
#         else:
#             break
#     await page
#     # Loop through gathered requests and get response body
#     logger.debug(f'receiveXHR Loop through gathered requests and get response body')
#     for request in requests:
#         try:
#             logger.debug(f"Fetching response body for request ID: {request[1]}")
#             res = await page.send(mycdp.network.get_response_body(request[1]))
#             logger.debug(f'receiveXHR res: {res}')
#             if res is None:
#                 logger.warning(f"No response body for request ID: {request[1]}")
#                 continue
#             responses.append({
#                 "url": request[0],
#                 "body": res[0],
#                 "is_base64": res[1],
#             })
#         except Exception as e:
#             logger.debug("Error getting response:", e)
#     logger.debug(f'receiveXHR responses: {responses}')
#     return responses