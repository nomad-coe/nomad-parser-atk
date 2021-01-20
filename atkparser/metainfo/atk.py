#
# Copyright The NOMAD Authors.
#
# This file is part of NOMAD.
# See https://nomad-lab.eu for further info.
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
import numpy as np            # pylint: disable=unused-import
import typing                 # pylint: disable=unused-import
from nomad.metainfo import (  # pylint: disable=unused-import
    MSection, MCategory, Category, Package, Quantity, Section, SubSection, SectionProxy,
    Reference
)
from nomad.metainfo.legacy import LegacyDefinition

from nomad.datamodel.metainfo import public

m_package = Package(
    name='atk_nomadmetainfo_json',
    description='None',
    a_legacy=LegacyDefinition(name='atk.nomadmetainfo.json'))


class section_method(public.section_method):

    m_def = Section(validate=False, extends_base_section=True, a_legacy=LegacyDefinition(name='section_method'))

    x_atk_density_convergence_criterion = Quantity(
        type=np.dtype(np.float64),
        shape=[],
        description='''
        Density convergence criteria to break the SCF cycle
        ''',
        a_legacy=LegacyDefinition(name='x_atk_density_convergence_criterion'))

    x_atk_mix_old = Quantity(
        type=np.dtype(np.int32),
        shape=[],
        description='''
        Number of old densities in the density mixer
        ''',
        a_legacy=LegacyDefinition(name='x_atk_mix_old'))

    x_atk_mix_weight = Quantity(
        type=np.dtype(np.float64),
        shape=[],
        description='''
        Mixing weight in density mixer
        ''',
        a_legacy=LegacyDefinition(name='x_atk_mix_weight'))

    x_atk_monkhorstpack_sampling = Quantity(
        type=np.dtype(np.int32),
        shape=[3],
        description='''
        Monkhorstpack grid sampling
        ''',
        a_legacy=LegacyDefinition(name='x_atk_monkhorstpack_sampling'))


m_package.__init_metainfo__()
