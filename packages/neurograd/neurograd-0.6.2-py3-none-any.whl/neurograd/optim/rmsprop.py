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
def fused_rmsprop_step(param, grad, sq_avg, lr, beta, eps):
    # Update running average of squared gradients and parameter in one kernel
    sq_avg[:] = beta * sq_avg + (1 - beta) * grad * grad
    param[:] -= lr * grad / (xp.sqrt(sq_avg) + eps)
    return param


class RMSprop(Optimizer):
    """
    RMSprop optimizer.
    """

    def __init__(self, model_parameters: Generator[Tuple[str, Tensor], None, None], lr: float = 0.01,
                 beta: float = 0.99, eps: float = 1e-8, weight_decay: float = 0.0) -> None:
        """
        Initializes the RMSprop optimizer.

        Args:
            model_parameters (Generator[Tuple[str, Tensor]]): Named parameters of the model to optimize.
            lr (float): Learning rate for the optimizer.
            beta (float): Smoothing constant for squared gradient moving average.
            eps (float): Small value to prevent division by zero.
            weight_decay (float): Weight decay factor for the optimizer (L2/Ridge).
        """
        super().__init__(model_parameters, lr, weight_decay)
        self.momentum = [(name, xp.zeros_like(param.data)) for name, param in self.params]
        self.beta = beta
        self.eps = eps

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
                
                # Fused squared-average + parameter update
                param.data = fused_rmsprop_step(param.data, param.grad, momentum_value, self.lr, self.beta, self.eps)

    
    def state_dict(self) -> dict:
        return {
            "lr": self.lr,
            "beta": self.beta,
            "eps": self.eps,
            "weight_decay": self.weight_decay,
            "params": self.params,
            "momentum": self.momentum,
        }

    def load_state_dict(self, state_dict: dict) -> None:
        self.lr = state_dict["lr"]
        self.beta = state_dict["beta"]
        self.eps = state_dict["eps"]
        self.weight_decay = state_dict["weight_decay"]
        self.params = state_dict["params"]
        self.momentum = state_dict["momentum"]
    
    def __repr__(self) -> str:
        return f"RMSprop(lr={self.lr}, beta={self.beta}, eps={self.eps}, weight_decay={self.weight_decay})."
    
    def __str__(self) -> str:
        return f"RMSprop with learning rate {self.lr}, beta {self.beta}, eps {self.eps}, and weight decay {self.weight_decay}."
