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

from __future__ import absolute_import

from autopkglib import Processor, ProcessorError, URLGetter

try:
    from plistlib import loads as plist_from_string
except ImportError:
    from plistlib import readPlistFromString as plist_from_string


__all__ = ["AlfredURLProvider"]

# Update URLs for Alfred versions
# Found in "Alfred (version).app/Contents/Frameworks/Alfred
# Framework.framework/Versions/A/Alfred Framework"
UPDATE_URLS = {
    "2": {
        "stable": "https://cachefly.alfredapp.com/updater/info.plist",
        "prerelease": "https://cachefly.alfredapp.com/updater/prerelease.plist",
    },
    "3": {
        "stable": "https://www.alfredapp.com/app/update/general.xml",
        "prerelease": "https://www.alfredapp.com/app/update/prerelease.xml",
    },
    "4": {
        "stable": "https://www.alfredapp.com/app/update4/general.xml",
        "prerelease": "https://www.alfredapp.com/app/update4/prerelease.xml",
    },
    "5": {
        "stable": "https://www.alfredapp.com/app/update5/general.xml",
        "prerelease": "https://www.alfredapp.com/app/update5/prerelease.xml",
    },
}

DEFAULT_MAJOR_VERSION = "2"
DEFAULT_RELEASE_TYPE = "stable"


class AlfredURLProvider(URLGetter):
    """Provides a download URL for the latest Alfred."""

    input_variables = {
        "base_url": {
            "required": False,
            "description": "The Alfred update info property list URL",
        },
        "major_version": {
            "required": False,
            "description": "The Alfred major version to get. "
            "The default value is %s. Possible values are: "
            "'%s'" % (DEFAULT_MAJOR_VERSION, "', '".join(UPDATE_URLS)),
        },
        "release_type": {
            "required": False,
            "description": "The Alfred release type to get. "
            "Possible values are 'stable' or 'prerelease'",
        },
    }
    output_variables = {
        "url": {"description": "URL to the latest Alfred release.",},
        "version": {"description": "Version of the latest Alfred release.",},
    }
    description = __doc__

    def download_info_plist(self, base_url):
        """Downloads the info.plist file and returns a plist object."""
        f = self.download(base_url)
        info_plist = plist_from_string(f)

        return info_plist

    def get_alfred_url(self, base_url):
        """Find and return a download URL for Alfred 2."""

        # Alfred 2, 3, and 4 update check uses a standard plist file.
        # If this changes in the future, we'll need to copy/adjust this method.
        info_plist = self.download_info_plist(base_url)
        version = info_plist.get("version", None)
        self.env["version"] = version
        self.output("Found version %s" % version)
        location = info_plist.get("location", None)

        return location

    def main(self):
        """Main process."""

        # Acquire input variables
        major_version = self.env.get("major_version", DEFAULT_MAJOR_VERSION)
        self.output("Major version is set to %s" % major_version)
        release_type = self.env.get("release_type", DEFAULT_RELEASE_TYPE)
        self.output("Release type is set to %s" % release_type)

        # Validate inputs
        if major_version not in UPDATE_URLS:
            raise ProcessorError(
                "Unsupported value for major_version: %s" % major_version
            )
        if release_type not in ("stable", "prerelease"):
            raise ProcessorError(
                "Unsupported value for release_type: %s" % release_type
            )

        # Get base URL depending on major version and release type
        base_url = self.env.get("base_url", UPDATE_URLS[major_version][release_type])
        self.output("Using URL %s" % base_url)

        # Get download URL by parsing content of base URL
        self.env["url"] = self.get_alfred_url(base_url)

        self.output("Found URL %s" % self.env["url"])


if __name__ == "__main__":
    PROCESSOR = AlfredURLProvider()
    PROCESSOR.execute_shell()
