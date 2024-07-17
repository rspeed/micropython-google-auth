# Copyright 2016 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from json import loads as load_json_string, dumps as dump_json_string
from urllib.parse import urlencode
from datetime import datetime, timedelta

from google.auth.util.exponential_backoff import ExponentialBackoff
from google.auth.util.helpers import utcnow
from google.auth.exceptions import RefreshError, MalformedError
from google.auth.transport import DEFAULT_RETRYABLE_STATUS_CODES
from google.auth.util.helpers import from_bytes
from google.auth import metrics

from google.auth.transport.base import BaseRequest, BaseResponse


JSON_CONTENT_TYPE: str = 'application/json'
URLENCODED_CONTENT_TYPE: str = 'application/x-www-form-urlencoded'
JWT_GRANT_TYPE: str = 'urn:ietf:params:oauth:grant-type:jwt-bearer'



def _handle_error_response (response_data: str | dict[str, str], retryable_error: bool) -> None:
	if isinstance(response_data, str):
		raise RefreshError(response_data, retryable = retryable_error)

	try:
		error_details = f"{response_data['error']}: {response_data['error_description']}"

	# If no details could be extracted, use the response data.
	except (KeyError, ValueError):
		error_details = dump_json_string(response_data)

	raise RefreshError(error_details, response_data, retryable = retryable_error)



def _can_retry (status_code: int, response_data: str | dict[str, str]) -> bool:
	if status_code in DEFAULT_RETRYABLE_STATUS_CODES:
		return True

	try:
		error_desc = response_data.get('error_description', '')
		error_code = response_data.get('error', '')

		# Per Oauth 2.0 RFC https://www.rfc-editor.org/rfc/rfc6749.html#section-4.1.2.1
		# This is needed because a redirect will not return a 500 status code.
		if any(e in {'internal_failure', 'server_error', 'temporarily_unavailable'} for e in (error_code, error_desc)):
			return True

	except AttributeError:
		# If the response isn't structured data (such as JSON) no further analysis is possible.
		pass

	return False



def _token_endpoint_request (request: BaseRequest, token_uri: str, body: dict[str, str | bytes], access_token: str | None = None, use_json: bool = False, can_retry: bool = True, headers: dict[str, str] = None, **kwargs) -> dict[str, str]:
	request_headers: dict[str, str] = {}
	request_body: bytes = b''

	if use_json:
		request_headers['Content-Type'] = JSON_CONTENT_TYPE
		request_body = dump_json_string(body).encode('utf-8')

	else:
		request_headers['Content-Type'] = URLENCODED_CONTENT_TYPE
		request_body = urlencode(body).encode('utf-8')

	if access_token:
		request_headers['Authorization'] = f'Bearer {access_token}'

	if headers:
		request_headers.update(headers)


	def _perform_request () -> tuple[bool, str | bytes | dict, bool | None]:
		response: BaseResponse = request(method = 'POST', url = token_uri, headers = request_headers, body = request_body, **kwargs)

		# Convert bytes to str
		response_body: str | dict[str, str] = from_bytes(response.content)

		try:
			# The response should be JSON
			response_body = load_json_string(response_body)

		except ValueError:
			# No problem, keep it as a string
			pass

		if response.status_code == 200:
			return True, response_body, None

		return False, response_body, _can_retry(status_code = response.status_code, response_data = response_body)


	request_succeeded: bool
	response_data: dict[str, str] | str
	retryable_error: bool | None

	# Attempt the request
	request_succeeded, response_data, retryable_error = _perform_request()

	if request_succeeded:
		return response_data

	# Fail fast
	if not can_retry or not retryable_error:
		_handle_error_response(response_data, retryable_error)
		return response_data

	# Keep trying
	retries = ExponentialBackoff()
	for _ in retries:
		request_succeeded, response_data, retryable_error = _perform_request()

		if request_succeeded:
			return response_data

		if not retryable_error:
			_handle_error_response(response_data, retryable_error)
			return response_data

	_handle_error_response(response_data, retryable_error)
	return response_data



def jwt_grant (request: BaseRequest, token_uri: str, assertion: bytes, can_retry: bool = True) -> tuple[str, datetime, dict[str, str]]:
	body: dict[str, str | bytes] = {'assertion': assertion, 'grant_type': JWT_GRANT_TYPE}

	headers: dict[str, str] = {metrics.API_CLIENT_HEADER: metrics.token_request_access_token_sa_assertion()}

	response_data: dict[str, str] = _token_endpoint_request(request, token_uri, body, can_retry = can_retry, headers = headers)

	try:
		access_token = response_data['access_token']

	except KeyError as caught_exc:
		raise RefreshError("No access token in response.", response_data, retryable = False) from caught_exc

	expiry: datetime | None = None

	try:
		# Some services do not respect the OAUTH2.0 RFC and send expires_in as a JSON String.
		expires_in = int(response_data['expires_in'])
		expiry = utcnow() + timedelta(seconds = expires_in)

	except ValueError as exc:
		raise MalformedError("Invalid format for `expires_in` response.") from exc

	except KeyError:
		# Expiration wasn't specified
		pass

	return access_token, expiry, response_data
