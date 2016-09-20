from scipy.io.netcdf import netcdf_file
from configurations import conf_types
from parser_configurations2 import parse_configuration
import re

class Reader:
    def __init__(self, fname):
        self.f = netcdf_file(fname, 'r', mmap=True)
        self.initialize()

    def initialize(self):
        self.conf_names = self.get_configuration_names()
        self.calc_names = self.get_calculator_names()
        self.finger_print_table = self.get_finger_print_table()

    def get_configuration_names(self):
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

    def get_calculator_names(self):
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

    def get_finger_print_table(self):
        table = {}
        if hasattr(self.f, 'fingerprint_table'):
            fpt = fd.fingerprint_table
            for fpg in fpt.split('#')[:-1]:
                fp, g = fpg.split(':')[:2]
                table[g] = fp
        return table

    def get_number_of_configurations(self):
        return len(self.conf_names)

    def get_atoms(self):

if __name__ == '__main__':
    r = Reader('h2.nc')
    print(r.get_configuration_names())
    print(r.get_finger_print_table())
