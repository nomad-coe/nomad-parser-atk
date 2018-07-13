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

from __future__ import print_function
import re
p = re.compile(
      '((?P<x_name>(GGA|LDA|MGGA|HF|HYB_MGGA)_X.*)|(?P<c_name>(GGA|LDA|MGGA)_C.*))')

short_names = {
        'LDA.RPA': 'LDA_X+LDA_C_RPA',
        'LDA.PZ': 'LDA_X+LDA_C_PZ',
        'LDA.PW': 'LDA_X+LDA_C_PW',
        'GGA.PW91': 'GGA_X_PW91+GGA_C_PW91',
        'GGA.PBE': 'GGA_X_PBE+GGA_C_PBE',
        'GGA.PBES': 'GGA_X_PBE_SOL+GGA_C_PBE_SOL',
        'GGA.RPBE': 'GGA_X_RPBE+GGA_C_PBE',
        'BLYP': 'GGA_X_B88+GGA_C_LYP',
        'HCTH407': 'GGA_XC_HCTH_407',
        'WC': 'GGA_X_WC+GGA_C_PBE',
        'AM05': 'GGA_X_AM05+GGA_C_AM05',
        'mBEEF': 'MGGA_X_MBEEF+GGA_C_PBE_SOL'}


def get_libxc_name(name):
    if name in short_names:
        libxc_name = short_names[name]
    else:
        libxc_name = name
    return libxc_name


def get_libxc_xc_names(name):
    """get dictionary with
       x_name: Exchange name (None if xc_name is not None)
       c_name: Correlation name (-||-)
       xc_name: XC name
    """
    name = get_libxc_name(name)
    xc = {'xc_name': None,
          'x_name' : None,
          'c_name': None}

    if '_XC_' in name:
        xc['xc_name'] = name
        return xc

    if '+' in name:
        s = name.split('+')
        xc['x_name'] = s[0]
        xc['c_name'] = s[1]
        return xc

    m = re.search(p, name)
    if m is not None: # it is either a correlation or exchange functional
        xc.update(m.groupdict())
        return xc

    xc['xc_name'] = name  # for something like BEEF-vdW
    return xc


if __name__ == '__main__':
    print(get_libxc_xc_names('LDA.PZ'))
    print(get_libxc_xc_names('LDA_X'))
    print(get_libxc_xc_names('GGA_X_PBE'))
