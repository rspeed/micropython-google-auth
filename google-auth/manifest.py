metadata(description = "Google-Auth for Micropython", version = "2.30.0", author = "Google LLC and Rob Speed", license = "Apache 2.0")

# Dependencies
require('base64')
require('copy')
require('datetime')
require('requests')

# Annoyingly not require-able
package('rsa', base_path = '../lib/micropython-rsa-signing')

package('google')
