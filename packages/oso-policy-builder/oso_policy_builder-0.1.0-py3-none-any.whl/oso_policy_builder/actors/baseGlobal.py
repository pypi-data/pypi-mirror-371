from ..core.builders import RuleBuilder, WithRoleBuilder
from ..core.registry import GlobalMeta, get_registry


class BaseGlobal(metaclass=GlobalMeta):
    """Global scope for application-wide roles and permissions"""

    @classmethod
    def can(cls, permission: str) -> RuleBuilder:
        """Start building a global permission rule"""
        return RuleBuilder(cls, permission)

    @classmethod
    def with_role(cls, role: str) -> WithRoleBuilder:
        """Start building global role-based permissions"""
        return WithRoleBuilder(cls, role)

    @classmethod
    def define_role_group(cls, group_name: str, roles: list[str]):
        """Define a role group that creates a custom predicate"""
        registry = get_registry()
        registry.add_role_group(group_name, roles)
