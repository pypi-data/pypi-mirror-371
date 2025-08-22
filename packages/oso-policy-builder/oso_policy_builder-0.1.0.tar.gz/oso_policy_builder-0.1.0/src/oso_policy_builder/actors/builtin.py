"""
Built-in actor types
"""

from .base import BaseActor


class User(BaseActor):
    """Built-in User actor - represents individual users"""

    pass


class Group(BaseActor):
    """Built-in Group actor - for ReBAC (Relationship-Based Access Control)"""

    pass
