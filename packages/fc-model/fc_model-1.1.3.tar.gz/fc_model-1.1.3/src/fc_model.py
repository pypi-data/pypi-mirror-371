from __future__ import annotations
import json
import os
from typing import Any, TypedDict, List, Dict, Union, Optional
from numpy.typing import NDArray

from numpy import dtype, int32, int64, float64

from fc_blocks import *
from fc_conditions import *
from fc_constraint import *
from fc_coordinate_system import *
from fc_data import *
from fc_materials import *
from fc_mesh import *
from fc_property_tables import *
from fc_receivers import *
from fc_set import *
from fc_value import *


class FCHeader(TypedDict):
    binary: bool
    description: str
    version: int
    types: Dict[str, int]


__all__ = [
    # Ключевой API
    'FCModel',
    # Доменные классы
    'FCMesh', 
    'FCBlock', 
    'FCPropertyTable', 
    'FCCoordinateSystem', 
    'FCConstraint', 
    'FCElement', 
    'FCElementType', 
    'FCMaterial', 
    'FCLoad', 
    'FCRestraint', 
    'FCInitialSet', 
    'FCReceiver', 
    'FCSet', 
    'FCDependencyColumn',
    'FCValue',
    'FCData',
    'FCHeader',
    'FCMaterialPropertiesTypeLiteral', 
    'FCMaterialProperty', 
    # Константы
    'FC_DEPENDENCY_TYPES_KEYS', 
    'FC_DEPENDENCY_TYPES_CODES', 
    'FC_INITIAL_SET_TYPES_CODES', 
    'FC_INITIAL_SET_TYPES_KEYS', 
    'FC_LOADS_TYPES_CODES', 
    'FC_LOADS_TYPES_KEYS', 
    'FC_MATERIAL_PROPERTY_NAMES_CODES', 
    'FC_MATERIAL_PROPERTY_NAMES_KEYS', 
    'FC_MATERIAL_PROPERTY_TYPES_CODES', 
    'FC_MATERIAL_PROPERTY_TYPES_KEYS',
    'FC_RESTRAINT_FLAGS_CODES', 
    'FC_RESTRAINT_FLAGS_KEYS'
    'FC_ELEMENT_TYPES_KEYID', 
    'FC_ELEMENT_TYPES_KEYNAME', 
]

