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

from __future__ import division
from contextlib import contextmanager
import numpy as np
import logging
from ase import units
from ase.data import chemical_symbols
from atkparser.atkio import Reader
from ase.data import atomic_masses
from nomadcore.unit_conversion.unit_conversion import convert_unit as cu
from atkparser.libxc_names import get_libxc_xc_names


@contextmanager
def open_section(p, name):
    gid = p.openSection(name)
    yield gid
    p.closeSection(name, gid)


def c(value, unit=None):
    """ Dummy function for unit conversion"""
    return cu(value, unit)


parser_info = {"name": "parser_atk", "version": "1.0"}


class ATKParserWrapper():
    """ A proper class envolop for running this parser using nomad-FAIRDI infra. """
    def __init__(self, backend, **kwargs):
        self.backend_factory = backend

    def parse(self, mainfile):
        logging.info('ATK parser started')
        logging.getLogger('nomadcore').setLevel(logging.WARNING)
        backend = self.backend_factory('atk.nomadmetainfo.json')
        parse_without_class(mainfile, backend)
        return backend


def parse_without_class(filename, backend):
    p = backend
    o = open_section

    r = Reader(filename)
    indices = range(r.get_number_of_calculators())
    for index in indices:
        r.c = r.get_calculator(index)
        if r.c is None:
            return backend
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
                #p.addValue('scf_threshold_energy_change',
                #           c(r.c.c.iteration_control_parameters.
                #             tolerance, 'eV')) # eV / electron
                p.addValue('x_atk_density_convergence_criterion',
                           r.c.iteration_control_parameters.tolerance)

                samp_c = np.array(
                    (r.c.numerical_accuracy_parameters.k_point_sampling.na,
                     r.c.numerical_accuracy_parameters.k_point_sampling.nb,
                     r.c.numerical_accuracy_parameters.k_point_sampling.nc))
                p.addArrayValues('x_atk_monkhorstpack_sampling', samp_c)
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
                        if hasattr(r.c._wave_functions, 'occupations'):
                            p.addArrayValues('eigenvalues_occupation',
                                              r.c._wave_functions.occupations)
                        if hasattr(r.c._wave_functions, 'ibz_kpts'):
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
        return p

    logging.getLogger('nomadcore').warn('no known calculator found, maybe not a ATK file?')
    with o(p, 'section_run'):
        p.addValue('program_name', 'ATK')
        p.addValue('program_version', r.atk_version)
    return p
