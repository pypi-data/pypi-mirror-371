import math

from pepflow import function, pep
from pepflow import pep_context as pc


def test_gd_e2e():
    ctx = pc.PEPContext("gd").set_as_current()
    pep_builder = pep.PEPBuilder()
    eta = 1
    N = 9

    f = pep_builder.declare_func(function.SmoothConvexFunction, L=1)
    f.add_tag("f")
    x = pep_builder.set_init_point("x_0")
    x_star = f.add_stationary_point("x_star")
    pep_builder.set_initial_constraint(
        ((x - x_star) ** 2).le(1, name="initial_condition")
    )

    # We first build the algorithm with the largest number of iterations.
    for i in range(N):
        x = x - eta * f.gradient(x)
        x.add_tag(f"x_{i + 1}")

    # To achieve the sweep, we can just update the performance_metric.
    for i in range(1, N + 1):
        p = ctx.get_by_tag(f"x_{i}")
        pep_builder.set_performance_metric(
            f.function_value(p) - f.function_value(x_star)
        )
        result = pep_builder.solve()
        expected_opt_value = 1 / (4 * i + 2)
        assert math.isclose(result.primal_opt_value, expected_opt_value, rel_tol=1e-3)
