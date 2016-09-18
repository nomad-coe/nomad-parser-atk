from ase.units import Bohr, Angstrom, kB as Kelvin, eV, Hartree


class PC(list):
    def __init__(self, val):
        self.val = val
    def __mul__(self, other):
        if type(other) is not list:
            if type(other) is not tuple:
                return self.val * other
        out = [o * self.val for o in other]
        if type(other) is tuple:
            out = tuple(out)
        return out
    def __rmul__(self, other):
        return self.__mul__(other)
    def __repr__(self):
        return format(self.val)


eV = PC(eV)
Angstrom = PC(Angstrom)
Hartree = PC(Hartree)
Bohr = PC(Bohr)
Kelvin = PC(Kelvin)
Hour = 1


