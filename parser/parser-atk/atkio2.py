from copy import copy
from scipy.io.netcdf import netcdf_file
from parser_configurations import parse_configuration as p_conf
#from parser_calculator import parse_calculator as p_calc

class X:
    def __init__(self, name=None):
        self.name = name

def has_data_with(what, f):
    for key in f.variables.keys():
        if what in key:
            return True
    return False

class Reader:
    def __init__(self, fname):
        self.f = netcdf_file(fname, 'r', mmap=True)
        self.CommonConcepts = X('CommonConcepts')
        self.CommonConcepts.Configurations = X('Configurations')

        if 0:
            gIDs = []
            for k in self.f.dimensions.keys():
                if '_gID' not in k:
                    continue
                i = k.index('_gID')
                gID = int(k[i+4: i+7])
                if gID not in gIDs:
                    gIDs.append(gID)

            self.gIDs = gIDs

        self.atk_version = self.f.version[4:].decode('utf-8')
        self.finger_prints = [x.split(':') for x in
                              self.f.fingerprint_table.\
                              decode('utf-8').split('#')][:-1]
        self.extract_common_concepts() #  atoms
        self.extract_total_energy()
        self.extract_calculator()
        self.extract_results()
        self.extract_wave_functions()
        self.extract_bandstructure()

    def print_keys(self):
        print('---dimensions---')
        for k in self.f.dimensions.keys():
            print(k)
        print('---variables---')
        for k in self.f.variables.keys():
            print(k)

    def extract_wave_functions(self):
        """ extract eigenvalues, occupations and wave_functions 
        """
        self.wave_functions = X('wave_functions')

    def extract_calculator(self):
        #p_calc(self)
        # dummy until p_calc stops crashing!
        self.calculator = X('calculator')
        self.calculator.basis = 'dzp'
        self.calculator.method = 'DFT'
        self.calculator.xc = 'LDA'
        self.calculator.charge = 0
        self.calculator.temp = 300.0  # icp
        self.calculator.dens_tolerance = 0.0001 # icp

    def extract_bandstructure(self):
        self.wave_functions = X('wave_functions')
        what = 'Bandstructure'
        if has_data_with(what, self.f) is False:
            return
        for key in self.f.variables.keys():
            if what in key:
                if 'route' in key:
                    self.wave_functions.route =\
                    self.f.variables[key][:].copy().tostring().decode('utf-8')
                    print(self.wave_functions.route)

    def extract_results(self):
        """
          try to read forces, stress and other stuff
        """
        self.results = X('results')


    def extract_total_energy(self):
        what = 'TotalEnergy'
        self.hamiltonian = X('hamiltonian')
        if has_data_with(what, self.f) is False:
            return
        for key in self.f.variables.keys():
            if what in key:
                if 'finger_print' in key:
                    self.hamiltonian.e_finger_print =\
                    self.f.variables[key][:].copy().tostring().decode('utf-8')
                elif 'Kinetic' in key:
                    self.hamiltonian.e_kin = self.f.variables[key][:].copy()[0]
                elif 'Exchange-Correlation' in key:
                    self.hamiltonian.e_xc = self.f.variables[key][:].copy()[0]
                elif 'External-Field' in key:
                    self.hamiltonian.e_external =\
                            self.f.variables[key][:].copy()[0]
                elif 'Electrostatic' in key:
                    self.hamiltonian.e_hartree = \
                            self.f.variables[key][:].copy()[0]
                elif 'Entropy-Term' in key:
                    self.hamiltonian.e_S = self.f.variables[key][:].copy()[0]
        ham = self.hamiltonian
        ham.e_tot = ham.e_kin + ham.e_xc + ham.e_hartree + ham.e_S

    def extract_common_concepts(self):
        if 'BulkConfiguration_gID000_dimension' in self.f.dimensions.keys():
            self.CommonConcepts.Configurations = X('BulkConfiguration')
        elif 'MoleculeConfiguration_gID000_dimension' in \
                self.f.dimensions.keys():
            self.CommonConcepts.Configurations = X('MoleculeConfiguration')
        else:
            assert 0, 'Not a Bulk or Molecule configurations found!'

        self.atoms = p_conf(self.f, self.CommonConcepts.Configurations.name)

if __name__ == '__main__':
    import sys
    fname = sys.argv[1]
    r = Reader(fname)
    #r.print_keys()
    #print(r.atoms)
    print(r.atk_version)
    print(r.hamiltonian.e_tot)
    print

