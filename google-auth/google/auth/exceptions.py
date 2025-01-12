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

class GoogleAuthError(Exception):
	_retryable: bool = False


	def __init__ (self, *args, **kwargs):
		super().__init__(*args)
		retryable = kwargs.get("retryable", False)
		self._retryable = retryable


	@property
	def retryable (self):
		return self._retryable



class TransportError(GoogleAuthError):
	"""Used to indicate an error occurred during an HTTP request."""



class RefreshError(GoogleAuthError):
	"""Used to indicate that refreshing the credentials' access token failed."""



class DefaultCredentialsError(GoogleAuthError):
	"""Used to indicate that acquiring default credentials failed."""



class MalformedError(DefaultCredentialsError):
	"""An exception for malformed data."""
