import mimetypes
import os

import aiohttp

from sightengine.video_models import VideoSyncResponse

from .models import CheckRequest, CheckResponse, VideoAsyncResponse

BASE_URL = "https://api.sightengine.com/1.0/"


class SightEngineClient:
    def __init__(self, api_user: int, api_secret: str):
        self.api_user = api_user
        self.api_secret = api_secret

    def _get_default_check_params(self, check_request: CheckRequest) -> dict:
        """Prepare parameters for the check request"""
        return {
            "api_user": self.api_user,
            "api_secret": self.api_secret,
            "models": ",".join(check_request.models),
        }

    def _get_default_headers(self, is_multipart: bool = False) -> dict:
        """Default headers for the API requests"""
        headers = {
            "accept": "application/json",
            "User-Agent": "sightengine-python-async/1.0",  # TODO update version
        }
        if not is_multipart:
            headers["Content-Type"] = "application/json"
        return headers

    async def _request(
        self,
        method: str,
        endpoint: str,
        params: dict = None,
        data: dict = None,
        files: dict = None,
        headers: dict = None,
    ):
        """Builds and sends an HTTP request to the SightEngine API"""
        is_multipart = files is not None
        headers = headers or self._get_default_headers(is_multipart=is_multipart)
        url = f"{BASE_URL}{endpoint}"

        async with aiohttp.ClientSession() as session:
            request_kwargs = {"headers": headers}
            if params:
                request_kwargs["params"] = params

            if files:
                form = aiohttp.FormData()
                # add data fields to the form
                for k, v in (data or {}).items():
                    form.add_field(k, str(v))

                # check if the file is a string, if so assume it's a file path
                if isinstance(files["media"], str):
                    # add file fields to the form
                    for field, file_path in files.items():
                        filename = os.path.basename(file_path)
                        content_type, _ = mimetypes.guess_type(file_path)
                        with open(file_path, "rb") as f:
                            file_bytes = f.read()
                        form.add_field(
                            field,
                            file_bytes,
                            filename=filename,
                            content_type=content_type,
                        )
                else:  # binary data
                    for field, file_bytes in files.items():
                        content_type, _ = mimetypes.guess_type(field)
                        form.add_field(
                            field,
                            file_bytes,
                            content_type=content_type,
                        )
                request_kwargs["data"] = form
            elif data:
                request_kwargs["data"] = data

            async with session.request(method, url, **request_kwargs) as response:
                if response.status != 200:
                    raise Exception(
                        f"Error: {response.status} - {await response.text()}"
                    )
                r_json = await response.json()
                # for debugging, write response to a file
                """
                import json
                with open("response.json", "w") as f:
                    json.dump(r_json, f, indent=4)
                """
                return r_json

    async def check(self, request: CheckRequest) -> CheckResponse:
        endpoint = "check.json"
        base_params = self._get_default_check_params(request)
        base_params.update(request.params or {})
        files = None
        response_model = CheckResponse

        if request.url:
            params = {**base_params, "url": request.url}
            method = "GET"
            data = None
        elif request.file:
            files = {"media": request.file}
            method = "POST"
            data = base_params
            params = None
        elif request.file_bytes:
            files = {"media": request.file_bytes}
            method = "POST"
            data = base_params
            params = None
        elif request.video_file:
            endpoint = "video/check-sync.json"
            files = {"media": request.video_file}
            method = "POST"
            data = base_params
            response_model = VideoSyncResponse

            # this is an async video check
            if request.callback_url:
                endpoint = "video/check.json"
                data = {**data, "callback_url": request.callback_url}
                response_model = VideoAsyncResponse
        else:
            raise ValueError(
                "One of url, file, file_bytes, or video_file must be provided"
            )

        r_json = await self._request(
            method=method,
            endpoint=endpoint,
            params=params if method == "GET" else None,
            data=data if method == "POST" else None,
            files=files,
        )
        return response_model(**r_json)
