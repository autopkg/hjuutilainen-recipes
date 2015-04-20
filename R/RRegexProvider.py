#!/usr/bin/env python
#
# Copyright 2015 Hannes Juutilainen
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

from autopkglib import Processor, ProcessorError

__all__ = ["RRegexProvider"]

OS_RELEASE_DEFAULT = "mavericks"


class RRegexProvider(Processor):
    """Provides a regular expression for R download URL"""
    input_variables = {
        "os_release": {
            "required": False,
            "description": "Set to mavericks or snowleopard",
        }
    }
    output_variables = {
        "r_regex": {
            "description": "Regular expression to use in URLTextSearcher processor",
        },
    }
    description = __doc__
    
    def main(self):
        os_release = self.env.get("OS_RELEASE", OS_RELEASE_DEFAULT)
        
        if os_release == "mavericks":
            new_regex = r'(?P<r_filename>R-(?P<r_version>[0-9\.]+)\.pkg)'
            self.env["r_regex"] = new_regex
        
        elif os_release == "snowleopard":
            new_regex = r'(?P<r_filename>R-(?P<r_version>[0-9\.]+)-snowleopard\.pkg)'
            self.env["r_regex"] = new_regex
        
        else:
            raise ProcessorError("Unsupported value for OS_RELEASE: %s" % os_release)


if __name__ == "__main__":
    processor = RRegexProvider()
    processor.execute_shell()
