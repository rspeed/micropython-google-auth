# Copyright 2016 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#	   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Transport adapter for Requests."""

from requests import request, Response as RequestsResponse

from google.auth.exceptions import TransportError
from google.auth.transport.base import BaseResponse, BaseRequest



class Response(BaseResponse):
	_response: RequestsResponse

	def __init__ (self, response: RequestsResponse):
		self._response = response


	@property
	def status_code (self) -> int:
		return self._response.status_code


	@property
	def headers (self) -> dict:
		return self._response.headers


	@property
	def content (self) -> bytes:
		return self._response.content



class Request(BaseRequest):
	def __call__ (self, url: str, method: str = 'GET', body: str | bytes | None = None, headers: dict[str,str] | None = None, timeout: int | None = None, **kwargs) -> Response:
		if timeout is None:
			timeout = self._DEFAULT_TIMEOUT

		try:
			return Response(request(method, url, data = body, headers = headers, timeout = timeout, **kwargs))

		except ValueError as exc:
			raise TransportError(exc) from exc
