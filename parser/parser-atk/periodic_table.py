from ase.data import atomic_names, atomic_numbers, chemical_symbols,\
        atomic_masses

def name(self):
    return self._name


def atomicNumber(self):
    return self._atomic_number


def symbol(self):
    return self._symbol


def atomicMass(self):
    return self._atomic_mass_amu

things = {}
for n, s, m in zip(atomic_names[1:], chemical_symbols[1:],
                      atomic_masses[1:]):
    stuff = {'_atomic_number': atomic_numbers[s],
             '_name': n,
             '_symbol': s,
             '_atomic_mass_amu': m,
             'atomicNumber': atomicNumber,
             'name': name,
             'atomicMass': atomicMass,
             'symbol': symbol}
    element = type(n, (object,), stuff)
    exec(n + ' = element()')
    #exec(s + ' = ' + n)
    exec('things[n] = ' + n)

# clean up
del stuff, name, atomicNumber, symbol, atomicMass, n, s, m, element
del atomic_names, atomic_numbers, chemical_symbols, atomic_masses
