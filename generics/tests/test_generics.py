# Copyright (c) 2024 Contributors
# Authors: Christian Smith; John Azariah
# All rights reserved.

import pytest
from typing import Generic, TypeVar
from abc import ABC, abstractmethod

import sys
import pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from generics.generics import TypeAnnotatedMeta

# Define TypeVars for use with Generic
T = TypeVar("T")
U = TypeVar("U")
V = TypeVar("V")
W = TypeVar("W")


# Example of a generic class
class MyGeneric(Generic[T, U], metaclass=TypeAnnotatedMeta):
    pass


def test_missing_type_arguments():
    with pytest.raises(TypeError):
        MyGeneric[int]


def test_no_specialization():
    with pytest.raises(TypeError):
        MyGeneric.validate_generic()


def test_class_property_access():
    assert MyGeneric[int, str].T is int
    assert MyGeneric[int, str].U is str


def test_typealias_class_property_access():
    RuntimeGeneric = MyGeneric[int, str]

    assert RuntimeGeneric.T is int
    assert RuntimeGeneric.U is str


def test_instance_property_access():
    instance = MyGeneric[float, bool]()

    assert instance.T is float
    assert instance.U is bool


def test_abc_integration():
    class SpecializedABC(MyGeneric[int, str], ABC):
        pass

    assert SpecializedABC.T is int
    assert SpecializedABC.U is str
    assert issubclass(SpecializedABC, ABC)


# Tests for accessing type parameter values
def test_single_type_parameter():
    class MyClass(Generic[T], metaclass=TypeAnnotatedMeta):
        pass

    assert MyClass[int].T == int, "Type parameter T should be int"


def test_multiple_type_parameters():
    class MyClass(Generic[T, U], metaclass=TypeAnnotatedMeta):
        pass
    assert MyClass[float, str].T == float, "Type parameter T should be float"
    assert MyClass[float, str].U == str, "Type parameter U should be str"


def test_invalid_type_annotation():
    class MyClass(Generic[T], metaclass=TypeAnnotatedMeta):
        pass

    with pytest.raises(TypeError, match="Type annotations must be types, not str"):
        MyClass[f'some_{str}_type']


def test_mismatched_type_arguments():
    class MyClass(Generic[T, U], metaclass=TypeAnnotatedMeta):
        pass

    with pytest.raises(TypeError, match="Number of type arguments must match the number of type parameters"):
        MyClass[int]


def test_generic_abstract_type():
    class MyClass(ABC, Generic[T, U], metaclass=TypeAnnotatedMeta):
        @abstractmethod
        def abstract_method(self):
            pass

    assert MyClass[int, str].T == int, "Type parameter T should be int"
    assert MyClass[int, str].U == str, "Type parameter U should be str"


def test_concrete_subclass_of_generic_abstract_type():
    class MyClass(ABC, Generic[T, U], metaclass=TypeAnnotatedMeta):
        @abstractmethod
        def abstract_method(self):
            pass

    class ConcreteClass(MyClass[int, str]):
        def abstract_method(self):
            return "Implemented"

    instance = ConcreteClass()
    assert instance.T == int, "Type parameter T should be int"
    assert instance.U == str, "Type parameter U should be str"
    assert instance.abstract_method() == "Implemented", "Abstract method should be callable and return the correct value"


def test_deep_inheritance_with_type_parameters():
    class MyClass(ABC, Generic[T, U], metaclass=TypeAnnotatedMeta):
        @abstractmethod
        def abstract_method(self):
            pass

    class BaseClass(MyClass[int, str]):
        def abstract_method(self):
            return "Base implementation"

    class SubClass(BaseClass):
        def abstract_method(self):
            return "SubClass implementation"

    base_instance = BaseClass()
    assert base_instance.T == int, "BaseClass type parameter T should be int"
    assert base_instance.U == str, "BaseClass type parameter U should be str"
    assert base_instance.abstract_method() == "Base implementation", \
        "BaseClass method should return correct value"

    sub_instance = SubClass()
    assert sub_instance.T == int, "SubClass type parameter T should be int"
    assert sub_instance.U == str, "SubClass type parameter U should be str"
    assert sub_instance.abstract_method() == "SubClass implementation", \
        "SubClass method should return correct value"


def test_inheriting_from_multiple_generic_base_classes():
    class MyClass(Generic[T, U], ABC, metaclass=TypeAnnotatedMeta):
        def abstract_method(self):
            raise NotImplementedError("Subclasses must implement this method")

    class AnotherClass(Generic[V, W], ABC, metaclass=TypeAnnotatedMeta):
        pass

    class CombinedClass(MyClass[int, str], AnotherClass[float, bool]):
        def abstract_method(self):
            return "CombinedClass implementation"

    instance = CombinedClass()
    assert instance.T == int, "Type parameter T should be int"
    assert instance.U == str, "Type parameter U should be str"
    assert instance.V == float, "Type parameter V should be float"
    assert instance.W == bool, "Type parameter W should be bool"
    assert instance.abstract_method() == "CombinedClass implementation", \
        "Abstract method should be callable and return the correct value"


def test_multiple_base_classes_with_shared_generic_typevars():
    class BaseClass1(Generic[T]):
        pass

    class BaseClass2(Generic[T]):
        pass

    class CombinedClass(BaseClass1[int], BaseClass2[int]):
        pass

    instance = CombinedClass()
    assert isinstance(instance, BaseClass1), "Instance should be a subclass of BaseClass1"
    assert isinstance(instance, BaseClass2), "Instance should be a subclass of BaseClass2"


def test_generic_with_no_typevars():
    class MyClass(ABC, Generic[T, U], metaclass=TypeAnnotatedMeta):
        @abstractmethod
        def abstract_method(self):
            pass

    class NonGenericBase:
        pass

    class CombinedClass(MyClass[int, str], NonGenericBase):
        def abstract_method(self):
            return "NonGeneric implementation"

    instance = CombinedClass()
    assert instance.T == int, "Type parameter T should be int"
    assert instance.U == str, "Type parameter U should be str"


def test_generic_subclass_with_generic_base():
    class BaseClass(Generic[T, U], metaclass=TypeAnnotatedMeta):
        pass

    class SubClass(BaseClass[V, V]):
        pass

    class ConcreteClass(SubClass[int, int]):
        pass

    assert ConcreteClass.T == int
    assert ConcreteClass.U == int
    assert SubClass[int, int].T == int
    assert SubClass[int, int].U == int
    assert BaseClass[int, int].T == int
    assert BaseClass[int, int].U == int
