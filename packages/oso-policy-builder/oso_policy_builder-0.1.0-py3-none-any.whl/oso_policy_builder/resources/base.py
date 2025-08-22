"""
Base Resource class and metaclass
"""

from ..core.expressions import AttributeCondition
from ..core.registry import ResourceMeta


class Resource(metaclass=ResourceMeta):
    """Base class for all resources"""

    @classmethod
    def has_attribute(
        cls, attribute_name: str, resource_var: str = "resource"
    ) -> AttributeCondition:
        """Create a method call condition"""
        return AttributeCondition(attribute_name, resource_var)
