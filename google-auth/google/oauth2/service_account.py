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

from copy import deepcopy
from datetime import datetime, timedelta
from io import open as open_file
from json import load as load_json

from google.auth.util.helpers import utcnow
from google.auth.exceptions import MalformedError
from google.auth.crypt.rsa import RSASigner
from google.auth.jwt import encode as encode_jwt

from google.auth.credentials.base import BaseCredentials
from google.auth.crypt.base import BaseSigner



class Credentials(BaseCredentials):
	"""Service account credentials"""

	GOOGLE_OAUTH2_TOKEN_ENDPOINT: str = 'https://oauth2.googleapis.com/token'
	DEFAULT_TOKEN_LIFETIME: timedelta = timedelta(hours = 1)
	DEFAULT_ADDITIONAL_CLAIMS: dict[str, str] = {}
	DEFAULT_TRUST_BOUNDARY: dict[str, list | str] = {'locations': [], 'encoded_locations': '0x0'}

	_service_account_email: str
	_subject: str | None
	_project_id: str | None
	_additional_claims: dict[str, str]
	_trust_boundary: dict[str, list | str]


	def __init__ (self, *, service_account_email: str, subject: str | None = None, project_id: str | None = None, additional_claims: dict[str, str] | None = None, trust_boundary: dict[str, list | str] | None = None, **kwargs):
		super().__init__(**kwargs)

		self._service_account_email = service_account_email
		self._subject = subject
		self._project_id = project_id

		if additional_claims is None:
			additional_claims = deepcopy(self.DEFAULT_ADDITIONAL_CLAIMS)
		self._additional_claims = additional_claims

		if trust_boundary is None:
			trust_boundary = self.DEFAULT_TRUST_BOUNDARY
		self._trust_boundary = trust_boundary


	@classmethod
	def from_service_account_info (cls, info: dict[str, str], **kwargs) -> 'Credentials':
		"""Creates a Credentials instance from parsed service account info."""

		if missing_fields := {'client_email', 'token_uri'}.difference(info.keys()):
			raise MalformedError(f"Service account info was not in the expected format, missing fields {", ".join(missing_fields)}.")

		params: dict[str, BaseSigner | str] = deepcopy(kwargs)
		params.update({'signer': RSASigner.from_service_account_info(info), 'service_account_email': info['client_email'], 'token_uri': info['token_uri'], 'project_id': info.get('project_id'), 'trust_boundary': info.get('trust_boundary')})

		return cls(**params)


	@classmethod
	def from_service_account_file (cls, filename: str, **kwargs) -> 'Credentials':
		"""Creates a Credentials instance from a service account JSON file."""

		with open_file(filename, 'r', encoding = 'utf-8') as json_file:
			info: dict['str', 'str'] = load_json(json_file)

		return cls.from_service_account_info(info = info, **kwargs)


	@property
	def service_account_email (self) -> str:
		"""The service account email."""

		return self._service_account_email


	@property
	def project_id (self) -> str:
		"""Project ID associated with this credential."""

		return self._project_id


	@property
	def requires_scopes (self) -> bool:
		"""Checks if the credentials requires scopes."""

		return not self._scopes


	def _make_authorization_grant_assertion (self) -> bytes:
		"""Creates an OAuth 2.0 assertion."""

		now: datetime = utcnow()
		expiry: datetime = now + self.DEFAULT_TOKEN_LIFETIME

		payload: dict = {
			'iat': int(now.timestamp()),
			'exp': int(expiry.timestamp()),  # The issuer must be the service account email.
			'iss': self._service_account_email,  # The audience must be the auth token endpoint's URI
			'aud': self.GOOGLE_OAUTH2_TOKEN_ENDPOINT,
			'scope': ' '.join(self._scopes)
		}

		payload.update(self._additional_claims)

		# The subject can be a user email for domain-wide delegation.
		if self._subject:
			payload.setdefault('sub', self._subject)

		return encode_jwt(self._signer, payload)


	@property
	def signer_email (self):
		return self._service_account_email


	@property
	def signer (self):
		return self._signer
