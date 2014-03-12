#!/usr/bin/env python
#
# Copyright 2013 Hannes Juutilainen
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

import re
import urllib2

from autopkglib import Processor, ProcessorError


__all__ = ["VagrantURLProvider"]


MAIN_DOWNLOAD_URL = "http://www.vagrantup.com/downloads.html"

re_dmg_url = re.compile(r'<a href=[\'\"](?P<dmg_url>https://dl.bintray.com/mitchellh/vagrant/Vagrant[-_][0-9\.]+\.dmg)[\'\"]>', re.IGNORECASE)

class VagrantURLProvider(Processor):
    """Provides a download URL for the latest Vagrant"""
    input_variables = {
        "base_url": {
            "required": False,
            "description": "The Vagrant download site",
        },
    }
    output_variables = {
        "url": {
            "description": "URL to the latest Vagrant release.",
        },
    }
    description = __doc__
    
    def parse_download_url(self, base_url):
        """Returns the URL"""
        try:
            f = urllib2.urlopen(base_url)
            html = f.read()
            f.close()
        except BaseException as e:
            raise ProcessorError("Can't download %s: %s" % (base_url, e))

        m = re_dmg_url.search(html)

        if not m:
            raise ProcessorError(
                "Couldn't find dmg link in %s" % base_url)
        
        dmg_url = m.group("dmg_url")
        self.output("Found dmg link: %s" % dmg_url)
        return dmg_url
    
    
    def get_vagrant_dmg_url(self, base_url):
        """Find and return a download URL"""
        
        # Parse the download page to get a dmg link
        dmg_url = self.parse_download_url(base_url)
        
        return dmg_url
    
    
    def main(self):
        base_url = self.env.get("base_url", MAIN_DOWNLOAD_URL)
        self.env["url"] = self.get_vagrant_dmg_url(base_url)
        self.output("Found URL %s" % self.env["url"])


if __name__ == "__main__":
    processor = VagrantURLProvider()
    processor.execute_shell()
