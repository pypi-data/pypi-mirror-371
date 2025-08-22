"""
Registry for tracking actors, resources, and rules
"""

from dataclasses import dataclass
from typing import Any


@dataclass
class PolarRule:
    """Represents a generated Polar rule"""

    head: str
    body: str = ""
    rule_type: str = "custom"
    resource_type: str = ""

    def __str__(self) -> str:
        if self.rule_type == "shorthand":
            return f'"{self.head}" if "{self.body}";'
        elif self.rule_type == "relation":
            return f"{self.head};"
        elif self.body and self.body != "true":
            return f"{self.head} if {self.body};"
        else:
            return f"{self.head};"


class PolicyRegistry:
    """Registry to track all policy rules and types"""

    def __init__(self):
        self.actors: dict[str, type] = {}
        self.resources: dict[str, dict[str, Any]] = {}
        self.rules: list[PolarRule] = []
        self.facts: list[str] = []
        self.global_info: dict[str, Any] = {"roles": [], "permissions": [], "class": None}
        self._group_enabled = False  # tracks if we added the RBAC group inheritance rule
        self._nested_groups_enabled = False

    def add_custom_rule(self, head: str, body: str):
        """Add a custom rule that goes after resource blocks"""
        rule = PolarRule(head=head, body=body, rule_type="custom_rule", resource_type="")
        self.rules.append(rule)

    def add_global_rule(self, head: str, body: str = ""):
        """Add a rule that goes in the global block"""
        rule = PolarRule(head=head, body=body, rule_type="global", resource_type="")
        self.rules.append(rule)

    def add_global_inheritance_rule(self, local_role: str, global_role: str, resource_type: str):
        """Add global role inheritance rule: 'local_role' if global 'global_role'"""
        rule = PolarRule(
            head=f'"{local_role}"',
            body=f'global "{global_role}"',
            rule_type="shorthand",
            resource_type=resource_type,
        )
        self.rules.append(rule)

    def add_shorthand_rule(self, head: str, body: str, resource_type: str):
        """Add a shorthand rule that goes inside a resource block"""
        rule = PolarRule(head=head, body=body, rule_type="shorthand", resource_type=resource_type)
        self.rules.append(rule)

    def add_relation_rule(self, rule_text: str, resource_type: str):
        """Add a relation-based rule that goes inside a resource block"""
        rule = PolarRule(head=rule_text, body="", rule_type="relation", resource_type=resource_type)
        self.rules.append(rule)

    def add_resource_rule(self, head: str, body: str, resource_type: str):
        """Add a complex rule that goes inside a resource block"""
        rule = PolarRule(
            head=head, body=body, rule_type="resource_rule", resource_type=resource_type
        )
        self.rules.append(rule)

    def add_group_inheritance_rule(self):
        """Add the group inheritance rule if not already added"""
        if self._group_enabled:
            return

        rule = PolarRule(
            head="has_role(user: User, role: String, resource: Resource)",
            body=(
                "group matches Group and "
                "has_group(user, group) and "
                "has_role(group, role, resource)"),
            rule_type="custom",
        )
        self.rules.append(rule)
        self._group_enabled = True

    def add_nested_groups_rule(self):
        """Add the nested groups rule if not already added"""
        if self._nested_groups_enabled:
            return

        rule = PolarRule(
            head="has_group(user: User, group: Group)",
            body="g matches Group and has_group(user, g) and has_group(g, group)",
            rule_type="custom",
        )
        self.rules.append(rule)
        self._nested_groups_enabled = True

    def clear(self):
        """Clear all registered data"""
        self.actors.clear()
        self.resources.clear()
        self.rules.clear()
        self.facts.clear()
        self._group_enabled = False


# Global registry instance
_registry = PolicyRegistry()


def get_registry() -> PolicyRegistry:
    """Get the global policy registry"""
    return _registry


class ActorMeta(type):
    """Metaclass for Actor classes"""

    def __new__(cls, name: str, bases: tuple, attrs: dict):
        # Create the class
        new_class = super().__new__(cls, name, bases, attrs)

        new_class._actor_name = name

        return new_class


def register_actor(actor_class):
    """Register an actor class when it's first used"""
    name = getattr(actor_class, "_actor_name", actor_class.__name__)
    if name not in _registry.actors:
        _registry.actors[name] = actor_class


class ResourceMeta(type):
    """Metaclass for Resource classes"""

    def __new__(cls, name: str, bases: tuple, attrs: dict, **kwargs):
        # Extract from class attributes first, then fall back to metaclass params
        permissions = attrs.get("permissions", kwargs.get("permissions", []))
        roles = attrs.get("roles", kwargs.get("roles", []))
        relations = attrs.get("relations", kwargs.get("relations", {}))
        polar_name = attrs.get("_polar_name", kwargs.get("polar_name", name.lower()))

        # Set defaults
        if permissions is None:
            permissions = []
        if roles is None:
            roles = []
        if relations is None:
            relations = {}
        if polar_name is None:
            polar_name = name.lower()

        # Store as class attributes
        attrs["_permissions"] = permissions
        attrs["_roles"] = roles
        attrs["_relations"] = relations
        attrs["_polar_name"] = polar_name

        # Create the class
        new_class = super().__new__(cls, name, bases, attrs)

        # Register if not base class
        if name not in ("Resource", "BaseResource"):
            _registry.resources[name] = {
                "class": new_class,
                "permissions": permissions,
                "roles": roles,
                "relations": relations,
                "polar_name": polar_name,
            }

        return new_class


class GlobalMeta(type):
    """Metaclass for Global class"""

    def __new__(cls, name: str, bases: tuple, attrs: dict):
        roles = attrs.get("roles", [])
        permissions = attrs.get("permissions", [])

        new_class = super().__new__(cls, name, bases, attrs)

        if name == "Global":
            _registry.global_info = {"roles": roles, "permissions": permissions, "class": new_class}

        return new_class
