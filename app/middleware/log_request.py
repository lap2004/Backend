from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from loguru import logger
import time


class LogRequestMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        logger.info(f"\[{request.method}] {request.url.path} from {request.client.host}")

        response: Response = await call_next(request)

        process_time = (time.time() - start_time) * 1000
        logger.info(f"Response {response.status_code} in {process_time:.2f}ms")

        return response
