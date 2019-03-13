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

from ase import data
import re
from atkparser.physical_quantities import eV, Angstrom, Bohr, Kelvin, Hour, Hartree

All = 'All'
Automatic = 'Automatic'
HamiltonianVariable = 'HamiltonianVariable'
SphericalSymmetric = 'SphericalSymmetric'


LDA = type('LDA', (object,), {'PZ': 'LDA.PZ',
                              'PW': 'LDA.PW',
                              'RPA': 'LDA.RPA'})()

GGA = type('GGA', (object,), {'PBE': 'GGA.PBE',
                              'RPBE': 'GGA.RPBE',
                              'PW91': 'GGA.PW91',
                              'PBES': 'GGA.PBES'})()

ptable = {name: symbol for symbol, name in zip(data.chemical_symbols,
                                               data.atomic_names)}
PeriodicTable = type('PeriodicTable', (object,), ptable)()

Preconditioner = type('Preconditioner', (object,), {'Off': 'Off',

                                                    'On': 'On'})


# Populate with dummy classes to hold hold variables (assumes kwargs!)
# Otherwise we have to build all of them with something like
# class LCAOCalculator(object):
#     def __init__(self, basis_set=None, ...)
#
# is easily done, but a bit more work at the moment...
#
def init(self, *args, **kwargs):
    #if len(args)>0:
    #    print(*args)
    #assert len(args) == 0
    self.args = args
    for key, value in kwargs.items():
        setattr(self, key, value)


clss = ['LCAOCalculator', 'BasisSet', 'ConfinedOrbital', 'CheckpointHandler',
        'ParallelParameters', 'AlgorithmParameters', 'DiagonalizationSolver',
        'FastFourierSolver', 'IterationControlParameters',
        'NumericalAccuracyParameters', 'MonkhorstPackGrid',
        'NormConservingPseudoPotential', 'AnalyticalSplit', 'ConfinedOrbital',
        'PolarizationOrbital', 'PulayMixer', 'HydrogenOrbital']

for cls in clss:
    code = cls + ' = type("' + cls + '", (object,)' + ', {"__init__": init})'
    exec(code)


def parse_calculator(fd, calcname):
    """calc: the configuratio the calcualtor refers to
       The name of the calculator in the nc-file is
       conf_calculator, fx BulkConfiguration_gID000_calculator
    """
    code = fd.variables[calcname].data[:].copy()
    code = code.tostring().decode("utf-8")
    if 0:
        print(code)
    #s = re.search('\s*(?P<name>[0-9a-zA-Z_]+)\s*=\s*LCAOCalculator\(', code)
    #name = s.group('name')
    exec(code)
    for obj in locals().values():
        if isinstance(obj, LCAOCalculator):
            return obj
    assert 0, 'No calculator found'

if __name__ == '__main__':
    from scipy.io.netcdf import netcdf_file
    fd = netcdf_file('Water.nc', 'r')
    calc = parse_calculator(fd, 'BulkConfiguration_gID000_calculator')
    print(dir(calc))
