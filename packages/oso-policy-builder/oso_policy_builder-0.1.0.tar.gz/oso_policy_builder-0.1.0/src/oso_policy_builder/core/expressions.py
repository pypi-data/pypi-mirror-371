from __future__ import annotations


class PolarCondition:
    """Base class for Polar conditions"""

    def __str__(self) -> str:
        raise NotImplementedError(f"{self.__class__.__name__} must implement __str__() method")

    def and_(self, other: PolarCondition) -> AndCondition:
        """Logical AND - use .and_() method"""
        return AndCondition(self, other)

    def or_(self, other: PolarCondition) -> OrCondition:
        """Logical OR - use .or_() method"""
        return OrCondition(self, other)


class HasRoleCondition(PolarCondition):
    def __init__(self, role: str, actor_name: str = "actor", resource_name: str = "resource"):
        self.role = role
        self.actor_name = actor_name
        self.resource_name = resource_name

    def __str__(self) -> str:
        if self.role:  # Fixed role
            if self.resource_name == "resource":
                return f'has_role({self.actor_name}, "{self.role}", {self.resource_name})'
            else:
                return f'has_role({self.actor_name}, "{self.role}")'
        else:  # Variable role - for has_role(user, role)
            return f"has_role({self.actor_name}, role)"


class HasPermissionCondition(PolarCondition):
    """Represents has_permission(actor, permission, resource) condition"""

    def __init__(self, permission: str, resource_var: str = "resource"):
        self.permission = permission
        self.resource_var = resource_var

    def __str__(self) -> str:
        return f'has_permission(actor, "{self.permission}", {self.resource_var})'


class HasRelationCondition(PolarCondition):
    """Represents has_relation(actor, relation, resource) condition"""

    def __init__(self, relation: str, resource_var: str = "resource"):
        self.relation = relation
        self.resource_var = resource_var

    def __str__(self) -> str:
        return f'has_relation(actor, "{self.relation}", {self.resource_var})'


class AttributeCondition(PolarCondition):
    """Represents resource.method() calls"""

    def __init__(self, method: str, resource_var: str = "resource"):
        self.method = method
        self.resource_var = resource_var

    def __str__(self) -> str:
        # Generate proper Polar method call syntax
        return f"{self.method}({self.resource_var})"


class NotCondition(PolarCondition):
    """Represents not(...) condition"""

    def __init__(self, condition: PolarCondition):
        self.condition = condition

    def __str__(self) -> str:
        return f"not ({self.condition})"


class AndCondition(PolarCondition):
    """Represents condition1 and condition2"""

    def __init__(self, left: PolarCondition, right: PolarCondition):
        self.left = left
        self.right = right

    def __str__(self) -> str:
        return f"{self.left} and {self.right}"


class OrCondition(PolarCondition):
    """Represents condition1 or condition2"""

    def __init__(self, left: PolarCondition, right: PolarCondition):
        self.left = left
        self.right = right

    def __str__(self) -> str:
        return f"({self.left}) or ({self.right})"


class MatchesCondition(PolarCondition):
    def __init__(self, var_name: str, var_type: str):
        self.var_name = var_name
        self.var_type = var_type

    def __str__(self) -> str:
        return f"{self.var_name} matches {self.var_type}"


class InListCondition(PolarCondition):
    def __init__(self, var_name: str, values: list):
        self.var_name = var_name
        self.values = values

    def __str__(self) -> str:
        values_str = ", ".join(f'"{v}"' for v in self.values)
        return f"{self.var_name} in [{values_str}]"
