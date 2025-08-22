"""
Oso Policy Builder - A experimental Pythonic library for building Oso's Polar policies
"""

__version__ = "0.1.0"

# Main exports
from .actors.baseGlobal import BaseGlobal
from .actors.builtin import Group, User
from .core.expressions import PolarCondition
from .core.generator import PolicyBuilder
from .resources.base import Resource
from .utils.decorators import attribute
from .utils.helpers import and_, has_permission, has_role, not_, or_

__all__ = [
    "PolicyBuilder",
    "User",
    "Group",
    "BaseGlobal",
    "Resource",
    "and_",
    "or_",
    "not_",
    "has_role",
    "has_permission",
    "PolarCondition",
    "attribute",
]
