"""
Helper functions for building compound conditions
"""

from ..core.expressions import (
    AndCondition,
    HasPermissionCondition,
    HasRoleCondition,
    NotCondition,
    OrCondition,
    PolarCondition,
)


def has_role(role: str, resource_var: str = "resource") -> HasRoleCondition:
    """Create a has_role condition"""
    return HasRoleCondition(role, resource_var)


def has_permission(permission: str, resource_var: str = "resource") -> HasPermissionCondition:
    """Create a has_permission condition"""
    return HasPermissionCondition(permission, resource_var)


def not_(condition: PolarCondition) -> NotCondition:
    """Create a not condition"""
    return NotCondition(condition)


def and_(*conditions: PolarCondition) -> PolarCondition:
    """Combine multiple conditions with AND"""
    if len(conditions) == 0:
        raise ValueError("and_() requires at least one condition")
    elif len(conditions) == 1:
        return conditions[0]
    elif len(conditions) == 2:
        return AndCondition(conditions[0], conditions[1])
    else:
        # Chain multiple conditions: a and b and c
        result = conditions[0]
        for condition in conditions[1:]:
            result = AndCondition(result, condition)
        return result


def or_(*conditions: PolarCondition) -> PolarCondition:
    """Combine multiple conditions with OR"""
    if len(conditions) == 0:
        raise ValueError("or_() requires at least one condition")
    elif len(conditions) == 1:
        return conditions[0]
    elif len(conditions) == 2:
        return OrCondition(conditions[0], conditions[1])
    else:
        # Chain multiple conditions: a or b or c
        result = conditions[0]
        for condition in conditions[1:]:
            result = OrCondition(result, condition)
        return result


def _analyze_variable_usage(condition_str: str, actor_name: str, resource_name: str) -> dict:
    import re

    return {
        "actor_used": bool(re.search(rf"\b{actor_name}\b", condition_str)),
        "resource_used": bool(re.search(rf"\b{resource_name}\b", condition_str)),
    }
