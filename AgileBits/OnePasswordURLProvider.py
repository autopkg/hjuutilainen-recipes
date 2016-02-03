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
import json

from autopkglib import Processor, ProcessorError


__all__ = ["OnePasswordURLProvider"]

# Variables for the update URL:
# - https://app-updates.agilebits.com/check/1/
# - Kernel version
# - String "OPM4"
# - Locale
# - The 1Password build number to update from
UPDATE_URL_FOUR = "https://app-updates.agilebits.com/check/1/13.0.0/OPM4/en/400600"
UPDATE_URL_FIVE = "https://app-updates.agilebits.com/check/1/14.0.0/OPM4/en/500000"
UPDATE_URL_SIX = "https://app-updates.agilebits.com/check/1/14.0.0/OPM4/en/553001"
DEFAULT_SOURCE = "Amazon CloudFront"
DEFAULT_MAJOR_VERSION = "6"


class OnePasswordURLProvider(Processor):
    """Provides a download URL for the latest 1Password"""
    input_variables = {
        "major_version": {
            "required": False,
            "description": "The 1Password major version to get. "
            "Possible values are '4', '5' or '6' and the default is '6'",
        },
        "base_url": {
            "required": False,
            "description": "The 1Password update check URL",
        },
        "source": {
            "required": False,
            "description": "Where to download the disk image. "
            "Possible values are 'Amazon CloudFront', 'CacheFly' and 'AgileBits'. "
            "Default is Amazon CloudFront."
        },
        "CURL_PATH": {
            "required": False,
            "default": "/usr/bin/curl",
            "description": "Path to curl binary. Defaults to /usr/bin/curl.",
        },
    }
    output_variables = {
        "url": {
            "description": "URL to the latest 1Password release.",
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
    
    def download_update_info(self, base_url):
        """Downloads the update url and returns a json object"""
        f = self.fetch_content(base_url, None)
        try:
            json_data = json.loads(f)
        except (ValueError, KeyError, TypeError) as e:
            self.output("JSON response was: %s" % f)
            raise ProcessorError("JSON format error: %s" % e)

        return json_data

    def get_1Password_dmg_url(self, base_url, preferred_source):
        """Find and return a download URL"""
        
        self.output("Preferred source is %s" % preferred_source)
        
        # 1Password update check gets a JSON response from the server.
        # Grab it and parse...
        info_plist = self.download_update_info(base_url)
        version = info_plist.get('version', None)
        self.output("Found version %s" % version)
        
        sources = info_plist.get('sources', [])
        found_source = next((source for source in sources if source['name'] == preferred_source), None)
        if found_source:
            source_url = found_source.get('url', None)
            if not source_url:
                raise ProcessorError("No URL found for %s" % preferred_source)
            return source_url
        else:
            raise ProcessorError("No download source for %s" % preferred_source)
    
    def main(self):
        major_version = self.env.get("major_version", DEFAULT_MAJOR_VERSION)
        if int(major_version) == 4:
            UPDATE_URL = UPDATE_URL_FOUR
        elif int(major_version) == 5:
            UPDATE_URL = UPDATE_URL_FIVE
        elif int(major_version) == 6:
            UPDATE_URL = UPDATE_URL_SIX
        else:
            raise ProcessorError("Unsupported value for major version: %s" % major_version)
        base_url = self.env.get("base_url", UPDATE_URL)
        source = self.env.get("source", DEFAULT_SOURCE)
        self.env["url"] = self.get_1Password_dmg_url(base_url, source)
        self.output("Found URL %s" % self.env["url"])


if __name__ == "__main__":
    processor = OnePasswordURLProvider()
    processor.execute_shell()
