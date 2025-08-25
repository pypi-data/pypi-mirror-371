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


import numpy as np

from pepflow import expression_manager as exm
from pepflow import pep as pep
from pepflow import point, scalar, utils


def test_scalar_add_tag():
    pep_builder = pep.PEPBuilder()
    with pep_builder.make_context("test"):
        s1 = scalar.Scalar(is_basis=True, eval_expression=None, tags=["s1"])
        s2 = scalar.Scalar(is_basis=True, eval_expression=None, tags=["s2"])

        s_add = s1 + s2
        assert s_add.tag == "s1+s2"

        s_add = s1 + 0.1
        assert s_add.tag == "s1+0.1"

        s_radd = 0.1 + s1
        assert s_radd.tag == "0.1+s1"

        s_sub = s1 - s2
        assert s_sub.tag == "s1-s2"

        s_sub = s1 - (s2 + s1)
        assert s_sub.tag == "s1-(s2+s1)"

        s_sub = s1 - (s2 - s1)
        assert s_sub.tag == "s1-(s2-s1)"

        s_sub = s1 - 0.1
        assert s_sub.tag == "s1-0.1"

        s_rsub = 0.1 - s1
        assert s_rsub.tag == "0.1-s1"


def test_scalar_mul_tag():
    pep_builder = pep.PEPBuilder()
    with pep_builder.make_context("test"):
        s = scalar.Scalar(is_basis=True, eval_expression=None, tags=["s"])

        s_mul = s * 0.1
        assert s_mul.tag == "s*0.1"

        s_rmul = 0.1 * s
        assert s_rmul.tag == "0.1*s"

        s_neg = -s
        assert s_neg.tag == "-s"

        s_truediv = s / 0.1
        assert s_truediv.tag == "1/0.1*s"


def test_scalar_add_and_mul_tag():
    pep_builder = pep.PEPBuilder()
    with pep_builder.make_context("test"):
        s1 = scalar.Scalar(is_basis=True, eval_expression=None, tags=["s1"])
        s2 = scalar.Scalar(is_basis=True, eval_expression=None, tags=["s2"])

        s_add_mul = (s1 + s2) * 0.1
        assert s_add_mul.tag == "(s1+s2)*0.1"

        s_add_mul = s1 + s2 * 0.1
        assert s_add_mul.tag == "s1+s2*0.1"

        s_neg_add = -(s1 + s2)
        assert s_neg_add.tag == "-(s1+s2)"

        s_rmul_add = 0.1 * (s1 + s2)
        assert s_rmul_add.tag == "0.1*(s1+s2)"


def test_scalar_hash_different():
    pep_builder = pep.PEPBuilder()
    with pep_builder.make_context("test"):
        s1 = scalar.Scalar(is_basis=True, eval_expression=None)
        s2 = scalar.Scalar(is_basis=True, eval_expression=None)
    assert s1.uid != s2.uid


def test_scalar_tag():
    pep_builder = pep.PEPBuilder()
    with pep_builder.make_context("test"):
        s1 = scalar.Scalar(is_basis=True, eval_expression=None)
        s1.add_tag(tag="my_tag")
    assert s1.tags == ["my_tag"]
    assert s1.tag == "my_tag"


def test_scalar_repr():
    pep_builder = pep.PEPBuilder()
    with pep_builder.make_context("test"):
        s1 = scalar.Scalar(is_basis=True, tags=["s1"])
        print(s1)  # it should be fine without tag
        s1.add_tag("my_tag")
        assert str(s1) == "my_tag"


def test_scalar_in_a_list():
    pep_builder = pep.PEPBuilder()
    with pep_builder.make_context("test"):
        s1 = scalar.Scalar(is_basis=True, eval_expression=None)
        s2 = scalar.Scalar(is_basis=True, eval_expression=None)
        s3 = scalar.Scalar(is_basis=True, eval_expression=None)
    assert s1 in [s1, s2]
    assert s3 not in [s1, s2]


def test_expression_manager_on_basis_scalar():
    pep_builder = pep.PEPBuilder()
    with pep_builder.make_context("test") as ctx:
        s1 = scalar.Scalar(is_basis=True, eval_expression=None, tags=["s1"])
        s2 = scalar.Scalar(is_basis=True, eval_expression=None, tags=["s2"])
        pm = exm.ExpressionManager(ctx)

        np.testing.assert_allclose(pm.eval_scalar(s1).vector, np.array([1, 0]))
        np.testing.assert_allclose(pm.eval_scalar(s2).vector, np.array([0, 1]))

        s3 = scalar.Scalar(is_basis=True, eval_expression=None, tags=["s3"])  # noqa: F841
        pm = exm.ExpressionManager(ctx)

        np.testing.assert_allclose(pm.eval_scalar(s1).vector, np.array([1, 0, 0]))
        np.testing.assert_allclose(pm.eval_scalar(s2).vector, np.array([0, 1, 0]))


def test_expression_manager_eval_scalar():
    pep_builder = pep.PEPBuilder()
    with pep_builder.make_context("test") as ctx:
        s1 = scalar.Scalar(is_basis=True, tags=["s1"])
        s2 = scalar.Scalar(is_basis=True, tags=["s2"])
        s3 = 2 * s1 + s2 / 4 + 5
        s4 = s3 + s1
        s5 = s4 + 5

        p1 = point.Point(is_basis=True, tags=["p1"])
        p2 = point.Point(is_basis=True, tags=["p2"])
        s6 = p1 * p2

        p3 = point.Point(is_basis=True, tags=["p3"])
        p4 = point.Point(is_basis=True, tags=["p4"])
        s7 = 5 * p3 * p4

        s8 = s6 + s7

        pm = exm.ExpressionManager(ctx)

    np.testing.assert_allclose(pm.eval_scalar(s3).vector, np.array([2, 0.25]))
    np.testing.assert_allclose(pm.eval_scalar(s3).constant, 5)
    np.testing.assert_allclose(pm.eval_scalar(s4).vector, np.array([3, 0.25]))
    np.testing.assert_allclose(pm.eval_scalar(s5).vector, np.array([3, 0.25]))
    np.testing.assert_allclose(pm.eval_scalar(s5).constant, 10)

    np.testing.assert_allclose(pm.eval_point(p1).vector, np.array([1, 0, 0, 0]))
    np.testing.assert_allclose(pm.eval_point(p2).vector, np.array([0, 1, 0, 0]))
    np.testing.assert_allclose(pm.eval_point(p3).vector, np.array([0, 0, 1, 0]))
    np.testing.assert_allclose(pm.eval_point(p4).vector, np.array([0, 0, 0, 1]))

    np.testing.assert_allclose(
        pm.eval_scalar(s6).matrix,
        np.array(
            [
                [0.0, 0.5, 0.0, 0.0],
                [0.5, 0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, 0.0],
            ]
        ),
    )
    np.testing.assert_allclose(
        pm.eval_scalar(s7).matrix,
        np.array(
            [
                [0.0, 0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, 2.5],
                [0.0, 0.0, 2.5, 0.0],
            ]
        ),
    )

    np.testing.assert_allclose(
        pm.eval_scalar(s8).matrix,
        np.array(
            [
                [0.0, 0.5, 0.0, 0.0],
                [0.5, 0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, 2.5],
                [0.0, 0.0, 2.5, 0.0],
            ]
        ),
    )


def test_constraint():
    pep_builder = pep.PEPBuilder()
    with pep_builder.make_context("test") as ctx:
        s1 = scalar.Scalar(is_basis=True, tags=["s1"])
        s2 = scalar.Scalar(is_basis=True, tags=["s2"])
        s3 = 2 * s1 + s2 / 4 + 5

        c1 = s3.le(5, name="c1")
        c2 = s3.lt(5, name="c2")
        c3 = s3.ge(5, name="c3")
        c4 = s3.gt(5, name="c4")
        c5 = s3.eq(5, name="c5")

        pm = exm.ExpressionManager(ctx)

    np.testing.assert_allclose(pm.eval_scalar(c1.scalar).vector, np.array([2, 0.25]))
    np.testing.assert_allclose(pm.eval_scalar(c1.scalar).constant, 0)
    assert c1.comparator == utils.Comparator.LT

    np.testing.assert_allclose(pm.eval_scalar(c2.scalar).vector, np.array([2, 0.25]))
    np.testing.assert_allclose(pm.eval_scalar(c2.scalar).constant, 0)
    assert c2.comparator == utils.Comparator.LT

    np.testing.assert_allclose(pm.eval_scalar(c3.scalar).vector, np.array([2, 0.25]))
    np.testing.assert_allclose(pm.eval_scalar(c3.scalar).constant, 0)
    assert c3.comparator == utils.Comparator.GT

    np.testing.assert_allclose(pm.eval_scalar(c4.scalar).vector, np.array([2, 0.25]))
    np.testing.assert_allclose(pm.eval_scalar(c4.scalar).constant, 0)
    assert c4.comparator == utils.Comparator.GT

    np.testing.assert_allclose(pm.eval_scalar(c5.scalar).vector, np.array([2, 0.25]))
    np.testing.assert_allclose(pm.eval_scalar(c5.scalar).constant, 0)
    assert c5.comparator == utils.Comparator.EQ
