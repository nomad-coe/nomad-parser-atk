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

import ase.units as au
import numpy as np

class PhysicalQuantity(list):
    def __init__(self, val):
        self.val = val
    def __mul__(self, other):
        if type(other) is not list:
            if type(other) is not tuple:
                return self.val * other
        out = (np.asarray(other) * self.val).tolist()
        if type(other) is tuple:
            out = tuple(out)
        return out
    def __rmul__(self, other):
        return self.__mul__(other)
    def __repr__(self):
        return format(self.val)

eV = PhysicalQuantity(au.eV)
Angstrom = PhysicalQuantity(au.Angstrom)
Hartree = PhysicalQuantity(au.Hartree)
Bohr = PhysicalQuantity(au.Bohr)
Kelvin = PhysicalQuantity(au.kB)
Hour = 1
Degrees = PhysicalQuantity(1.0)
amu = PhysicalQuantity(1.0)
things = {'eV': eV,
          'Angstrom': Angstrom,
          'Hartree': Hartree,
          'Bohr': Bohr,
          'Kelvin': Kelvin,
          'Hour': Hour,
          'Degrees': Degrees,
          'amu': amu}

if __name__ == '__main__':
    print(Angstrom*4.0)
