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


__all__ = ["GIMPURLProvider"]


MAIN_DOWNLOAD_URL_GIMP = "http://www.gimp.org/downloads/"
MAIN_DOWNLOAD_URL_LISANET = "http://gimp.lisanet.de/Website/Download.html"
DEFAULT_FLAVOUR = "lisanet.de"
DEFAULT_SYSTEM_VERSION = "MountainLion"

class GIMPURLProvider(Processor):
    """Provides a download URL for the latest GIMP"""
    input_variables = {
        "flavour": {
            "required": False,
            "description": "Specify 'gimp.org' or 'lisanet.de'. This corresponds to the two "
                            "download options on http://www.gimp.org/downloads/. "
                            "If not defined, the default is 'lisanet.de'.",
        },
        "system_version": {
            "required": False,
            "description": "Specify 'Mavericks', 'MountainLion', 'Lion' or 'SnowLeopard'. "
                            "If not defined, the default is 'Mavericks'. This variable is "
                            "only used if we're using lisanet.de for the download. "
                            "Also note that 'MountainLion', 'Lion' and 'SnowLeopard' currently point to the same download.",
        },
    }
    output_variables = {
        "url": {
            "description": "URL to the latest GIMP release.",
        },
    }
    description = __doc__
    
    
    def get_GIMP_dmg_url(self, base_url):
        """Checks the given URL for a link to GIMP download"""
        try:
            f = urllib2.urlopen(base_url)
            html = f.read()
            f.close()
        except BaseException as e:
            raise ProcessorError("Can't download %s: %s" % (base_url, e))
        re_downloadlink = re.compile(r'<a href="(?P<download_url>ftp://ftp.gimp.org/pub/gimp/.*\.dmg)".*</a>', re.IGNORECASE)
        m = re_downloadlink.search(html)
        if not m:
            raise ProcessorError(
                "Couldn't find download url in %s" % base_url)
        download_url = m.group("download_url")
        return download_url
    
    
    def get_GIMP_dmg_url_lisanet(self, base_url, system_version):
        """Checks the given URL for a link to GIMP download"""
        try:
            f = urllib2.urlopen(base_url)
            html = f.read()
            f.close()
        except BaseException as e:
            raise ProcessorError("Can't download %s: %s" % (base_url, e))
        
        if system_version.lower() == "mavericks":
            re_downloadlink_lisanet = re.compile(r'.*href="(?P<download_url>http://sourceforge.net/projects/gimponosx/files/GIMP%20Mavericks/.*\.dmg/download)".*', re.IGNORECASE)
        elif system_version.lower() == "mountainlion":
            re_downloadlink_lisanet = re.compile(r'.*href="(?P<download_url>http://sourceforge.net/projects/gimponosx/files/GIMP%20Snow%20Leopard/.*\.dmg/download)".*', re.IGNORECASE)
        elif system_version.lower() == "lion":
            re_downloadlink_lisanet = re.compile(r'.*href="(?P<download_url>http://sourceforge.net/projects/gimponosx/files/GIMP%20Snow%20Leopard/.*\.dmg/download)".*', re.IGNORECASE)
        elif system_version.lower() == "snowleopard":
            re_downloadlink_lisanet = re.compile(r'.*href="(?P<download_url>http://sourceforge.net/projects/gimponosx/files/GIMP%20Snow%20Leopard/.*\.dmg/download)".*', re.IGNORECASE)
        else:
            raise ProcessorError(
                "Don't know how to handle system version: %s" % system_version)
        
        m = re_downloadlink_lisanet.search(html)
        if not m:
            raise ProcessorError(
                "Couldn't find download url in %s" % base_url)
        download_url = m.group("download_url")
        return download_url
    
    
    def main(self):
        flavour = self.env.get("flavour", DEFAULT_FLAVOUR)
        system_version = self.env.get("system_version", DEFAULT_SYSTEM_VERSION)
        if flavour == "gimp.org":
            base_url = self.env.get("base_url", MAIN_DOWNLOAD_URL_GIMP)
            self.env["url"] = self.get_GIMP_dmg_url(base_url)
        elif flavour == "lisanet.de":
            base_url = self.env.get("base_url", MAIN_DOWNLOAD_URL_LISANET)
            self.env["url"] = self.get_GIMP_dmg_url_lisanet(base_url, system_version)
        else:
            raise ProcessorError("Unknown flavour '%s'" % flavour)
        self.output("Found URL %s" % self.env["url"])


if __name__ == "__main__":
    processor = GIMPURLProvider()
    processor.execute_shell()
