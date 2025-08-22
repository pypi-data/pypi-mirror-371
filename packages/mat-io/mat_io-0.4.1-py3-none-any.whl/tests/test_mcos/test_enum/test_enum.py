import os
from enum import Enum

import numpy as np
import pytest

from matio import load_from_mat


class EnumClass(Enum):
    """Enum class for testing purposes."""

    enum1 = {"val": np.array([1.0]).reshape(1, 1)}
    enum2 = {"val": np.array([2.0]).reshape(1, 1)}
    enum3 = {"val": np.array([3.0]).reshape(1, 1)}
    enum4 = {"val": np.array([4.0]).reshape(1, 1)}
    enum5 = {"val": np.array([5.0]).reshape(1, 1)}
    enum6 = {"val": np.array([6.0]).reshape(1, 1)}


class EnumClass2(Enum):
    """Enum class for testing"""

    enum1 = {"uint32.Data": np.array([1], dtype=np.uint32).reshape(1, 1)}


params_base = [
    (
        np.array(
            [
                [
                    EnumClass.enum1,
                ]
            ]
        ),
        "enum_base",
    ),
    (
        np.array(
            [
                EnumClass.enum1,
                EnumClass.enum2,
                EnumClass.enum3,
                EnumClass.enum4,
                EnumClass.enum5,
                EnumClass.enum6,
            ]
        ).reshape(2, 3, order="F"),
        "enum_arr",
    ),
    (
        np.array(
            [
                [
                    EnumClass2.enum1,
                ]
            ]
        ),
        "enum_uint32",
    ),
]


@pytest.mark.parametrize(
    "expected_array, var_name",
    params_base,
    ids=["enum-base-v7", "enum-array-v7", "enum-derived-v7"],
)
def test_enum_load_v7(expected_array, var_name):
    file_path = os.path.join(os.path.dirname(__file__), "test_enum_v7.mat")
    matdict = load_from_mat(file_path, raw_data=False)

    assert var_name in matdict
    assert matdict[var_name].shape == expected_array.shape
    assert matdict[var_name].dtype == expected_array.dtype

    for idx in np.ndindex(expected_array.shape):
        actual_member = matdict[var_name][idx]
        expected_member = expected_array[idx]
        assert actual_member.name == expected_member.name
        assert actual_member.value == expected_member.value


@pytest.mark.parametrize(
    "expected_array, var_name",
    params_base,
    ids=["enum-base-v7.3", "enum-array-v7.3", "enum-derived-v7.3"],
)
def test_enum_load_v73(expected_array, var_name):
    file_path = os.path.join(os.path.dirname(__file__), "test_enum_v73.mat")
    matdict = load_from_mat(file_path, raw_data=False)

    # Output format
    assert var_name in matdict
    assert matdict[var_name].shape == expected_array.shape
    assert matdict[var_name].dtype == expected_array.dtype

    for idx in np.ndindex(expected_array.shape):
        actual_member = matdict[var_name][idx]
        expected_member = expected_array[idx]
        assert actual_member.name == expected_member.name
        assert actual_member.value == expected_member.value
