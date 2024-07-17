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

from json import dumps as dump_json_string

from google.auth.util.helpers import unpadded_urlsafe_b64encode
from google.auth.crypt.base import BaseSigner



def encode (signer: BaseSigner, payload: dict[str, str], header: dict[str, str] | None = None, key_id: str | None = None) -> bytes:
	"""Make a signed JWT."""

	print()

	if header is None:
		header = {}

	if key_id is None:
		key_id = signer.key_id

	header['typ'] = 'JWT'

	if 'alg' not in header:
		header['alg'] = 'RS256'

	if key_id is not None:
		header['kid'] = key_id

	segments: list[bytes] = [unpadded_urlsafe_b64encode(dump_json_string(seg).encode('utf-8')) for seg in (header, payload)]
	signature = unpadded_urlsafe_b64encode(signer.sign(b'.'.join(segments)))
	segments.append(signature)

	return b'.'.join(segments)
