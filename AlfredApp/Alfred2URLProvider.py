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

import urllib2
import plistlib

from autopkglib import Processor, ProcessorError


__all__ = ["Alfred2URLProvider"]

# Found in "Alfred 2.app/Contents/Frameworks/Alfred Framework.framework/Versions/A/Alfred Framework"
UPDATE_INFO_PLIST_URL = "https://cachefly.alfredapp.com/updater/info.plist"

class Alfred2URLProvider(Processor):
    """Provides a download URL for the latest Alfred"""
    input_variables = {
        "base_url": {
            "required": False,
            "description": "The Alfred update info property list URL",
        },
    }
    output_variables = {
        "url": {
            "description": "URL to the latest Alfred release.",
        },
    }
    description = __doc__
    
    def download_info_plist(self, base_url):
        """Downloads the info.plist file and returns a plist object"""
        try:
            f = urllib2.urlopen(base_url)
            plist_data = f.read()
            f.close()
        except BaseException as e:
            raise ProcessorError("Can't download %s: %s" % (base_url, e))
        
        info_plist = plistlib.readPlistFromString(plist_data)
        
        return info_plist
    
    
    def get_alfred_dmg_url(self, base_url):
        """Find and return a download URL"""
        
        # Alfred 2 update check uses a standard plist file.
        # Grab it and parse...
        info_plist = self.download_info_plist(base_url)
        version = info_plist.get('version', None)
        self.output("Found version %s" % version)
        location = info_plist.get('location', None)
        
        return location
    
    
    def main(self):
        base_url = self.env.get("base_url", UPDATE_INFO_PLIST_URL)
        self.env["url"] = self.get_alfred_dmg_url(base_url)
        self.output("Found URL %s" % self.env["url"])


if __name__ == "__main__":
    processor = Alfred2URLProvider()
    processor.execute_shell()
