#!/usr/bin/env python
#
# Copyright 2016 Hannes Juutilainen
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import hashlib

from autopkglib import Processor, ProcessorError

__all__ = ["ChecksumVerifier"]

# Default options
DEFAULT_ALGORITHM = "SHA1"


class ChecksumVerifier(Processor):
    """Verifies the checksum of a given file"""
    input_variables = {
        "pathname": {
            "required": True,
            "description": "File path to verify.",
        },
        "checksum": {
            "required": True,
            "description": "The expected checksum.",
        },
        "algorithm": {
            "required": False,
            "description": "Algorithm to use. Supported values are "
                           "SHA1, SHA224, SHA256, SHA384, SHA512 or MD5. "
                           "If not defined, SHA1 is assumed.",
        },
    }
    output_variables = {
    }
    description = __doc__

    def calculate_checksum(self, file_path=None, hasher=None):
        """Calculates a checksum by reading input file in chunks
        http://stackoverflow.com/a/3431838

        :param file_path: The input file to hash
        :param hasher: Hash type to use
        """
        if not hasher or not file_path:
            return None
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hasher.update(chunk)
        return hasher.hexdigest()

    def main(self):
        # We absolutely need the input path and an expected checksum
        input_path = self.env.get("pathname", None)
        if not os.path.exists(input_path):
            raise ProcessorError("Error: File %s does not exist." % input_path)
        checksum = self.env.get("checksum", None)
        if not checksum or checksum == "":
            raise ProcessorError("Error: Expected checksum is empty.")

        # Calculate and verify the checksum
        algorithm = self.env.get("algorithm", DEFAULT_ALGORITHM)
        self.output("Calculating %s checksum for %s" % (algorithm, input_path))
        calculated_checksum = self.calculate_checksum(input_path, hashlib.new(algorithm))
        self.output("Calculated checksum: %s" % calculated_checksum)
        self.output("Expected checksum:   %s" % checksum)
        if calculated_checksum == checksum:
            self.output("Calculated checksum matches the expected checksum.")
        else:
            raise ProcessorError("Error: Calculated checksum does not match expected checksum")


if __name__ == "__main__":
    processor = ChecksumVerifier()
    processor.execute_shell()
