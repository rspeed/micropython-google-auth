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

"""Base classes for cryptographic signers and verifiers."""



class BaseSigner:
	"""Abstract base class for cryptographic signers."""


	@property
	def key_id (self):
		"""The key ID."""

		raise NotImplementedError("Key id must be implemented")


	def sign (self, message: str | bytes) -> bytes:
		"""Signs a message."""

		raise NotImplementedError("Sign must be implemented")
