from ase import Atoms
from ase.build import bulk
import re

Angstrom = 1
Hydrogen = type('Hydrogen', (object,), {})
Hydrogen.symbol = 'H'
Helium= type('Helium', (object,), {})
Helium.symbol = 'H'
Lithium= type('Lithium', (object,), {})
Lithium.symbol = 'Si'
Oxygen = type('Oxygen', (object,), {})
Oxygen.symbol = 'O'
Silicon = type('Silicon', (object,), {})
Silicon.symbol = 'Si'



class UnitCell:
    def __init__(self, a, b, c, origin=None):
        self.cell = [a, b, c]

class FaceCenteredCubic:
    def __init__(self, a):
       self.cell = bulk('X', crystalstructure='fcc', a=a).get_cell()


class BulkConfiguration:
    def __init__(self, bravais_lattice, elements, cartesian_coordinates=None,
                 fractional_coordinates=None, ghost_atoms=None,
                 velocities=None, tag_data=None, fast_init=False):
        self.bulkconfiguration = True
        symbols = [e.symbol for e in elements]
        if cartesian_coordinates is not None:
            positions = cartesian_coordinates
            scale_atoms = False
        elif fractional_coordinates is not None:
            positions = fractional_coordinates
            scale_atoms = True
        else:
            positions = None
            scale_atoms = False
        pbc = True
        atoms = Atoms(symbols, positions, pbc=pbc)
        atoms.set_cell(bravais_lattice.cell, scale_atoms=scale_atoms)
        self.ghost_atoms_indices = ghost_atoms
        self.atoms = atoms


def parse_configuration(fd, conftype='BulkConfiguration', verbose=False):
    code = fd.variables[conftype + '_gID000'].data[:].copy()
    code = code.tostring().decode("utf-8")
    s = re.search('\s*(?P<name>[0-9a-zA-Z_]+)\s*=\s*BulkConfiguration\(', code)
    name = s.group('name')
    if verbose:
        print('name:', name)
        print(code)

    exec(code)
    atoms = (locals()[name]).atoms
    return atoms

if __name__ == '__main__':
    import re
    from scipy.io.netcdf import netcdf_file
    fd = netcdf_file('Water.nc', 'r')
    atoms = parse_configuration(fd, verbose=True)
    print(atoms)
