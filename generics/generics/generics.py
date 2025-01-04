# Copyright (c) 2024 Contributors
# Authors: Christian Smith; John Azariah
# All rights reserved.

from types import NoneType
from typing import TypeVar, _GenericAlias
from abc import ABCMeta


# Define a custom metaclass to handle type annotations
class TypeAnnotatedMeta(ABCMeta):
    def __new__(mcls, name, bases, namespace, **kwargs):
        """Create a merged list of type variables from all base classes and __orig_bases__."""
        cls = super().__new__(mcls, name, bases, namespace, **kwargs)

        # Collect type variables from all base classes and __orig_bases__
        type_vars = []

        # Base classes will have `__parameters__` if they are generic and declare type variables.
        for base in bases:
            if hasattr(base, "__parameters__") and base.__parameters__:
                type_vars.extend(base.__parameters__)

        # `__orig_bases__` will exist in the namespace during class creation to track the generic arguments.
        if "__orig_bases__" in namespace:
            for orig_base in namespace["__orig_bases__"]:
                if hasattr(orig_base, "__args__") and orig_base.__args__:
                    type_vars.extend(arg for arg in orig_base.__args__ if isinstance(arg, TypeVar))

        # Remove duplicates and assign to __parameters__
        cls.__parameters__ = tuple(dict.fromkeys(type_vars))  # Preserve order, remove duplicates
        return cls

    def __getitem__(cls, types):
        # Ensure item is a tuple (for multiple type parameters)
        if not isinstance(types, tuple):
            types = (types,)

        # Validate all type parameters (ignore TypeVar instances)
        for typ in types:
            if not isinstance(typ, (type, TypeVar, _GenericAlias, NoneType)):
                raise TypeError(f"Type annotations must be types, not {type(typ).__name__}")

        # Dynamically create a new subclass with class-level properties for type parameters
        type_var_names = [tvar.__name__ for tvar in cls.__parameters__]

        if (len(type_var_names) != len(types)):
            raise TypeError("Number of type arguments must match the number of type parameters")

        # Create the Annotated class dynamically
        class Annotated(cls):
            __type_parameters__ = dict(zip(type_var_names, types))

            # Dynamically add class-level properties for each type parameter
            for name, value in zip(type_var_names, types):
                setattr(cls, name, value)

            def __repr__(self):
                params = ", ".join(
                    f"{name}={typ.__name__ if hasattr(typ, '__name__') else typ}"
                    for name, typ in self.__type_parameters__.items()
                )
                return f"{cls.__name__}[{params}]"

        for name, value in zip(type_var_names, types):
            setattr(Annotated, name, value)

        return Annotated

    @classmethod
    def validate_generic(cls):
        """
        Ensure the class has valid type arguments.

        Raises:
            TypeError: If the generic type is not properly specialized.
        """
        if not cls.__type_params__:
            raise TypeError(f"{cls.__name__} must be specialized with concrete types.")
