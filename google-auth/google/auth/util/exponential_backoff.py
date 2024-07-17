# Copyright 2022 Google LLC
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

import random
import time


"""Exponential Backoff Utility"""



class ExponentialBackoff:
	"""An exponential backoff iterator. This can be used in a for loop to perform requests with exponential backoff."""

	# The default amount of retry attempts
	DEFAULT_RETRY_TOTAL_ATTEMPTS = 3

	# The default initial backoff period (1.0 second).
	DEFAULT_INITIAL_INTERVAL_SECONDS: float = 1.0

	# The default randomization factor (0.1 which results in a random period ranging between 10% below and 10% above the retry interval).
	DEFAULT_RANDOMIZATION_FACTOR: float = 0.1

	# The default multiplier value (2 which is 100% increase per back off).
	DEFAULT_MULTIPLIER: float = 2.0

	_total_attempts: int
	_initial_wait_seconds: float
	_current_wait_seconds: float
	_randomization_factor: float
	_multiplier: float
	_backoff_count: int


	def __init__ (self, total_attempts: int | None = None, initial_wait_seconds: int | None = None, randomization_factor: float | None = None, multiplier: float | None = None) -> None:
		if total_attempts is None:
			total_attempts = self.DEFAULT_RETRY_TOTAL_ATTEMPTS

		self._total_attempts = total_attempts
		if initial_wait_seconds is None:
			initial_wait_seconds = self.DEFAULT_INITIAL_INTERVAL_SECONDS

		self._current_wait_seconds = self._initial_wait_seconds = float(initial_wait_seconds)
		if randomization_factor is None:
			randomization_factor = self.DEFAULT_RANDOMIZATION_FACTOR

		self._randomization_factor = randomization_factor
		if multiplier is None:
			multiplier = self.DEFAULT_MULTIPLIER

		self._multiplier = multiplier
		self._backoff_count = 0


	def __iter__ (self) -> 'ExponentialBackoff':

		self._backoff_count = 0
		self._current_wait_seconds = self._initial_wait_seconds

		return self


	def __next__ (self) -> int:

		if self._backoff_count >= self._total_attempts:
			raise StopIteration

		self._backoff_count += 1

		jitter_variance: float = self._current_wait_seconds * self._randomization_factor
		jitter: float = random.uniform(self._current_wait_seconds - jitter_variance, self._current_wait_seconds + jitter_variance)

		# Wait a bit
		time.sleep(jitter)

		self._current_wait_seconds *= self._multiplier

		return self._backoff_count


	@property
	def total_attempts (self) -> int:
		"""The total number of backoff attempts that can be made."""

		return self._total_attempts


	@property
	def backoff_count (self) -> int:
		"""The current number of backoff attempts that have been made."""

		return self._backoff_count
