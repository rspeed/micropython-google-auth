# Copyright 2023 Google LLC
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

""" We use x-goog-api-client header to report metrics. This module provides the constants and helper methods to construct x-goog-api-client header."""

from sys import version_info
from google.auth import __version__


API_CLIENT_HEADER = 'x-goog-api-client'

# Auth request type
REQUEST_TYPE_ACCESS_TOKEN = 'auth-request-type/at'

# Credential type
CRED_TYPE_SA_ASSERTION = 'cred-type/sa'
PYTHON_AND_AUTH_LIB_VERSION = f'gl-upython/{'.'.join(map(str, version_info))} auth/{__version__}'



# Token request metric header values

# x-goog-api-client header value for service account credentials access token request (assertion flow).
# Example: "gl-python/3.7 auth/1.1 auth-request-type/at cred-type/sa"
def token_request_access_token_sa_assertion () -> str:
	return f'{PYTHON_AND_AUTH_LIB_VERSION} {REQUEST_TYPE_ACCESS_TOKEN} {CRED_TYPE_SA_ASSERTION}'
