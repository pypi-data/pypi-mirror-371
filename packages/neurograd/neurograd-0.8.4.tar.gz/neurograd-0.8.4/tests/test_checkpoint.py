import os
import numpy as np
import neurograd as ng
from neurograd.nn.layers.linear import Linear
from neurograd.optim.sgd import SGD


def test_save_and_load_checkpoint_roundtrip(tmp_path):
    # Build a tiny model with deterministic parameters
    model = Linear(4, 3, use_bias=True)
    # Overwrite params with deterministic values
    model.weight.data[:] = ng.xp.arange(12, dtype=model.weight.data.dtype).reshape(4, 3)
    model.bias.data[:] = ng.xp.array([0.1, 0.2, 0.3], dtype=model.bias.data.dtype)

    opt = SGD(model.named_parameters(), lr=0.01, beta=0.9, weight_decay=0.01)

    ckpt_path = tmp_path / "checkpoint_ng.pth"

    # Save explicit dict-style checkpoint
    ng.save({
        'model_state': model.state_dict(),
        'optimizer_state': opt.state_dict()
    }, str(ckpt_path))

    # Create a fresh model/optimizer with different params
    model2 = Linear(4, 3, use_bias=True)
    # Make sure different values
    model2.weight.data[:] = 0
    model2.bias.data[:] = 0
    opt2 = SGD(model2.named_parameters(), lr=0.0)  # different hyperparams to ensure load works

    # Load checkpoint and restore
    ckpt = ng.load(str(ckpt_path))
    assert "model_state" in ckpt
    assert "optimizer_state" in ckpt

    model2.load_state_dict(ckpt["model_state"])
    opt2.load_state_dict(ckpt["optimizer_state"])

    # Compare weights
    sd1 = model.state_dict()
    sd2 = model2.state_dict()
    for k in sd1:
        assert np.allclose(sd1[k], sd2[k])


def test_save_with_dict_style(tmp_path):
    model = Linear(2, 2, use_bias=True)
    model.weight.data[:] = ng.xp.array([[1.0, 2.0], [3.0, 4.0]], dtype=model.weight.data.dtype)
    model.bias.data[:] = ng.xp.array([0.5, -0.5], dtype=model.bias.data.dtype)

    # Explicit dict-style save using ng.save
    path = tmp_path / "checkpoint_dict.pth"
    ng.save({"model_state": model.state_dict()}, str(path))

    ckpt = ng.load(str(path))
    assert "model_state" in ckpt

    # Load into a new model
    model_new = Linear(2, 2, use_bias=True)
    model_new.load_state_dict(ckpt["model_state"])
    for k, v in model.state_dict().items():
        assert np.allclose(v, model_new.state_dict()[k])
