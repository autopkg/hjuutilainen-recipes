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

__all__ = ["BlenderPermissionsFixer"]


class BlenderPermissionsFixer(Processor):
    """Fixes incorrect permissions on Blender by running chmod -R u+w"""
    input_variables = {
        "downloaded_blender_path": {
            "required": True,
            "description": "Path to downloaded and unarchived Blender folder",
        }
    }
    output_variables = {}
    description = __doc__
    
    def main(self):
        downloaded_blender_path = self.env.get("downloaded_blender_path")
        
        if os.path.exists(downloaded_blender_path):
            cmd = ["/bin/chmod", "-R", "u+w", downloaded_blender_path]
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output, error = p.communicate()
            if p.returncode != 0:
                raise ProcessorError("chmod failed with error: %s" % error)
            else:
                self.output("Added write bits recursively to %s" % downloaded_blender_path)
        else:
            self.output("Skipped: File not found: %s" % downloaded_blender_path)


if __name__ == "__main__":
    processor = BlenderPermissionsFixer()
    processor.execute_shell()
