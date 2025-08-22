"""
Decorators for defining custom attributes and rules
"""

from collections.abc import Callable

from ..core.expressions import AttributeCondition
from ..core.registry import get_registry


def attribute(actor_class: type):
    """Decorator to define custom attributes on actor classes"""

    def decorator(func: Callable) -> Callable:
        attribute_name = func.__name__

        # Execute the function to get the condition
        condition = func(actor_class)

        # Register the Polar rule
        registry = get_registry()
        actor_name = getattr(actor_class, "_actor_name", actor_class.__name__)
        rule_head = f"{attribute_name}({actor_name.lower()}: {actor_name})"
        registry.add_custom_rule(rule_head, str(condition))

        # Create a method that returns the right condition for different contexts
        def attribute_method(actor_class: str = None) -> AttributeCondition:
            return AttributeCondition(attribute_name, "actor")

        setattr(actor_class, attribute_name, classmethod(attribute_method))
        return attribute_method

    return decorator
