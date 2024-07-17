__all__ = 'urlencode'

# noinspection SpellCheckingInspection
_ALWAYS_SAFE: bytes = (
	b'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
	b'abcdefghijklmnopqrstuvwxyz'
	b'0123456789'
	b'_.-'
)



def _encode_bytes (string: bytes, safe: bytes) -> str:
	for char in string:
		if char in safe:
			yield chr(char)
		else:
			yield f'%{char:02X}'



def _quote (string: str | bytes, safe: str = '', encoding: str = 'utf-8') -> str:
	if isinstance(string, str):
		string: bytes = string.encode(encoding)

	if isinstance(safe, str):
		safe += ' '
		# Normalize 'safe' by converting to bytes and removing non-ASCII chars
		safe: bytes = safe.encode('ascii', 'ignore')
	else:
		safe += b' '
		safe: bytes = bytes([c for c in safe if c < 128])
	safe += _ALWAYS_SAFE

	return (''.join(_encode_bytes(string, safe))).replace(' ', '+')



def urlencode (query: dict[str | bytes, str | bytes], safe: str | bytes = '', encoding: str = 'utf-8') -> str:
	queries: list = []

	for k, v in query.items():
		if isinstance(k, bytes):
			k = _quote(k, safe)
		else:
			k = _quote(str(k), safe, encoding)

		if isinstance(v, bytes):
			v = _quote(v, safe)
		else:
			v = _quote(str(v), safe, encoding)

		queries.append(f'{k}={v}')

	return '&'.join(queries)
