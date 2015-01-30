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
import xml.etree.ElementTree as ET

from autopkglib import Processor, ProcessorError


__all__ = ["LibreOfficeURLProvider"]


LANGUAGE_CODE = "en-US"
TYPE = "mac-x86_64"
MAIN_DOWNLOAD_URL = "http://www.libreoffice.org/download/libreoffice-fresh/"

re_mirrorlist = re.compile(r'<a href=[\'\"](?P<mirrorlist_url>\S*\.dmg\.mirrorlist)[\'\"].*</a>', re.IGNORECASE)
re_metalink = re.compile(r'<a href="(?P<meta4_url>.*\.dmg\.meta4)".*</a>', re.IGNORECASE)


class LibreOfficeURLProvider(Processor):
    """Provides a download URL for the latest LibreOffice"""
    input_variables = {
        "language_code": {
            "required": False,
            "description": "Default is en-US. This is only used for the language packs so it has currently no effect.",
        },
        "type": {
            "required": False,
            "description": (
                "Set the system/architecture. Accepted values are mac-x86 and mac-x86_64. "
                "If not defined, mac-x86 is used."),
        },
    }
    output_variables = {
        "url": {
            "description": "URL to the latest and closest LibreOffice release.",
        },
    }
    description = __doc__
    
    def get_metalinks(self, mirrorlist_url):
        """Parse the metadata page and get a link to the download locations XML"""
        try:
            f = urllib2.urlopen(mirrorlist_url)
            html = f.read()
            f.close()
        except BaseException as e:
            raise ProcessorError("Can't download %s: %s" % (mirrorlist_url, e))
        m = re_metalink.search(html)
        if not m:
            raise ProcessorError(
                "Couldn't find metalink url in %s" % mirrorlist_url)
        metalink_url = m.group("meta4_url")
        
        try:
            f = urllib2.urlopen(metalink_url)
            metalink_xml = f.read()
            f.close()
        except BaseException as e:
            raise ProcessorError("Can't download %s: %s" % (metalink_url, e))
        
        root = ET.fromstring(metalink_xml)
        all_urls = []
        for url in root.findall('.//{urn:ietf:params:xml:ns:metalink}url'):
            priority = url.get('priority')
            download_url = url.text
            location = url.get('location')
            if priority is None:
                continue
            url_dict = {
                    'priority': priority,
                    'url': download_url,
                    'location': location,
                    }
            all_urls.append(url_dict)
        return all_urls
    
    
    def get_mirrorlist_url(self, base_url):
        """Checks the given URL for a link to LibreOffice download metadata"""
        try:
            f = urllib2.urlopen(base_url)
            html = f.read()
            f.close()
        except BaseException as e:
            raise ProcessorError("Can't download %s: %s" % (base_url, e))
        m = re_mirrorlist.search(html)
        if not m:
            raise ProcessorError(
                "Couldn't find mirrorlist url in %s" % base_url)
        mirrorlist_url = m.group("mirrorlist_url")
        return mirrorlist_url
    
    
    def get_libreoffice_dmg_url(self, base_url):
        """Find and return a download URL"""
        
        # Get an URL describing the mirror locations
        mirrorlist_url = self.get_mirrorlist_url(base_url)
        
        # Get the metalink XML and parse it for download locations
        dmg_links = self.get_metalinks(mirrorlist_url)
        if len(dmg_links) > 0:
            mirrored_url = dmg_links[0].get('url', None)
            return mirrored_url
        else:
            raise ProcessorError("Couldn't find any download locations")
    
    
    def create_url(self):
        """Creates the main download URL"""
        base_url_start = self.env.get("base_url", MAIN_DOWNLOAD_URL)
        language_code = self.env.get("language_code", LANGUAGE_CODE)
        type = self.env.get("type", TYPE)
        type_component = '='.join(['type', type])
        lang_component = '='.join(['lang', language_code])
        request_string = '&'.join([type_component, lang_component])
        return '?'.join([base_url_start, request_string])
    
    
    def main(self):
        base_url = self.create_url()
        self.env["url"] = self.get_libreoffice_dmg_url(base_url)
        self.output("Found URL %s" % self.env["url"])


if __name__ == "__main__":
    processor = LibreOfficeURLProvider()
    processor.execute_shell()
