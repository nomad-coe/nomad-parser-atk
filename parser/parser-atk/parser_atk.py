from __future__ import division
import os
from contextlib import contextmanager
import numpy as np
from ase import units
from ase.data import chemical_symbols
from atkio import Reader
from ase.data import atomic_masses
import setup_paths
from nomadcore.unit_conversion.unit_conversion import convert_unit as cu
from nomadcore.local_meta_info import loadJsonFile, InfoKindEl
from nomadcore.parser_backend import JsonParseEventsWriterBackend
from libxc_names import get_libxc_xc_names


@contextmanager
def open_section(p, name):
    gid = p.openSection(name)
    yield gid
    p.closeSection(name, gid)


def c(value, unit=None):
    """ Dummy function for unit conversion"""
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
    r = Reader(filename)
    indices = range(r.get_number_of_calculators())
    for index in indices:
        r.c = r.get_calculator(index)
        if r.c is None:
            return
        r.atoms = r.get_atoms(index)

        p = JsonParseEventsWriterBackend(metaInfoEnv)
        o = open_section
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
                symbols = np.array([chemical_symbols[z] for z in
                                    r.atoms.numbers])
                p.addArrayValues('atom_labels', symbols)
                p.addArrayValues('atom_positions', c(r.atoms.positions,
                                                     'angstrom'))
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
                # p.addValue('scf_threshold_energy_change',
                #           c(r.convergence.scf_energy, 'eV')) # eV / electron
                p.addValue('smearing_kind', 'fermi')
                p.addRealValue('smearing_width',
                               c(r.c.numerical_accuracy_parameters.
                                 electron_temperature, 'K'))
                p.addRealValue('total_charge', r.c.charge)

                xc_names = get_libxc_xc_names(r.c.exchange_correlation)
                for name in xc_names.values():
                    if name is not None:
                        with o(p, 'section_XC_functionals'):
                            p.addValue('XC_functional_name', name)

            with o(p, 'section_single_configuration_calculation'):
                p.addValue('single_configuration_calculation_to_system_ref',
                           system_gid)
                p.addValue('single_configuration_to_calculation_method_ref',
                           method_gid)
    #            p.addValue('single_configuration_calculation_converged',
    #                      r.scf.converged)
    #            p.addRealValue('energy_total',
    #                           c(r.hamiltonian.e_tot_extrapolated, 'eV'))
                if hasattr(r.c._hamiltonian, 'e_kin'):
                    p.addRealValue('energy_free',
                                   c(r.c._hamiltonian.e_total_free, 'eV'))
                    p.addRealValue('energy_XC', c(r.c._hamiltonian.e_xc, 'eV'))
                    p.addRealValue('electronic_kinetic_energy',
                                   c(r.c._hamiltonian.e_kin, 'eV'))
                    p.addRealValue('energy_correction_entropy',
                                   c(r.c._hamiltonian.e_entropy, 'eV'))
        #            p.addRealValue('energy_reference_fermi',
    #                          c(r.occupations.fermilevel, 'eV'))
                if hasattr(r.c._results, 'forces'):
                    p.addArrayValues('atom_forces_free_raw',
                                     c(r.c._results.forces, 'eV/angstrom'))
                #if hasattr(r.results, 'magmoms'):
                #    p.addArrayValues('x_gpaw_magnetic_moments',
                #                     r.results.magmoms)
                #    p.addRealValue('x_atk_spin_Sz',
                #                    r.results.magmoms.sum() / 2.0)
                if hasattr(r.c._wave_functions, 'eigenvalues'):
                    with o(p, 'section_eigenvalues'):
                        p.addValue('eigenvalues_kind', 'normal')
                        p.addArrayValues('eigenvalues_values',
                                         c(r.c._wave_functions.eigenvalues,
                                           'eV'))
                        p.addArrayValues('eigenvalues_occupation',
                                         r.c._wave_functions.occupations)
                        p.addArrayValues('eigenvalues_kpoints',
                                         r.c._wave_functions.ibz_kpts)
                if hasattr(r.c._wave_functions, 'band_paths'):
                    with o(p, 'section_k_band'):
                        for band_path in r.wave_functions.band_paths:
                            with o(p, 'section_k_band_segment'):
                                p.addArrayValues('band_energies',
                                                 c(band_path.eigenvalues,
                                                   'eV'))
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
