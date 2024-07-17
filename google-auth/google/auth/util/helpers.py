# Copyright 2015 Google Inc.
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

"""Helper functions for commonly used utilities."""

from datetime import datetime, timezone
from base64 import b64encode, b64decode



def utcnow () -> datetime:
	"""Returns the current UTC datetime."""

	return datetime.now(timezone.utc)



def to_bytes (value: bytes | str, encoding: str = 'utf-8') -> bytes:
	"""Converts str to bytes, if necessary."""

	try:
		return value.encode(encoding)

	except AttributeError:
		return value



def from_bytes (value: str | bytes, encoding: str = 'utf-8') -> str:
	"""Converts bytes to str, if necessary."""

	try:
		return value.decode(encoding)

	except AttributeError:
		return value



def _b64_translate (input_bytes, trans_table):
	"""Re-implement bytes.translate() as there is no such function in micropython"""
	result = bytearray()

	for byte in input_bytes:
		translated_byte = trans_table.get(byte, byte)
		result.append(translated_byte)

	return bytes(result)



def _b64_maketrans (f, t):
	"""Re-implement bytes.maketrans() as there is no such function in micropython"""
	if len(f) != len(t):
		raise ValueError("maketrans arguments must have same length")
	translation_table = dict(zip(f, t))
	return translation_table



def _b64_bytes_from_decode_data (s):
	if isinstance(s, str):
		try:
			return s.encode("ascii")
		except UnicodeEncodeError:
			raise ValueError("string argument should contain only ASCII characters")
	elif isinstance(s, (bytes, bytearray)):
		return s
	else:
		raise TypeError("argument should be bytes or ASCII string, not %s" % s.__class__.__name__)



_urlsafe_encode_translation = _b64_maketrans(b'+/', b'-_')
_urlsafe_decode_translation = _b64_maketrans(b'-_', b'+/')



def unpadded_urlsafe_b64encode (value: bytes | str) -> bytes | str:
	"""Encodes base64 strings removing any padding characters."""

	return _b64_translate(b64encode(value), _urlsafe_encode_translation).rstrip(b'=')



def padded_urlsafe_b64decode (value: str | bytes) -> bytes:
	"""Decodes base64 strings lacking padding characters."""

	value: bytes = to_bytes(value)
	value = value + b'=' * (-len(value) % 4)
	return b64decode(_b64_translate(_b64_bytes_from_decode_data(value), _urlsafe_decode_translation))
