# Copyright 2016 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Interfaces for credentials."""

from datetime import datetime, timedelta, timezone

from google.oauth2.client import jwt_grant

from google.auth.transport.base import BaseRequest
from google.auth.crypt.base import BaseSigner



class BaseCredentials:
	REFRESH_THRESHOLD: timedelta = timedelta(minutes = 3, seconds = 45)

	token: str | None
	expiry: datetime | None

	_token_uri: str | None

	_scopes: list[str]
	_default_scopes: list[str]

	_signer: BaseSigner



	class TokenState:
		FRESH = 1
		STALE = 2
		INVALID = 3



	def __init__ (self, *, token: str | None = None, expiry: datetime | None = None, token_uri: str | None = None, scopes: list[str] | None = None, default_scopes: list[str] | None = None, signer: BaseSigner):
		self.token = token
		self.expiry = expiry

		self._token_uri = token_uri

		if scopes is None:
			scopes = []
		self._scopes = scopes

		if default_scopes is None:
			default_scopes = []
		self._default_scopes = default_scopes

		self._signer = signer


	@property
	def valid (self) -> bool:
		return self.token_state in (self.TokenState.FRESH, self.TokenState.STALE)


	@property
	def token_state (self) -> int:
		if self.token is None:
			return self.TokenState.INVALID

		# Credentials that can't expire are always treated as fresh.
		if self.expiry is None:
			return self.TokenState.FRESH

		now = datetime.now(timezone.utc)

		if now >= self.expiry:
			return self.TokenState.INVALID

		is_stale = now >= (self.expiry - self.REFRESH_THRESHOLD)
		if is_stale:
			return self.TokenState.STALE

		return self.TokenState.FRESH


	def _make_authorization_grant_assertion (self):
		raise NotImplementedError("_make_authorization_grant_assertion must be implemented")


	def refresh (self, request: BaseRequest):

		assertion = self._make_authorization_grant_assertion()
		self.token, self.expiry, _ = jwt_grant(request, self._token_uri, assertion)


	def apply (self, headers: dict[str, str], token: list[str] | None = None) -> None:
		headers['authorization'] = f"Bearer {token or self.token}"


	@property
	def scopes (self) -> list[str]:
		return self._scopes


	@property
	def default_scopes (self) -> list[str]:
		return self._default_scopes


	@property
	def requires_scopes (self) -> bool:
		"""True if these credentials require scopes to obtain an access token."""

		return False


	def has_scopes (self, scopes: list[str] | set[str] | tuple[str]) -> bool:
		"""Checks if the credentials have the given scopes."""

		return set(scopes).issubset(set(self._scopes) & set(self._default_scopes))


	def sign_bytes (self, message):
		raise NotImplementedError("Sign bytes must be implemented.")


	@property
	def signer_email (self):
		raise NotImplementedError("Signer email must be implemented.")


	@property
	def signer (self):
		raise NotImplementedError("Signer must be implemented.")
