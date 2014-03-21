#!/usr/bin/env python
#
# Copyright 2014 Hannes Juutilainen
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
import subprocess
from autopkglib import Processor, ProcessorError


__all__ = ["CurlCompiler"]

CURL_INSTALL_PATH = "/usr/local/curl-custom"

class CurlCompiler(Processor):
    description = "Compiles curl."
    input_variables = {
        "curl_source_path": {
            "required": True,
            "description": "Path to the downloaded curl source code.",
        },
        "curl_install_path": {
            "required": False,
            "description": "The path where curl should be installed. Default is '/usr/local/curl-custom'",
        },
    }
    output_variables = {
        
    }
    
    __doc__ = description
    
    def compile_curl_source_at_path(self, source_path, install_path):
        """
        Compiles curl sources at 'source_path' and installs to 'install_path'
        """
        
        # Change the working directory
        os.chdir(source_path)
        
        # Create the needed environment variables
        current_env = os.environ.copy()
        current_env["DYLD_LIBRARY_PATH"] = "/usr/lib"
        current_env["LDFLAGS"] = "-L/usr/lib"
        current_env["CPPFLAGS"] = "-I/usr/include"
        
        # ===============================================================
        #  Step 1. Run "./configure --prefix=<install_path>"
        # ===============================================================
        self.output("Configuring...")
        #process = ["./configure", "--prefix=%s" % install_path, "--without-libidn", "--disable-ldap", "--disable-ldaps", "--disable-manual"]
        process = ["./configure", "--prefix=%s" % install_path]
        p = subprocess.Popen(process, bufsize=1, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=current_env)
        (results, err) = p.communicate()
        if p.returncode != 0:
            raise ProcessorError("Failed with error: %s" % (err))
        
        # ===============================================================
        #  Step 2. Run "make"
        # ===============================================================
        self.output("Running make...")
        p = subprocess.Popen(["make"], bufsize=1, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=current_env)
        (results, err) = p.communicate()
        if p.returncode != 0:
            raise ProcessorError("Failed with error: %s" % (err))
        
        # ===============================================================
        #  Step 3. Run "make install DESTDIR=<pkgroot_dir>"
        # ===============================================================
        self.output("Running make install...")
        process = ["make", "install", "DESTDIR=%s" % self.env["pkgroot"]]
        p = subprocess.Popen(process, bufsize=1, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=current_env)
        (results, err) = p.communicate()
        if p.returncode != 0:
            raise ProcessorError("Failed with error: %s" % (err))
        
        pass
    
    def main(self):
        curl_source_path = self.env["curl_source_path"]
        curl_install_path = self.env.get("curl_install_path", CURL_INSTALL_PATH)
        self.compile_curl_source_at_path(curl_source_path, curl_install_path)
    

if __name__ == '__main__':
    processor = PraatVersionFixer()
    processor.execute_shell()
    
