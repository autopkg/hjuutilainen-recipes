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

import subprocess
import plistlib

from autopkglib import Processor, ProcessorError


__all__ = ["AlfredURLProvider"]

# Update URLs for Alfred version 2.x
# Found in "Alfred 2.app/Contents/Frameworks/Alfred Framework.framework/Versions/A/Alfred Framework"
ALFRED2_UPDATE_URL = "https://cachefly.alfredapp.com/updater/info.plist"
ALFRED2_UPDATE_URL_PRERELEASE = "https://cachefly.alfredapp.com/updater/prerelease.plist"

# Update URLs for Alfred version 3.x
# Found in "Alfred 3.app/Contents/Frameworks/Alfred Framework.framework/Versions/A/Alfred Framework"
ALFRED3_UPDATE_URL = "https://www.alfredapp.com/app/update/general.xml"
ALFRED3_UPDATE_URL_PRERELEASE = "https://www.alfredapp.com/app/update/prerelease.xml"

DEFAULT_MAJOR_VERSION = "2"
DEFAULT_RELEASE_TYPE = "stable"

class AlfredURLProvider(Processor):
    """Provides a download URL for the latest Alfred"""
    input_variables = {
        "base_url": {
            "required": False,
            "description": "The Alfred update info property list URL",
        },
        "major_version": {
            "required": False,
            "description": "The Alfred major version to get. "
            "Possible values are '2'or '3' and the default is '2'",
        },
        "release_type": {
            "required": False,
            "description": "The Alfred release type to get. "
            "Possible values are 'stable' or 'prerelease'",
        },
        "CURL_PATH": {
            "required": False,
            "default": "/usr/bin/curl",
            "description": "Path to curl binary. Defaults to /usr/bin/curl.",
        },
    }
    output_variables = {
        "url": {
            "description": "URL to the latest Alfred release.",
        },
        "version": {
            "description": "Version of the latest Alfred release.",
        },
    }
    description = __doc__
    
    def fetch_content(self, url, headers=None):
        """Returns content retrieved by curl, given a url and an optional
        dictionary of header-name/value mappings. Logic here borrowed from
        URLTextSearcher processor."""

        try:
            cmd = [self.env['CURL_PATH'], '--location']
            if headers:
                for header, value in headers.items():
                    cmd.extend(['--header', '%s: %s' % (header, value)])
            cmd.append(url)
            proc = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            (data, stderr) = proc.communicate()
            if proc.returncode:
                raise ProcessorError(
                    'Could not retrieve URL %s: %s' % (url, stderr))
        except OSError:
            raise ProcessorError('Could not retrieve URL: %s' % url)

        return data
    
    def download_info_plist(self, base_url):
        """Downloads the info.plist file and returns a plist object"""
        f = self.fetch_content(base_url, None)
        info_plist = plistlib.readPlistFromString(f)
        
        return info_plist
    
    def get_alfred2_url(self, base_url):
        """Find and return a download URL for Alfred 2"""
        
        # Alfred 2 update check uses a standard plist file.
        # Grab it and parse...
        info_plist = self.download_info_plist(base_url)
        version = info_plist.get('version', None)
        self.env["version"] = version
        self.output("Found version %s" % version)
        location = info_plist.get('location', None)
        
        return location
    
    def get_alfred3_url(self, base_url):
        """Find and return a download URL for Alfred 3"""
        
        # Alfred 3 update check uses a standard plist file.
        # The file has the same structure as the version 2 update file
        # but we're keeping these methods separate in case something changes
        # in future.
        info_plist = self.download_info_plist(base_url)
        version = info_plist.get('version', None)
        self.env["version"] = version
        self.output("Found version %s" % version)
        location = info_plist.get('location', None)
        
        return location
    
    def main(self):
        major_version = self.env.get("major_version", DEFAULT_MAJOR_VERSION)
        self.output("Major version is set to %s" % major_version)
        release_type = self.env.get("release_type", DEFAULT_RELEASE_TYPE)
        self.output("Release type is set to %s" % release_type)
        
        # Alfred 2
        if int(major_version) == 2:
            if release_type == "stable":
                base_url = self.env.get("base_url", ALFRED2_UPDATE_URL)
            elif release_type == "prerelease":
                base_url = self.env.get("base_url", ALFRED2_UPDATE_URL_PRERELEASE)
            else:
                raise ProcessorError("Unsupported value for release_type: %s" % release_type)
            self.output("Using URL %s" % base_url)
            self.env["url"] = self.get_alfred2_url(base_url)
        
        # Alfred 3
        elif int(major_version) == 3:
            if release_type == "stable":
                base_url = self.env.get("base_url", ALFRED3_UPDATE_URL)
            elif release_type == "prerelease":
                base_url = self.env.get("base_url", ALFRED3_UPDATE_URL_PRERELEASE)
            else:
                raise ProcessorError("Unsupported value for release_type: %s" % release_type)
            self.output("Using URL %s" % base_url)
            self.env["url"] = self.get_alfred3_url(base_url)
        
        else:
            raise ProcessorError("Unsupported value for major_version: %s" % major_version)
        
        self.output("Found URL %s" % self.env["url"])


if __name__ == "__main__":
    processor = AlfredURLProvider()
    processor.execute_shell()
