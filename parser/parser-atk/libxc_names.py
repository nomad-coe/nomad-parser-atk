from __future__ import print_function

short_names = {
        'LDA': 'LDA_X+LDA_C_PW',
        'PW91': 'GGA_X_PW91+GGA_C_PW91',
        'PBE': 'GGA_X_PBE+GGA_C_PBE',
        'PBEsol': 'GGA_X_PBE_SOL+GGA_C_PBE_SOL',
        'revPBE': 'GGA_X_PBE_R+GGA_C_PBE',
        'RPBE': 'GGA_X_RPBE+GGA_C_PBE',
        'BLYP': 'GGA_X_B88+GGA_C_LYP',
        'HCTH407': 'GGA_XC_HCTH_407',
        'WC': 'GGA_X_WC+GGA_C_PBE',
        'AM05': 'GGA_X_AM05+GGA_C_AM05',
        # 'M06-L': 'MGGA_X_M06_L+MGGA_C_M06_L',
        # 'TPSS': 'MGGA_X_TPSS+MGGA_C_TPSS',
        # 'revTPSS': 'MGGA_X_REVTPSS+MGGA_C_REVTPSS',
        'mBEEF': 'MGGA_X_MBEEF+GGA_C_PBE_SOL'}


def get_libxc_name(name):
    if name in short_names:
        libxc_name = short_names[name]
    else:
        libxc_name = name
    return libxc_name


if __name__ == '__main__':
    print(get_libxc_name('LDA'))
    print(get_libxc_name('GGA_X_PBE'))
