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
from distutils.version import StrictVersion

from autopkglib import Processor, ProcessorError


__all__ = ["OpenOfficeURLProvider"]


LANGUAGE_CODE = "en-US"
LOCATOR_URL = "http://www.apache.org/dyn/closer.lua/openoffice/"
re_URL = re.compile(r'\<strong\>(?P<the_url>http://.+)\</strong\>')
re_link = re.compile(r'<a href="(.*?)">.*?</a>', re.IGNORECASE)

# Download link format: Apache_OpenOffice_<version>_MacOS_x86_install_en-US.dmg
re_dmg = re.compile(r'a[^>]* href="(?P<filename>Apache_OpenOffice_[\d]+.*_MacOS_x86-64_install.+\.dmg)"', re.IGNORECASE)
re_version = re.compile(r'(?P<version>[0-9]+\.[0-9]+\.[0-9]+).*')


class OpenOfficeURLProvider(Processor):
    """Provides a download URL for the latest Open Office"""
    input_variables = {
        "base_url": {
            "required": False,
            "description": "Default is to use the closest mirror. List of apache mirrors: http://www.apache.org/mirrors/",
        },
        "language_code": {
            "required": False,
            "description": "Default is en-US",
        },
    }
    output_variables = {
        "url": {
            "description": "URL to the latest and closest OpenOffice release.",
        },
    }
    description = __doc__
    
    
    def get_closest_apache_mirror(self):
        """Returns the closest OpenOffice mirror URL"""
        try:
            f = urllib2.urlopen(LOCATOR_URL)
            html = f.read()
            f.close()
        except BaseException as e:
            raise ProcessorError("Can't download %s: %s" % (LOCATOR_URL, e))

        m = re_URL.search(html)

        if not m:
            raise ProcessorError(
                "Couldn't find closest mirror link in %s" % LOCATOR_URL)
        
        closest_url = m.group("the_url")
        self.output("Closest mirror is %s" % closest_url)
        return closest_url
    
    
    def versions_at_url(self, url):
        """Parses an Apache file list page for links that look like version numbers"""
        try:
            f = urllib2.urlopen(url)
            mirrorhtml = f.read()
            f.close()
        except BaseException as e:
            raise ProcessorError("Can't download %s: %s" % (url, e))
        
        links = re.findall(re_link, mirrorhtml)
        if not links:
            raise ProcessorError(
                "Couldn't find links in %s" % url)
        
        found_versions = []
        for link_name in links:
            m = re_version.search(link_name)
            if not m:
                continue
            version_number = m.group("version")
            found_versions.append(version_number)
        
        # Sort the versions
        found_versions.sort(key=StrictVersion)
        
        # Reverse the array so the first item is the latest item
        found_versions.reverse()
        
        return found_versions
    
    
    def dmg_link_at_url(self, url):
        """Checks the given URL for a link to OpenOffice installer"""
        try:
            f = urllib2.urlopen(url)
            html = f.read()
            f.close()
        except BaseException as e:
            # Don't raise anything since this url might not exist.
            # Return None instead and the requester will move on to the next URL
            self.output("Can't download %s: %s" % (url, e))
            return None
        
        m = re_dmg.search(html)
        if not m:
            raise ProcessorError(
                "Couldn't find dmg links in %s" % url)
        
        dmg_url = '/'.join(s.strip('/') for s in [url, m.group("filename")])
        return dmg_url
    
    
    def get_openoffice_dmg_url(self, base_url, language_code):
        """Find and return a download URL"""
        
        # Determine the closest mirror or use the override base_url
        if base_url == LOCATOR_URL:
            closest_mirror = self.get_closest_apache_mirror()
        else:
            self.output("Using mirror %s" % base_url)
            closest_mirror = base_url
        
        # Get a list of available versions from the mirror
        versions = self.versions_at_url(closest_mirror)
        
        # Did we get anything?
        if len(versions) == 0:
            raise ProcessorError("Couldn't find any versions")
        
        # Go through each version and check if there's something to download. The versions
        # list is already sorted by version with the latest version at index 0.
        for version in versions:
            
            # Create an URL for the file list page. The URL format appears is:
            # http://<mirror_URL>/<version>/binaries/<language_code>/
            url_pieces = [closest_mirror, version, 'binaries', language_code]
            version_url = '/'.join(s.strip('/') for s in url_pieces)
            
            # If the URL is valid and contains a valid dmg file, bail out and return it
            dmg_url = self.dmg_link_at_url(version_url)
            if dmg_url:
                return dmg_url
        
        # If we got this far, the following happened:
        #   - We succesfully resolved a mirror link
        #   - We found one or more versions from the mirror
        #   ...but...
        #   - The mirror doesn't contain anything for the version and requested language.
        #     Usually this means a new version has been released but it hasn't yet fully
        #     propagated to all mirrors.
        raise ProcessorError(
            "Found one or more versions but couldn't find any download links for language %s" % language_code)
    
    
    def main(self):
        base_url = self.env.get("base_url", LOCATOR_URL)
        language_code = self.env.get("language_code", LANGUAGE_CODE)
        self.env["url"] = self.get_openoffice_dmg_url(base_url, language_code)
        self.output("Found URL %s" % self.env["url"])


if __name__ == "__main__":
    processor = OpenOfficeURLProvider()
    processor.execute_shell()
