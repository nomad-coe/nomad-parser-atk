# Copyright 2016-2018 Mikkel Strange, Fawzi Mohamed
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

from atkparser.periodic_table import things as ptab_ns
from atkparser.physical_quantities import things as physquan_ns
from atkparser.configurations import conf_types, things as confs_ns


def parse_configuration(fd, name, verbose=False):
    """ convert a nanolanguage python script into
    ASE list of atoms.

    Parameters:

        fd: netcdf_file handle
        name: str (i.e "BulkConfiguration_gID000")

    """
    code = fd.variables[name].data[:].copy()
    code = code.tostring().decode("utf-8")
    if 0:
        print('parsing code:\n------------')
        print(code)

    things = ptab_ns.copy()
    things.update(physquan_ns)
    things.update(confs_ns)
    exec(code, {}, things)
    for obj in things.values():
        for conf_type in conf_types:
            if isinstance(obj, confs_ns[conf_type]):
                return obj.atoms
    return -1


if __name__ == '__main__':
    from ase.visualize import view
    from scipy.io.netcdf import netcdf_file
    import sys
    fd = netcdf_file(sys.argv[1], 'r')
    name = 'BulkConfiguration_gID000'
    atoms = parse_configuration(fd, name)
    view(atoms)
#    configurations = {}
#    fp_gids = fd.fingerprint_table[:].decode('utf-8').split('#')
#    for c in fp_gids:
#        if len(c) > 0:
#            fingerprint, gID = c.split(':')[:2]
#            gID.strip()
#            for name in ['BulkConfiguration_' + gID,
#                         'MoleculeConfiguration_' + gID]:
#                if name in fd.variables.keys():
#                    configurations[name] = fingerprint
#
#    for name, fingerprint in configurations.items():
#        print(name+',', fingerprint)
#        atoms = parse_configuration(fd, name)
#        view(atoms)
