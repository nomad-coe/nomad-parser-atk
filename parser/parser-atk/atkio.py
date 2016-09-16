"""Simple wrapper to atk output files"""
from scipy.io.netcdf import netcdf_file


class X:
    def __init__(self, name=None):
        self.name = name


class Atoms:
    def __init__(self):
        self.positions = None
        self.numbers = None
        self.cell = None
        self.pbc = None


class Hamiltonian:
    def __init__(self):
        self.e_entropy = None
        self.e_kinetic = None
        self.e_total_free = None
        self.e_total_extrapolated = None
        self.e_xc = None


class BandPath:
    def __init__(self):
        self.labels = None
        self.eigenvalues = None
        self.kpts = None


class WaveFunctions:
    def __init__(self):
        self.occupations
        self.eigenvalues = None
        self.ibz_kpts = None
        self.band_paths = None


class Reader:
    def __init__(self, filename):
        self.f = netcdf_file(filename)
        self.v = self.f.variables
        self.read_atoms()
        self.read_hamiltonian()
        self.read_wave_functions()

        self.xc = None

    def read_atoms(self):
        self.atoms = Atoms()

    def read_hamiltonian(self):
        self.hamiltonian = Hamiltonian()

    def read_wave_functions(self):
        self.wave_functions = WaveFunctions()

    def get_number_of_structures(self):
        """ Several structures could in principle be in one file
            how many we are dealing with
        """
        return 1
