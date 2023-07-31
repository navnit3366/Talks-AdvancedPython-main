import imp
from pathlib import Path
import sys
from xml.etree import ElementTree


def _xml_to_code(file):
    xml = ElementTree.parse(file)
    code = 'import structure as l\n'
    for node in xml.findall('struct'):
        code += _xml_struct_code(node)
    return code


def _xml_struct_code(node: ElementTree.Element):
    name = node.get('name')
    code = f'class {name}(l.Structure):\n'
    for field in node.findall('field'):
        field_name = field.get('name')
        typ = field.get('type')
        attributes = field.attrib.copy()
        del attributes['name']
        del attributes['type']
        params = ', '.join(f'{k}={v}' for k, v in attributes.items())
        code += f'    {field_name} = l.{typ}({params})\n'
    return code


class StructureImporter:
    def __init__(self, path):
        self._path = path

    def find_module(self, fullname: str, path=None):
        name = fullname.rpartition('.')[-1]
        if path is None:
            path = self._path
        for dir_name in path:
            filename = Path(dir_name) / f'{name}.struct'
            if filename.exists():
                return StructureXMLLoader(filename)
        return None
    

class StructureXMLLoader:
    def __init__(self, filename):
        self._filename = filename

    def load_module(self, fullname):
        mod = sys.modules.setdefault(fullname, imp.new_module(fullname))
        mod.__file__ = str(self._filename)
        mod.__loader__ = self
        code = _xml_to_code(self._filename)
        exec(code, mod.__dict__, mod.__dict__)
        return mod

    
sys.meta_path.append(StructureImporter(sys.path))

