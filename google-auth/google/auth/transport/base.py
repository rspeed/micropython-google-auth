# Copyright 2016 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


class BaseResponse:
	@property
	def status_code (self):
		raise NotImplementedError("status must be implemented.")


	@property
	def headers (self):
		raise NotImplementedError("headers must be implemented.")


	@property
	def content (self):
		raise NotImplementedError("data must be implemented.")



class BaseRequest:
	_DEFAULT_TIMEOUT: int = 120


	def __call__ (self, url: str, method: str = 'GET', body: str | bytes = None, headers: dict[str, str] | None = None, timeout: int | None = None, **kwargs) -> BaseResponse:
		raise NotImplementedError("__call__ must be implemented.")
