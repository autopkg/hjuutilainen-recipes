#!/usr/bin/env python
#
# Copyright 2013 Timothy Sutton
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

# Borrowed code and concepts from Unzipper and Copier processors.

# chris.gerke@gmail.com
# Borrowed code and concepts from FlatPkgUnpacker.py in the AutoPKG core. Credits above ^
# see comments throughout, there is a some todo items
# figure out how to make this a shared processor

import os.path
import subprocess
import shutil

from glob import glob
from autopkglib import Processor, ProcessorError

__all__ = ["cmmacCreator"]

class cmmacCreator(Processor):
    description = ("Compresses an app, dmg or pkg using CMAppUtil. ")
    input_variables = {
        "source_file": {
            "required": True,
            "description": ("Path to an app, dmg or pkg. "),
        },
        "destination_directory": {
            "required": True,
            "description": ("Directory where the cmmac will be created "),
        },
    }
    output_variables = {
    }

    __doc__ = description
    source_path = None

    def cmmacConvert(self):
        # CMAppUtil is required http://www.microsoft.com/en-us/download/details.aspx?id=36212
        # THINGS TO DO :
        # need to detect the source_file type and append -a option to cmmacmd if the file is a dmg
        # think about extracting the cmmac via tar -xvf then altering the detection.xml for version info if req
        if os.path.exists('/usr/local/bin/CMAppUtil'):
            try:
                self.output("Found binary %s" % '/usr/local/bin/CMAppUtil')
            except OSError as e:
                raise ProcessorError(
                    "Can't find binary %s: %s" % ('/usr/local/bin/CMAppUtil', e.strerror))
        try:
            cmmaccmd = ["/usr/local/bin/CMAppUtil",
                      "-s",
                      "-v",
                      "-c", self.env['source_file'],
                      "-o", self.env['destination_directory']]
            p = subprocess.Popen(cmmaccmd,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)
            (out, err) = p.communicate()
        except OSError as e:
            raise ProcessorError("cmmac execution failed with error code %d: %s"
                % (e.errno, e.strerror))
        if p.returncode != 0:
            raise ProcessorError("cmmac conversion of %s failed: %s"
                % (self.env['source_file'], err))

    def main(self):
        if os.path.exists(self.env['source_file']):
            try:
                self.output("Found %s" % self.env['source_file'])
            except OSError as e:
                raise ProcessorError(
                    "Can't find %s" % (self.env['source_file'], e.strerror))

        # probably don't need this because most people will use the RECIPE_CACHE_DIR
        # which should be the parent directory for the source_file, check above should catch this
        if os.path.exists(self.env['destination_directory']):
            try:
                self.output("Found %s" % self.env['destination_directory'])
            except OSError as e:
                raise ProcessorError(
                    "Can't find %s" % (self.env['destination_directory'], e.strerror))

        # overwrite cmmac? or simply raise exception?
        # cmmac files can be extracted using tar -xvf, the resources contain a metadata file and the PKG/APP
        # its possible with some more code to check and compare the versions of those items and make a decision
        # thinking about this after I get a little better with python
        # figure out how to append to "Nothing downloaded, packaged or imported." so it reads...
        # Nothing downloaded, packaged, converted or imported.
        sourcefilebase = os.path.basename(self.env['source_file'])
        cmmac = (self.env['destination_directory'] + "/" + sourcefilebase + ".cmmac")

        if os.path.exists(cmmac):
              self.output("Found an existing cmmac %s exiting..." % cmmac)
        else:
              self.output("Didn't find an existing cmmac %s" % cmmac)
              self.cmmacConvert()

if __name__ == '__main__':
    processor = cmmacCreator()
    processor.execute_shell()
