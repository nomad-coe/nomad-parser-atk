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

from ase import Atoms
from ase.lattice.triclinic import Triclinic as TC
from ase.build import bulk


class UnitCell:
    def __init__(self, a, b, c, origin=None):
        self.cell = [a, b, c]


class Triclinic:
    def __init__(self, a, b, c, alpha, beta, gamma):
        self.cell = TC(symbol='X', latticeconstant=(a, b, c, alpha,
                                                    beta, gamma)).get_cell()
    def primitiveVectors(self):
        return self.cell

class FaceCenteredCubic:
    def __init__(self, a):
        self.cell = bulk('X', crystalstructure='fcc', a=a).get_cell()

    def primitiveVectors(self):
        return self.cell


class BodyCenteredCubic:
    def __init__(self, a):
        self.cell = bulk('X', crystalstructure='bcc', a=a).get_cell()

    def primitiveVectors(self):
        return self.cell


class BulkConfiguration:
    def __init__(self, bravais_lattice, elements, cartesian_coordinates=None,
                 fractional_coordinates=None, ghost_atoms=None,
                 velocities=None, tag_data=None, fast_init=False):
        if elements is None:
            symbols = None
        else:
            symbols = [e.symbol() for e in elements]
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
        atoms.ghost_atoms = ghost_atoms
        self.atoms = atoms


class MoleculeConfiguration:
    def __init__(self, elements=None, cartesian_coordinates=None,
                 fractional_coordinates=None, ghost_atoms=None,
                 velocities=None, tag_data=None, fast_init=False):
        if elements is None:
            symbols = None
        else:
            symbols = [e.symbol() for e in elements]
        if cartesian_coordinates is not None:
            positions = cartesian_coordinates
        else:
            positions = None
        pbc = False
        atoms = Atoms(symbols, positions, pbc=pbc)
        atoms.ghost_atoms = ghost_atoms
        self.atoms = atoms


things = {'UnitCell': UnitCell,
          'Triclinic': Triclinic,
          'FaceCenteredCubic': FaceCenteredCubic,
          'BulkConfiguration': BulkConfiguration,
          'MoleculeConfiguration': MoleculeConfiguration}

conf_types = ['MoleculeConfiguration',
              'BulkConfiguration']

if __name__ == '__main__':
    t = Triclinic(4.0, 4.0, 4.0, 90.0, 90.0, 90.0)
    print(t.primitiveVectors())
