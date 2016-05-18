#!/usr/bin/env python
#
# Copyright 2015 Hannes Juutilainen
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
from distutils.version import LooseVersion

from autopkglib import Processor, ProcessorError


__all__ = ["HashiCorpURLProvider"]

RELEASES_BASE_URL = "https://releases.hashicorp.com"
DEFAULT_OS = "darwin"
DEFAULT_ARCH = "all"


class HashiCorpURLProvider(Processor):
    """Provides a download URL for a HashiCorp project using their releases API"""
    input_variables = {
        "project_name": {
            "required": True,
            "description": "The name of the HashiCorp project to get. "
            "Possible values are listed at https://releases.hashicorp.com",
        },
        "os": {
            "required": False,
            "description": "",
        },
        "arch": {
            "required": False,
            "description": "Architecture to get: 386, amd64, arm",
        },
        "CURL_PATH": {
            "required": False,
            "default": "/usr/bin/curl",
            "description": "Path to curl binary. Defaults to /usr/bin/curl.",
        },
    }
    output_variables = {
        "url": {
            "description": "URL to the latest project release.",
        },
        "version": {
            "description": "URL to the latest project release.",
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
    
    def download_releases_info(self, base_url):
        """Downloads the update url and returns a json object"""
        f = self.fetch_content(base_url, None)
        try:
            json_data = json.loads(f)
        except (ValueError, KeyError, TypeError) as e:
            self.output("JSON response was: %s" % f)
            raise ProcessorError("JSON format error: %s" % e)

        return json_data
    
    def get_project_url(self, base_url, operating_system, architecture):
        """Find and return a download URL"""
        # Download a JSON with all releases
        releases = self.download_releases_info(base_url)
        #print json.dumps(releases, sort_keys=True, indent=4, separators=(',', ': '))
        
        # Sort versions with LooseVersion and get a dictionary for the latest version
        versions = releases.get('versions', None)
        version_numbers = versions.keys()
        version_numbers.sort(key=LooseVersion, reverse=True)
        latest_version = versions[version_numbers[0]]
        #print json.dumps(latest_version, sort_keys=True, indent=4, separators=(',', ': '))
        
        # Set the version variable
        self.env["version"] = latest_version.get('version', None)
        
        # Go through the builds and get the os and arch specific download URL
        builds = latest_version.get('builds', [])
        found_build = next((build for build in builds if build['os'] == operating_system and build['arch'] == architecture), None)
        if found_build:
            source_url = found_build.get('url', None)
            if not source_url:
                raise ProcessorError("No URL found for os: %s, arch: %s" % (operating_system, architecture))
            return source_url
        else:
            raise ProcessorError("No build for os: %s, arch: %s" % (operating_system, architecture))
    
    def main(self):
        project_name = self.env.get("project_name")
        operating_system = self.env.get("os", DEFAULT_OS)
        architecture = self.env.get("arch", DEFAULT_ARCH)
        base_url = "/".join([RELEASES_BASE_URL, project_name, "index.json"])
        self.env["url"] = self.get_project_url(base_url, operating_system, architecture)
        self.output("Found URL %s" % self.env["url"])


if __name__ == "__main__":
    processor = HashiCorpURLProvider()
    processor.execute_shell()
