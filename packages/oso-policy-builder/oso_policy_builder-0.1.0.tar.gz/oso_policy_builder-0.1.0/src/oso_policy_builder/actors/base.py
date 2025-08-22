"""
Base Actor class and metaclass
"""

from ..core.builders import RuleBuilder, WithRoleBuilder
from ..core.expressions import (
    HasPermissionCondition,
    HasRelationCondition,
    HasRoleCondition,
    InListCondition,
    MatchesCondition,
    PolarCondition,
)
from ..core.registry import ActorMeta
from ..utils.helpers import and_


class BaseActor(metaclass=ActorMeta):
    """Base class for all actors"""

    @classmethod
    def can(cls, permission: str) -> RuleBuilder:
        """Start building a permission rule"""
        return RuleBuilder(cls, permission)

    @classmethod
    def with_role(cls, role: str) -> WithRoleBuilder:
        """Start building role-based permissions"""
        return WithRoleBuilder(cls, role)

    @classmethod
    def has_role(cls, role: str, resource_name: str = "resource") -> HasRoleCondition:
        """Create a has_role condition"""
        return HasRoleCondition(role=role, resource_name=resource_name)

    @classmethod
    def has_permission(
        cls, permission: str, resource_var: str = "resource"
    ) -> HasPermissionCondition:
        """Create a has_permission condition"""
        return HasPermissionCondition(permission, resource_var)

    @classmethod
    def has_relation(cls, relation: str, resource_var: str = "resource") -> HasRelationCondition:
        """Create a has_permission condition"""
        return HasRelationCondition(relation, resource_var)

    @classmethod
    def has_role_in(cls, roles: list[str], actor_var: str = None) -> PolarCondition:
        """Check if actor has any role in the given list"""
        if actor_var is None:
            actor_var = cls.__name__.lower()

        # Generate: role matches String and role in [...] and has_role(user, role)
        return and_(
            MatchesCondition("role", "String"),
            InListCondition("role", roles),
            HasRoleCondition("", actor_var, None),  # has_role(user, role)
        )
