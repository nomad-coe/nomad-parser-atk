from scipy.io.netcdf import netcdf_file
from configurations import conf_types
from parser_configurations2 import parse_configuration
from parser_calculator import parse_calculator
import re


class Reader:
    def __init__(self, fname):
        self.atoms_x = {} # like {'gID0001': Atoms('H2')}
        self.calculator_x = {} # like {'gID0001': LCAOCalculator}
        self.f = netcdf_file(fname, 'r', mmap=True)
        self.initialize()
        gids = self.calc_names.keys()
        for gid in gids:
            conf_name = self.conf_names[gid]
            calc_name = self.calc_names[gid]
            fpt = self.finger_print_table[gid] # req for for analysis parsing
            self.atoms_x[gid] = parse_configuration(self.f, conf_name)
            self.calculator_x[gid] = parse_calculator(self.f, calc_name)

    def initialize(self):
        """Read the names of the variables in the netcdf file for
           configurations and calculators and setup
           the finger print table which maps between calculated
           quantities and configurations.
        """
        self.atk_version = self.f.version[:].decode('utf-8').split()[-1]
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
        return len(self.conf_names)

    def get_atoms(self, n=-1):
        """ASE atoms for sorted gID's
        """
        key = [key for key in sorted(self.atoms_x.keys(), reverse=True)][n]
        return self.atoms_x[key]

    def get_calculator(self, n=-1):
        """LCAOCalculator for sorted gID's
        """
        key = [key for key in sorted(self.calculator_x.keys(),
                                     reverse=True)][n]
        return self.calculator_x[key]


if __name__ == '__main__':
    import sys
    r = Reader(sys.argv[1])
    for key, value in r.atoms_x.items():
        print(key,value)
    print(r.get_atoms(0))
