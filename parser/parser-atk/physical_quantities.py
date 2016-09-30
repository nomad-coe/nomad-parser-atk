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
