# Copyright: 2025 The PEPFlow Developers
#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

from __future__ import annotations

import enum
import numbers
from typing import TYPE_CHECKING, Any

import numpy as np

if TYPE_CHECKING:
    from pepflow.function import Function
    from pepflow.point import Point
    from pepflow.scalar import Scalar


def SOP(v, w):
    """Symmetric Outer Product."""
    return 1 / 2 * (np.outer(v, w) + np.outer(w, v))


def SOP_self(v):
    return SOP(v, v)


class Op(enum.Enum):
    ADD = "add"
    SUB = "sub"
    MUL = "mul"
    DIV = "div"


class Comparator(enum.Enum):
    GT = "GT"
    LT = "LT"
    EQ = "EQ"


def is_numerical(val: Any) -> bool:
    return isinstance(val, numbers.Number)


def parenthesize_tag(val: Point | Scalar | Function) -> str:
    tmp_tag = val.tag
    if not val.is_basis:
        if val.eval_expression.op == Op.ADD or val.eval_expression.op == Op.SUB:
            tmp_tag = f"({val.tag})"
    return tmp_tag
