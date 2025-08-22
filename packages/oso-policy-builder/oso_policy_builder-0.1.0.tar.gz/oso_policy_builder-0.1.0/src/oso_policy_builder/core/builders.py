"""
Builder classes for constructing permission rules
"""

from typing import TYPE_CHECKING

from ..utils.helpers import _analyze_variable_usage
from .expressions import PolarCondition
from .registry import get_registry, register_actor

if TYPE_CHECKING:
    pass


class RuleBuilder:
    """Builder for creating permission rules"""

    def __init__(self, actor_class: type, permission: str):
        if not self._is_global_class(actor_class):
            register_actor(actor_class)
        self.actor_class = actor_class
        self.permission = permission
        self.is_global = getattr(actor_class, "__name__", "") == "Global"

    def on(self, resource_class: type) -> "ConditionalRuleBuilder":
        """Start building conditional permission"""
        return ConditionalRuleBuilder(self.actor_class, self.permission, resource_class)

    def when(self, condition: PolarCondition) -> "ConditionalRuleBuilder":
        """Allow .when() for global permissions e.g. Global.can({perm}).when({condition})"""
        if not self.is_global:
            raise ValueError("when() without on() is only supported for Global permissions")
        return ConditionalRuleBuilder(self.actor_class, self.permission, None).when(condition)

    def _is_global_class(self, cls):
        """Check if class inherits from BaseGlobal"""
        return any(getattr(base, "__name__", "") == "BaseGlobal" for base in cls.__mro__)


class ConditionalRuleBuilder:
    """Builder for conditional permissions"""

    def __init__(self, actor_class: type, permission: str, resource_class: type):
        self.actor_class = actor_class
        self.permission = permission
        self.resource_class = resource_class
        self.actor_polar_name = getattr(actor_class, "_polar_name", actor_class.__name__.lower())
        if resource_class is not None:
            self.resource_polar_name = getattr(
                resource_class, "_polar_name", resource_class.__name__.lower()
            )
        else:
            self.resource_polar_name = None

    def when(self, condition: PolarCondition) -> "ConditionalRuleBuilder":
        """Add condition using Polar condition objects"""
        registry = get_registry()

        condition_str = str(condition)
        if self.resource_class is None:
            registry.add_global_rule(f'"{self.permission}"', condition_str)
        else:
            if condition_str.startswith('has_role(actor, "') and condition_str.endswith(
                '", resource)'
            ):
                # Extract role from condition like 'has_role(actor, "editor", resource)'
                role = condition_str.split('"')[1]
                registry.add_shorthand_rule(self.permission, role, self.resource_class.__name__)
            else:
                # Complex condition - add as resource rule
                condition_str_for_analysis = condition_str.replace(
                    "actor", self.actor_polar_name
                ).replace("resource", self.resource_polar_name)

                usage = _analyze_variable_usage(
                    condition_str_for_analysis, self.actor_polar_name, self.resource_polar_name
                )

                rule_head = self._generate_smart_rule_head(usage)
                registry.add_resource_rule(
                    rule_head, condition_str_for_analysis, self.resource_class.__name__
                )

        return self

    def _generate_smart_rule_head(self, usage: dict) -> str:
        """Generate rule head with smart parameter detection"""
        actor_param = (
            f"{self.actor_polar_name}: {self.actor_class.__name__}"
            if usage["actor_used"]
            else f"_: {self.actor_class.__name__}"
        )
        permission_param = f'"{self.permission}"'
        resource_param = (
            f"{self.resource_polar_name}: {self.resource_class.__name__}"
            if usage["resource_used"]
            else f"_: {self.resource_class.__name__}"
        )

        return f"has_permission({actor_param}, {permission_param}, {resource_param})"


class WithRoleBuilder:
    """Builder for role-based permissions"""

    def __init__(self, actor_class: type, role: str, source_resource_class: type = None):
        self.actor_class = actor_class
        self.role = role
        self.source_resource_class = source_resource_class
        self.is_global = getattr(actor_class, "__name__", "") == "Global"

    def can(self, *permissions: str) -> "RolePermissionBuilder":
        """Grant permissions to this role"""
        return RolePermissionBuilder(
            self.actor_class, self.role, list(permissions), self.source_resource_class
        )

    def inherits_role(self, inherited_role: str) -> "RoleInheritanceBuilder":
        return RoleInheritanceBuilder(
            self.actor_class, inherited_role, self.role, self.source_resource_class
        )

    def on(self, resource_class: type) -> "WithRoleBuilder":
        """Specify source resource for cross-resource inheritance"""
        return WithRoleBuilder(self.actor_class, self.role, resource_class)


class RolePermissionBuilder:
    """Builder for role-based permission grants"""

    def __init__(
        self,
        actor_class: type,
        role: str,
        permissions: list[str],
        source_resource_class: type = None,
    ):
        self.actor_class = actor_class
        self.role = role
        self.permissions = permissions
        self.source_resource_class = source_resource_class
        self.is_global = getattr(actor_class, "__name__", "") == "Global"

    def can(self, *permissions: str):
        return PermissionGrantBuilder(self, list(permissions))

    def on(self, resource_class: type) -> "RolePermissionBuilder":
        """Grant permissions on any resource of this type - generates shorthand rules"""
        registry = get_registry()

        if self.is_global:
            # Global role inheritance: "internal_admin" if global "admin";
            registry.add_global_inheritance_rule(self.head, self.body, resource_class.__name__)
        else:
            if self.source_resource_class is None:
                # Same-resource: generate shorthand rules
                for permission in self.permissions:
                    registry.add_shorthand_rule(permission, self.role, resource_class.__name__)
            else:
                # Cross-resource: generate relation rules
                source_relation = _find_relation_name(resource_class, self.source_resource_class)
                for permission in self.permissions:
                    rule_text = f'"{permission}" if "{self.role}" on "{source_relation}"'
                    registry.add_relation_rule(rule_text, resource_class.__name__)

        return self


class PermissionGrantBuilder:
    """Handles .can("permission").on(Resource) and allows chaining back"""

    def __init__(self, role_builder: RolePermissionBuilder, permissions: list[str]):
        self.role_builder = role_builder
        self.permissions = permissions

    def on(self, target_resource_class: type) -> RolePermissionBuilder:
        """Grant these permissions on the target resource"""
        registry = get_registry()

        if self.role_builder.source_resource_class is None:
            # Same-resource: generate shorthand rules
            for permission in self.permissions:
                registry.add_shorthand_rule(
                    permission, self.role_builder.role, target_resource_class.__name__
                )
        else:
            # Cross-resource: generate relation rules
            source_relation = _find_relation_name(
                target_resource_class, self.role_builder.source_resource_class
            )
            for permission in self.permissions:
                rule_text = f'"{permission}" if "{self.role_builder.role}" on "{source_relation}"'
                registry.add_relation_rule(rule_text, target_resource_class.__name__)

        # Return the role builder to allow chaining: .can().on().can().on()
        return self.role_builder


class RoleInheritanceBuilder:
    """Builder for role inheritance: {head} if {body}"""

    def __init__(self, actor_class: type, head: str, body: str, source_resource_class: type = None):
        self.actor_class = actor_class
        self.head = head
        self.body = body
        self.source_resource_class = source_resource_class

    def on(self, resource_class: type) -> "RoleInheritanceBuilder":
        """Specify which resource this inheritance applies to"""
        registry = get_registry()
        if self.source_resource_class is None:
            # Same-resource inheritance: "viewer" if "editor";
            registry.add_shorthand_rule(self.head, self.body, resource_class.__name__)
        else:
            # Cross-resource inheritance: "editor" if "editor" on "document";
            source_relation = _find_relation_name(resource_class, self.source_resource_class)
            rule_text = f'"{self.head}" if "{self.body}" on "{source_relation}"'
            registry.add_relation_rule(rule_text, resource_class.__name__)

        return self


def _find_relation_name(target_resource: type, source_resource: type) -> str:  # ADD THIS METHOD
    """
    Find the relation name that connects target to source
    e.g. "doc" in "relations:{doc: Document}"
    """
    registry = get_registry()
    target_name = target_resource.__name__
    source_name = source_resource.__name__

    if target_name in registry.resources:
        relations = registry.resources[target_name]["relations"]
        for rel_name, rel_type in relations.items():
            rel_type_name = getattr(rel_type, "__name__", str(rel_type))
            if rel_type_name == source_name:
                return rel_name

    # Fallback to lowercase source name
    return source_name.lower()


def _is_global_class(self, cls):
    """Check if class inherits from BaseGlobal"""
    return any(getattr(base, "__name__", "") == "BaseGlobal" for base in cls.__mro__)
