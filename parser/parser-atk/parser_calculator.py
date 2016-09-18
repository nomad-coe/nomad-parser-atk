from ase import data
import re
from physical_quantities import eV, Angstrom, Bohr, Kelvin, Hour, Hartree

All = 'All'
Automatic = 'Automatic'
HamiltonianVariable = 'HamiltonianVariable'
SphericalSymmetric = 'SphericalSymmetric'


LDA = type('LDA', (object,), {'PZ': 'LDA.PZ',
                              'PW': 'LDA.PW'})()

GGA = type('GGA', (object,), {'PBE': 'GGA.PBE',
                              'RPBE': 'GGA.RPBE',
                              'PW91': 'GGA.PW91'})()

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
# is easily done, but a bit more work at the moment
#
def init(self, *args, **kwargs):
    self.args = args
    for key, value in kwargs.iteritems():
        setattr(self, key, value)


clss = ['LCAOCalculator', 'BasisSet', 'ConfinedOrbital', 'CheckpointHandler',
        'ParallelParameters', 'AlgorithmParameters', 'DiagonalizationSolver',
        'FastFourierSolver', 'IterationControlParameters',
        'NumericalAccuracyParameters', 'MonkhorstPackGrid',
        'NormConservingPseudoPotential', 'AnalyticalSplit', 'ConfinedOrbital',
        'PolarizationOrbital', 'PulayMixer']
for cls in clss:
    code = cls + ' = type("' + cls + '", (object,)' + ', {"__init__": init})'
    exec(code)


def parse_calculator(fd, conf='BulkConfiguration_gID000', verbose=False):
    """conf: the configuratio the calcualtor refers to
    """
    code = fd.variables[conf + '_calculator'].data[:].copy()
    code = code.tostring().decode("utf-8")
    s = re.search('\s*(?P<name>[0-9a-zA-Z_]+)\s*=\s*LCAOCalculator\(', code)
    name = s.group('name')
    exec(code)
    calc = (locals()[name])
    return calc

if __name__ == '__main__':
    from scipy.io.netcdf import netcdf_file
    fd = netcdf_file('Water.nc', 'r')
    calc = parse_calculator(fd)
