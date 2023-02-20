from autopkglib import Processor, ProcessorError

__all__ = ["CreateLibreOfficeAuxArchName"]


class CreateLibreOfficeAuxArchName(Processor):
    """This processor provides the extra architecture name needed for LibreOffice download paths for x86_64."""
	
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
        if ( self.env["arch_name"] ==  'aarch64'):
            # this architecture name is used consistently
            self.env["aux_arch_name"] = 'aarch64'
        elif ( self.env["arch_name"] == 'x86_64' ):
            # for x86_64 they use both forms in the path :(
            self.env["aux_arch_name"] = 'x86-64'
        else:
            self.env["aux_arch_name"] = 'Architecture_' + arch_name + '_not_supported_by_CreateLibreOfficeAuxArchName.'
if __name__ == "__main__":
    PROCESSOR = CreateLibreOfficeAuxArchName()
    PROCESSOR.execute_shell()
