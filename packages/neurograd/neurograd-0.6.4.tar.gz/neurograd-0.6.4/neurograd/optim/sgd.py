from .optimizer import Optimizer
from typing import Generator, Tuple
import neurograd as ng
from neurograd import Tensor, xp
import numpy as real_numpy

if xp is real_numpy:
    conditional_fuse = lambda f: f
else:
    from cupy import fuse
    conditional_fuse = fuse

@conditional_fuse
def fused_sgd_step(param, grad, momentum, lr, beta):
    # Update momentum and parameter in one fused kernel
    momentum[:] = beta * momentum + (1 - beta) * grad
    param[:] -= lr * momentum
    return param


class SGD(Optimizer):
    """
    Stochastic Gradient Descent (SGD) optimizer.
    """

    def __init__(self, model_parameters: Generator[Tuple[str, Tensor], None, None], lr: float = 0.01,
                 beta: float = 0.0, weight_decay: float = 0.0) -> None:
        """
        Initializes the SGD optimizer.

        Args:
            model_parameters (Generator[Tuple[str, Tensor]]): Named parameters of the model to optimize.
            lr (float): Learning rate for the optimizer.
            beta (float): Momentum factor for the optimizer.
            weight_decay (float): Weight decay factor for the optimizer (L2/Ridge).
        """
        super().__init__(model_parameters, lr, weight_decay)
        self.momentum = [(name, xp.zeros_like(param.data)) for name, param in self.params]
        self.beta = beta

    def step(self) -> None:
        """
        Performs a single optimization step.
        """
        for i, (name, param) in enumerate(self.params):
            if param.requires_grad and param.grad is not None:
                
                momentum_value = self.momentum[i][1]
                     
                # Weight decay fused with grad (in-place)
                if self.weight_decay > 0:
                    xp.add(param.grad, self.weight_decay * param.data, out=param.grad)
                
                # Fused momentum + parameter update
                param.data = fused_sgd_step(param.data, param.grad, momentum_value, self.lr, self.beta)


    def state_dict(self) -> dict:
        return {
            "lr": self.lr,
            "beta": self.beta,
            "weight_decay": self.weight_decay,
            "params": self.params,
            "momentum": self.momentum,
        }

    def load_state_dict(self, state_dict: dict) -> None:
        self.lr = state_dict["lr"]
        self.beta = state_dict["beta"]
        self.weight_decay = state_dict["weight_decay"]
        self.params = state_dict["params"]
        self.momentum = state_dict["momentum"]
    
    def __repr__(self) -> str:
        return f"SGD(lr={self.lr}, beta={self.beta}, weight_decay={self.weight_decay})."
    
    def __str__(self) -> str:
        return f"SGD with learning rate {self.lr} and beta {self.beta} and weight decay {self.weight_decay}."
