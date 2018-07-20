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
