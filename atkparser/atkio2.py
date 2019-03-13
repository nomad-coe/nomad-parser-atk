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

from copy import copy
from scipy.io.netcdf import netcdf_file
from atkparser.parser_configurations import parse_configuration as p_conf
from atkparser.parser_calculator import parse_calculator as p_calc
import re

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
        print(self.finger_prints)
        self.extract_common_concepts() #  atoms
        self.extract_calculator() # extract the calculator
        self.extract_total_energy() # look for total energy
        self.extract_results()  # look for results, forces, stress etc
        self.extract_wave_functions() # look for eigenvalues, wave functions
        self.extract_bandstructure()  # look for band structures

    def print_keys(self):
        """
            only for debuging
        """
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
        self.calculators = []
        for configuration in self.configurations:
            self.calculators.append(p_calc(self.f, configuration))

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
        #configurations could also be extraced from fingerprint_table
        self.configurations = []
        self.configurations_gIDs = []
        pm = re.compile('MoleculeConfiguration(?P<gid>_gID[0-9][0-9][0-9])$')
        pb = re.compile('BulkConfiguration(?P<gid>_gID[0-9][0-9][0-9])$')
        for key in self.f.variables.keys():
            for p in [pm, pb]:
                s = re.search(p, key)
                if s is not None:
                    self.configurations_gIDs.append(s.group('gid'))
                    self.configurations.append(s.group())
        self.configurations_atoms = []
        for conf in self.configurations:
            self.configurations_atoms.append(p_conf(self.f, conf))

if __name__ == '__main__':
    import sys
    fname = sys.argv[1]
    r = Reader(fname)
    #r.print_keys()
    #print(r.atoms)
    print(r.atk_version)
    print(r.hamiltonian.e_tot)
    print(r.calculators)
    print(r.configurations_atoms)
    print(r.configurations_atoms)

