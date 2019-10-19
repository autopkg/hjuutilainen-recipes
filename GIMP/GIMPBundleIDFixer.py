#!/usr/bin/env python
#
# Heavily based upon 
# Copyright 2016 Hannes Juutilainen
#
# Copyright 2018 James Nairn
# 
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

__all__ = ["GIMPBundleIDFixer"]


class GIMPBundleIDFixer(Processor):
    """Tidies bundleid on given GIMP.app"""
    input_variables = {
        "bundleid": {
            "required": True,
            "description": "Bundle ID from GIMP.app",
        }
    }
    output_variables = { 
        "bundleid": {
            "description": "Tidied form of bundleid",
        }
    }
    description = __doc__
    
    def main(self):
        bundleid = self.env.get("bundleid")
        
        # Strip illegal chars from bundleid
        # Apple docs https://developer.apple.com/library/archive/documentation/CoreFoundation/Conceptual/CFBundles/BundleTypes/BundleTypes.html#//apple_ref/doc/uid/10000123i-CH101-SW1
        bundleid = bundleid.strip(':')

        self.output("bundleid: {}".format(bundleid))
        self.env["bundleid"] = bundleid




if __name__ == "__main__":
    processor = GIMPBundleIDFixer()
    processor.execute_shell()
