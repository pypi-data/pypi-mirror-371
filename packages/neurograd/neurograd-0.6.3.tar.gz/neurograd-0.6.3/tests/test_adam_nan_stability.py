import numpy as np

from neurograd.tensor import Tensor
from neurograd.optim.adam import Adam


def simple_quadratic_loss(w: Tensor):
    # f(w) = mean((w - 3)^2)
    return ((w - 3.0) * (w - 3.0)).mean()


def test_adam_does_not_produce_nan_on_simple_quadratic():
    # Initialize parameter
    w = Tensor(np.array([10.0, -5.0, 0.5], dtype=np.float32), requires_grad=True)

    def params_gen():
        yield ("w", w)

    opt = Adam(params_gen(), lr=0.1)

    last_loss = None
    for _ in range(50):
        opt.zero_grad()
        loss = simple_quadratic_loss(w)
        assert not np.isnan(loss.data).any(), "Loss became NaN"
        loss.backward()
        opt.step()
        if last_loss is not None:
            # Should generally not increase wildly on this convex function
            assert loss.data <= last_loss + 1e-3
        last_loss = loss.data

