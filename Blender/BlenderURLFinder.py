#!/usr/local/autopkg/python

from autopkglib import Processor, ProcessorError
import requests
import re
from packaging import version

__all__ = ["BlenderURLFinder"]

class BlenderURLFinder(Processor):
    description = "Finds latest Blender macOS Intel & ARM64 DMG URLs."
    input_variables = {}
    output_variables = {
        "intel_url": "Download URL for Blender macOS x64 (Intel).",
        "arm_url": "Download URL for Blender macOS arm64 (Apple Silicon)."
    }

    def get_html(self, url):
        try:
            resp = requests.get(url)
            resp.raise_for_status()
            return resp.text
        except Exception as e:
            raise ProcessorError(f"Failed to fetch {url}: {e}")

    def main(self):
        base_url = "https://download.blender.org/release/"
        base_html = self.get_html(base_url)

        folders = re.findall(r'Blender(\d+\.\d+)/', base_html)
        if not folders:
            raise ProcessorError("No Blender version folders found.")

        latest_minor = max(folders, key=version.parse)
        patch_url = f"{base_url}Blender{latest_minor}/"
        patch_html = self.get_html(patch_url)
        patch_versions = re.findall(r'blender-(\d+\.\d+\.\d+)', patch_html)
        if not patch_versions:
            raise ProcessorError("No Blender patch versions found.")

        latest_patch = max(patch_versions, key=version.parse)
        # Build URLs for Intel and ARM
        self.env["intel_url"] = f"{patch_url}blender-{latest_patch}-macos-x64.dmg"
        self.env["arm_url"] = f"{patch_url}blender-{latest_patch}-macos-arm64.dmg"

if __name__ == "__main__":
    PROCESSOR = BlenderURLFinder()
    PROCESSOR.execute_shell()
