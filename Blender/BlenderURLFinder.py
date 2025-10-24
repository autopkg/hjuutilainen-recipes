#!/usr/local/autopkg/python

from autopkglib import Processor, ProcessorError
import subprocess
import re

__all__ = ["BlenderURLFinder"]

class BlenderURLFinder(Processor):
    description = "Finds the latest Blender macOS Intel & ARM64 DMG URLs."
    input_variables = {}
    output_variables = {
        "intel_url": "Download URL for Blender macOS x64 (Intel).",
        "arm_url": "Download URL for Blender macOS arm64 (Apple Silicon).",
        "found_version": "The latest Blender version string found on the site."
    }

    def get_html(self, url):
        """Fetch page contents using macOS system curl."""
        try:
            result = subprocess.run(
                ["curl", "-fsSL", url],
                capture_output=True,
                text=True,
                check=True,
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            raise ProcessorError(f"Failed to fetch {url}: {e}")

    @staticmethod
    def version_key(v):
        """Converts a version string like '4.2.1' or '4.2' to a numeric tuple."""
        parts = re.findall(r'\d+', v)
        return tuple(int(p) for p in parts)

    def main(self):
        base_url = "https://download.blender.org/release/"
        base_html = self.get_html(base_url)

        folders = re.findall(r'Blender(\d+\.\d+)/', base_html)
        if not folders:
            raise ProcessorError("No Blender version folders found.")

        latest_minor = max(folders, key=self.version_key)
        patch_url = f"{base_url}Blender{latest_minor}/"
        patch_html = self.get_html(patch_url)

        patch_versions = re.findall(r'blender-(\d+\.\d+\.\d+)', patch_html)
        if not patch_versions:
            raise ProcessorError("No Blender patch versions found.")

        latest_patch = max(patch_versions, key=self.version_key)

        self.env["intel_url"] = f"{patch_url}blender-{latest_patch}-macos-x64.dmg"
        self.env["arm_url"] = f"{patch_url}blender-{latest_patch}-macos-arm64.dmg"
        self.env["found_version"] = latest_patch

        self.output(f"Found Blender {latest_patch}")
        self.output(f"Intel URL: {self.env['intel_url']}")
        self.output(f"ARM URL:   {self.env['arm_url']}")

if __name__ == "__main__":
    PROCESSOR = BlenderURLFinder()
    PROCESSOR.execute_shell()
