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

from rsa import pkcs1
from rsa.key import PrivateKey

from google.auth.crypt.base import BaseSigner as BaseSigner
from google.auth.exceptions import MalformedError



class RSASigner(BaseSigner):
	PRIVATE_KEY_COMPONENTS: set = {'n', 'e', 'd', 'p', 'q'}

	SERVICE_ACCOUNT_INFO_PRIVATE_KEY: str = 'private_key_components'
	SERVICE_ACCOUNT_INFO_PRIVATE_KEY_ID: str = 'private_key_id'

	_key: PrivateKey
	_key_id: str


	def __init__ (self, private_key: dict[str, int], key_id: str):
		self._key = PrivateKey(**{i: private_key[i] for i in self.PRIVATE_KEY_COMPONENTS})
		self._key_id = key_id


	@property
	def key_id (self) -> str:
		return self._key_id


	def sign (self, message: bytes) -> bytes:
		return pkcs1.sign(message, self._key, 'SHA-256')


	@classmethod
	def from_service_account_info (cls, info: dict[str, str | dict[str, int]]) -> 'RSASigner':
		"""Creates a ``RSASigner`` instance from parsed service account info."""

		if missing_fields := {cls.SERVICE_ACCOUNT_INFO_PRIVATE_KEY, cls.SERVICE_ACCOUNT_INFO_PRIVATE_KEY_ID}.difference(info.keys()):
			raise MalformedError(f"Service account info was not in the expected format, missing fields {", ".join(missing_fields)}.")

		return cls(info[cls.SERVICE_ACCOUNT_INFO_PRIVATE_KEY], info.get(cls.SERVICE_ACCOUNT_INFO_PRIVATE_KEY_ID))
