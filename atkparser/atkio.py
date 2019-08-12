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

from scipy.io.netcdf import netcdf_file
import numpy as np
from ase.units import Hartree
from atkparser.configurations import conf_types
from atkparser.parser_configurations import parse_configuration
from atkparser.parser_calculator import parse_calculator
import re


class Reader:
    def __init__(self, fname):
        self.atoms_x = {}  # like {'gID0001': Atoms('H2')}
        self.calculator_x = {}  # like {'gID0001': LCAOCalculator}
        self._atoms_inp_x = {}  # contains inpyt python code
        self._calculator_inp_x = {}  # contains input python code
        self.conf_names = None
        self.calc_names = None
        self.f = netcdf_file(fname, 'r', mmap=True)

        try:
            # TODO this implementation might causes an error, in current SciPy netcdf_file has no .version
            self.atk_version = self.f.version[:].decode('utf-8').split()[-1]
        except Exception as e:
            self.atk_version = 'unavailable'

        self.read_names()
        for gid in self.calc_names.keys():
            conf_name = self.conf_names[gid]
            calc_name = self.calc_names[gid]
            self.atoms_x[gid] = parse_configuration(self.f, conf_name)
            self.calculator_x[gid] = parse_calculator(self.f, calc_name)
            self._calculator_inp_x[gid] = (self.f.variables[calc_name].data[:].
                                           copy().tostring().decode('utf-8'))
            self._atoms_inp_x[gid] = (self.f.variables[conf_name].data[:].
                                      copy().tostring().decode('utf-8'))

        # setup hamilton, results, wave_functions attr
        # to calculator to hold results (as in GPAW)
        p_etot_fp = r"^(?P<pref>TotalEnergy_gID[0-9]+)_finger_print"
        p_forc_fp = r"^(?P<pref>Forces_gID[0-9]+)_finger_print"
        p_mole_fp = r"^(?P<pref>MolecularEnergySpectrum_gID[0-9]+)_finger_print"

        for gid in self.calc_names.keys():  # loop over calculators
            calc = self.calculator_x[gid]
            calc._hamiltonian = type('Hamiltonian', (object,), {})()
            calc._results = type('Results', (object,), {})()
            calc._wave_functions = type('WaveFunctions', (object,), {})()
            fp = self.finger_print_table[gid]
            v = self.f.variables
            h = calc._hamiltonian
            r = calc._results
            wf = calc._wave_functions
            for name in self.f.variables.keys():
                # calc.hamiltonian.e_x,  x=e_tot, e_kin, ...
                # TotalEnergy object in ATK
                m_fp_etot = re.search(p_etot_fp, name)
                if m_fp_etot is not None:
                    pref = m_fp_etot.group('pref')
                    fp2 = v[pref + '_finger_print'].data[:].copy()
                    fp2 = fp2.tostring().decode('utf-8')
                    pref += '_component_'
                    if fp == fp2:
                        h.e_kin = v[pref + 'Kinetic'].data[:].copy()[0]
                        h.e_coulomb = v[pref +
                                        'Electrostatic'].data[:].copy()[0]
                        h.e_xc = v[pref +
                                   'Exchange-Correlation'].data[:].copy()[0]
                        h.e_entropy = v[pref +
                                        'Entropy-Term'].data[:].copy()[0]
                        h.e_external = v[pref +
                                         'External-Field'].data[:].copy()[0]
                        h.e_total_free = (h.e_kin + h.e_coulomb + h.e_xc +
                                          h.e_entropy + h.e_external)
                    continue
                # calc.results.forces
                m_fp_forc = re.search(p_forc_fp, name)
                if m_fp_forc is not None:
                    pref = m_fp_forc.group('pref')
                    fp2 = v[pref + '_finger_print'].data[:].copy()
                    fp2 = fp2.tostring().decode('utf-8')
                    if fp == fp2:
                        r.forces = v[pref +
                                     '_atom_resolved_forces'].data[:].copy()
                    continue
                m_fp_mole = re.search(p_mole_fp, name)
                if m_fp_mole is not None:
                    pref = m_fp_mole.group('pref')
                    fp2 = v[pref + '_finger_print'].data[:].copy()
                    fp2 = fp2.tostring().decode('utf-8')
                    if fp == fp2:
                        nspin = v[pref + '_number_of_spin'].data[:].copy()[0]
                        nspin = int(nspin)
                        eigs1 = v[pref + '_eigenvalues_up'].data[:].copy()
                        eigs2 = v[pref + '_eigenvalues_up'].data[:].copy()
                        if (v[pref + '_eigenvalues_up'].
                            unit.decode('utf-8') == 'Hartree'):
                            eigs1 *= Hartree
                            eigs2 *= Hartree
                        if nspin == 1:
                            eigenvalues = eigs1.reshape(1, 1, -1)
                        elif nspin == 2:
                            eigenvalues = np.array((eigs1, eigs2))
                            eigenvalues = eigenvalues.reshape(2, 1, -1)
                        wf.eigenvalues = eigenvalues
                    continue

    def read_names(self):
        """Read the names of the variables in the netcdf file for
           configurations and calculators and setup
           the finger print table which maps between calculated
           quantities and configurations.
        """
        # TODO there might be are no ._names in new SciPy version
        try:
            self._names = self.f._names[:].decode('utf-8').split(';')
        except Exception:
            self._names = list(self.f.variables.keys())
        self.conf_names = self._read_configuration_names()
        self.calc_names = self._read_calculator_names()
        self.finger_print_table = self._read_finger_print_table()

    def _read_configuration_names(self):
        """ find the configuration names in the nc files,
        i.e. {'gID001': 'BulkConfiguration_gID001'}
        """
        d = self.f.dimensions
        conf_names = {}
        for k in d.keys():
            for conf_type in conf_types:
                p = conf_type + '(?P<gID>_gID[0-9][0-9][0-9])_dimension'
                m = re.search(p, k)
                if m is not None:
                    g = m.group('gID')
                    conf_names[g[1:]] = conf_type + g
        return conf_names

    def _read_calculator_names(self):
        d = self.f.dimensions
        calc_names = {}
        for k in d.keys():
            for conf_type in conf_types:
                p = conf_type + \
                        '(?P<gID>_gID[0-9][0-9][0-9])_calculator_dimension'
                m = re.search(p, k)
                if m is not None:
                    g = m.group('gID')
                    calc_names[g[1:]] = conf_type + g + '_calculator'
        return calc_names

    def _read_finger_print_table(self):
        table = {}
        if hasattr(self.f, 'fingerprint_table'):
            fpt = self.f.fingerprint_table.decode('utf-8')
            for fpg in fpt.split('#')[:-1]:
                fp, g = fpg.split(':')[:2]
                table[g] = fp
        return table

    def get_number_of_configurations(self):
        return len(self.atoms_x)

    def get_number_of_calculators(self):
        return len(self.calculator_x)

    def get_atoms(self, n=-1):
        """ASE atoms for sorted gID's
        """
        key = [key for key in sorted(self.atoms_x.keys(), reverse=True)][n]
        return self.atoms_x[key]

    def get_calculator(self, n=-1):
        """LCAOCalculator for sorted gID's
        """
        if len(self.calculator_x) == 0:
            return None
        key = [key for key in sorted(self.calculator_x.keys(),
                                     reverse=True)][n]
        return self.calculator_x[key]


if __name__ == '__main__':
    import sys
    r = Reader(sys.argv[1])
    for key, value in r.atoms_x.items():
        print(key, type(value))
    for gid, calc in r.calculator_x.items():
        print(gid, type(calc))
        print(calc._wave_functions.eigenvalues)
#    for key, value in r._calculator_inp_x.items():
#        print(value)
