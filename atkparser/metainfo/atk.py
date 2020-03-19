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
