#
# Copyright The NOMAD Authors.
#
# This file is part of NOMAD. See https://nomad-lab.eu for further info.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import pytest

from nomad.datamodel import EntryArchive
from atkparser import ATKParser


def approx(value, abs=0, rel=1e-6):
    return pytest.approx(value, abs=abs, rel=rel)


@pytest.fixture(scope='module')
def parser():
    return ATKParser()


def test_scf(parser):
    archive = EntryArchive()
    parser.parse('tests/data/Si2.nc', archive, None)

    sec_run = archive.section_run[0]
    assert sec_run.program_version == 'ATK 2016.0.3'

    sec_method = sec_run.section_method[0]
    assert sec_method.smearing_width == 300
    assert sec_method.section_XC_functionals[1].XC_functional_name == 'LDA_C_PZ'

    sec_system = sec_run.section_system[0]
    assert sec_system.lattice_vectors[1][0].magnitude == approx(2.7153e-10)
    assert sec_system.atom_positions[1][0].magnitude == approx(1.35765e-10)
    assert sec_system.atom_labels == ['Si', 'Si']

    sec_scc = sec_run.section_single_configuration_calculation[0]
    assert sec_scc.energy_total.magnitude == approx(-5.73249938e-17)
    assert sec_scc.energy_XC.magnitude == approx(-3.41975673e-17)
