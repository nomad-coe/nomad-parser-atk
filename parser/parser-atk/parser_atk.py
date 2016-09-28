from __future__ import division
import os
from contextlib import contextmanager
import numpy as np
from ase import units
from ase.data import chemical_symbols
from atkio import Reader
from scipy.io.netcdf import netcdf_file
from ase.data import atomic_masses
from ase.units import Rydberg
import setup_paths
from nomadcore.unit_conversion.unit_conversion import convert_unit as cu
from nomadcore.local_meta_info import loadJsonFile, InfoKindEl
from nomadcore.parser_backend import JsonParseEventsWriterBackend
from libxc_names import get_libxc_name


@contextmanager
def open_section(p, name):
    gid = p.openSection(name)
    yield gid
    p.closeSection(name, gid)


def c(value, unit=None):
    """ Dummy function for unit conversion"""
    return value
    return cu(value, unit)


parser_info = {"name": "parser_atk", "version": "1.0"}
path = '../../../../nomad-meta-info/meta_info/nomad_meta_info/' +\
        'atk.nomadmetainfo.json'
metaInfoPath = os.path.normpath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), path))

metaInfoEnv, warns = loadJsonFile(filePath=metaInfoPath,
                                  dependencyLoader=None,
                                  extraArgsHandling=InfoKindEl.ADD_EXTRA_ARGS,
                                  uri=None)


def parse(filename):
    p = JsonParseEventsWriterBackend(metaInfoEnv)
    o = open_section
    r = Reader(filename) #  Reader(filename)
    index = 0 # need to loop over index at some point if more that one conf per
              # file
    r.calculator = r.get_calculator(index)
    r.atoms = r.get_atoms(index)
    p.startedParsingSession(filename, parser_info)
    with o(p, 'section_run'):
        p.addValue('program_name', 'ATK')
        p.addValue('program_version', r.atk_version)
        p.addValue('program_basis_set_type', 'numeric AOs')
        with o(p, 'section_basis_set_atom_centered'):
            p.addValue('basis_set_atom_centered_short_name',
                       'ATK LCAO basis')
        with o(p, 'section_system') as system_gid:
            p.addArrayValues('simulation_cell',
                             c(r.atoms.cell, 'angstrom'))
            symbols = np.array([chemical_symbols[z] for z in r.atoms.numbers])
            p.addArrayValues('atom_labels', symbols)
            p.addArrayValues('atom_positions', c(r.atoms.positions, 'angstrom'))
            p.addArrayValues('configuration_periodic_dimensions',
                             np.array(r.atoms.pbc, bool))
            if hasattr(r.atoms, 'momenta'):
                masses = atomic_masses[r.atoms.numbers]
                velocities = r.atoms.momenta / masses.reshape(-1, 1)
                p.addArrayValues('atom_velocities',
                                c(velocities * units.fs / units.Angstrom,
                                  'angstrom/femtosecond'))
        with o(p, 'section_sampling_method'):
            p.addValue('ensemble_type', 'NVE')
        with o(p, 'section_frame_sequence'):
            pass
        with o(p, 'section_method') as method_gid:
            p.addValue('relativity_method', 'pseudo_scalar_relativistic')
            p.addValue('electronic_structure_method', 'DFT')
            #p.addValue('scf_threshold_energy_change',
            #           c(r.convergence.scf_energy, 'eV')) # eV / electron
            p.addValue('smearing_kind', 'fermi')
            p.addRealValue('smearing_width',
                           c(r.calculator.numerical_accuracy_parameters.\
                             electron_temperature, 'K'))
            p.addRealValue('total_charge', r.calculator.charge)
            with o(p, 'section_XC_functionals'):
                p.addValue('XC_functional_name',
                           get_libxc_name(r.calculator.exchange_correlation))
        with o(p, 'section_single_configuration_calculation'):
            p.addValue('single_configuration_calculation_to_system_ref',
                       system_gid)
            p.addValue('single_configuration_to_calculation_method_ref',
                       method_gid)
#            p.addValue('single_configuration_calculation_converged',
#                      r.scf.converged)
#            p.addRealValue('energy_total',
#                           c(r.hamiltonian.e_tot_extrapolated, 'eV'))
            p.addRealValue('energy_free',
                           c(r.hamiltonian.e_tot, 'eV'))
            p.addRealValue('energy_XC', c(r.hamiltonian.e_xc, 'eV'))
            p.addRealValue('electronic_kinetic_energy',
                           c(r.hamiltonian.e_kin, 'eV'))
            p.addRealValue('energy_correction_entropy',
                           c(r.hamiltonian.e_S, 'eV'))
#            p.addRealValue('energy_reference_fermi',
#                          c(r.occupations.fermilevel, 'eV'))
            if hasattr(r.results, 'forces'):
                p.addArrayValues('atom_forces_free_raw',
                                 c(r.results.forces, 'eV/angstrom'))
            #if hasattr(r.results, 'magmoms'):
            #    p.addArrayValues('x_gpaw_magnetic_moments',
            #                     r.results.magmoms)
            #    p.addRealValue('x_atk_spin_Sz', r.results.magmoms.sum() / 2.0)
            if hasattr(r.wave_functions, 'eigenvalues'):
                with o(p, 'section_eigenvalues'):
                    p.addValue('eigenvalues_kind', 'normal')
                    p.addArrayValues('eigenvalues_values',
                                     c(r.wave_functions.eigenvalues, 'eV'))
                    p.addArrayValues('eigenvalues_occupation',
                                     r.wave_functions.occupations)
                    p.addArrayValues('eigenvalues_kpoints',
                                     r.wave_functions.ibz_kpts)
            if hasattr(r.wave_functions, 'band_paths'):
                with o(p, 'section_k_band'):
                    for band_path in r.wave_functions.band_paths:
                        with o(p, 'section_k_band_segment'):
                            p.addArrayValues('band_energies',
                                            c(band_path.eigenvalues, 'eV'))
                            p.addArrayValues('band_k_points', 'eV',
                                             band_path.kpoints)
                            p.addArrayValues('band_segm_labels',
                                            band_path.labels)
                            p.addArrayValues('band_segm_start_end',
                                             np.asarray(
                                                 [band_path.kpoints[0],
                                                  band_path.kpoints[-1]]))


    p.finishedParsingSession("ParseSuccess", None)

if __name__ == '__main__':
    import sys
    filename = sys.argv[1]
    parse(filename)
