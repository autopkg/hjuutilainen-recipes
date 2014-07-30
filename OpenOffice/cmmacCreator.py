#!/usr/bin/env python
#
# Copyright 2014 Chris Gerke
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
import shutil
import subprocess

from autopkglib import Processor, ProcessorError

__all__ = ["cmmacCreator"]

class cmmacCreator(Processor):
    '''Create an SCCM cmmac file using a pkg.'''

    description = __doc__

    input_variables = {
        'source_pkg': {
            'description': 'Path to a package',
            'required': True,
        },
        'destination_folder': {
            'description': 'Path to the cmmac file to be created',
            'required': True,
        },
    }

    output_variables = {}

    def compress(self, source_file, dest_path):
        try:
            subprocess.check_call(['CMAppUtil','-s','-v','-c', source_file, '-o', dest_path])
        except subprocess.CalledProcessError, err:
            raise ProcessorError("%s compressing %s" % (err, source_file))

    def main(self):
        source_file = self.env.get('source_pkg')
        dest_path = self.env.get('destination_folder')

        self.compress(source_file, dest_path)

        self.output("Compressed for SCCM %s to %s"
            % (source_file, dest_path))

if __name__ == '__main__':
    processor = cmmacCreator()
    processor.execute_shell()
