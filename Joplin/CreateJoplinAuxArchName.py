from autopkglib import Processor, ProcessorError

__all__ = ["CreateJoplinAuxArchName"]


class CreateJoplinAuxArchName(Processor):
    """This processor provides the extra architecture name needed for Joplin download paths for x86_64."""
	
    input_variables = {
        "arch_name": {
            "required": True,
            "description": "The name of the architecture used in the source DMG and the output PKG.",
        }
    }
    output_variables = {
        "aux_arch_name": {"description": "The second form of architecture name used in the download path for x86_64.",}
    }

    description = __doc__

    def main(self):
        if ( self.env["arch_name"] ==  'arm64'):
            # this architecture name is used consistently
            self.env["aux_arch_name"] = 'arm64'
        elif ( self.env["arch_name"] == 'x86_64' ):
            # for x86_64 Joplin uses 'mac' in the path :(
            self.env["aux_arch_name"] = 'mac'
        else:
            self.env["aux_arch_name"] = 'Architecture_' + arch_name + '_not_supported_by_CreateJoplinAuxArchName.'
if __name__ == "__main__":
    PROCESSOR = CreateJoplinAuxArchName()
    PROCESSOR.execute_shell()
