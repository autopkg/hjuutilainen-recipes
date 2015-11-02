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

import urllib2
import json
from distutils.version import StrictVersion

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
            "description": "",
        },
    }
    output_variables = {
        "url": {
            "description": "URL to the latest project release.",
        },
    }
    description = __doc__
    
    def download_releases_info(self, base_url):
        """Downloads the update url and returns a json object"""
        try:
            f = urllib2.urlopen(base_url)
            json_data = json.load(f)
        except BaseException as e:
            raise ProcessorError("Can't download %s: %s" % (base_url, e))

        return json_data
    
    def get_project_url(self, base_url, operating_system, architecture):
        """Find and return a download URL"""
        releases = self.download_releases_info(base_url)
        versions = releases.get('versions', None)
        version_numbers = versions.keys()
        version_numbers.sort(key=StrictVersion, reverse=True)
        latest_version = versions[version_numbers[0]]
        #print json.dumps(latest_version, sort_keys=True, indent=4, separators=(',', ': '))
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
