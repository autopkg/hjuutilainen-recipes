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

from autopkglib import Processor, ProcessorError

import subprocess
import os

__all__ = ["GIMPPermissionsFixer"]


class GIMPPermissionsFixer(Processor):
    """Fixes incorrect permissions on given GIMP.app"""
    input_variables = {
        "gimp_app_path": {
            "required": True,
            "description": "Path to GIMP.app",
        }
    }
    output_variables = {}
    description = __doc__
    
    def main(self):
        gimp_app_path = self.env.get("gimp_app_path")
        
        if os.path.exists(gimp_app_path):
            gimp_bin_path = os.path.join(gimp_app_path, "Contents/MacOS/GIMP")
            cmd = ["/bin/chmod", "+x", gimp_bin_path]
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output, error = p.communicate()
            if p.returncode != 0:
                raise ProcessorError("chmod failed with error: %s" % error)
            else:
                self.output("Added execute bits to %s" % gimp_bin_path)
        else:
            raise ProcessorError("File not found: %s" % gimp_app_path)


if __name__ == "__main__":
    processor = GIMPPermissionsFixer()
    processor.execute_shell()
