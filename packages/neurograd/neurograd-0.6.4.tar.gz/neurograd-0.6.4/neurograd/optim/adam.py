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
def fused_adam_step(param, grad, m, v, lr, beta1, beta2, epsilon, t):
    # Update biased first and second moment estimates
    m[:] = beta1 * m + (1 - beta1) * grad
    v[:] = beta2 * v + (1 - beta2) * grad * grad
    # Compute bias-corrected moments
    m_hat = m / (1 - beta1 ** t)
    v_hat = v / (1 - beta2 ** t)
    # Parameter update
    param[:] -= lr * m_hat / (xp.sqrt(v_hat) + epsilon)
    return param



class Adam(Optimizer):
    """
    Adam optimizer with momentum and adaptive learning rate.
    This optimizer combines the benefits of AdaGrad and RMSProp, and is well-suited for a wide range of problems.
    """

    def __init__(self, model_parameters: Generator[Tuple[str, Tensor], None, None], lr: float = 0.01,
                 beta1: float = 0.9, beta2: float = 0.999, epsilon: float = 1e-8,
                 weight_decay: float = 0.0) -> None:
        """
        Initializes the Adam optimizer.

        Args:
            model_parameters (Generator[Tuple[str, Tensor]]): Named parameters of the model to optimize.
            lr (float): Learning rate for the optimizer.
            beta1 (float): Exponential decay rate for the first moment estimate.
            beta2 (float): Exponential decay rate for the second moment estimate.
            epsilon (float): Small value to prevent division by zero.
            weight_decay(float): Weight decay factor for the optimizer (L2/Ridge).
        """
        super().__init__(model_parameters, lr, weight_decay)
        self.first_momentum = [(name, xp.zeros_like(param.data)) for name, param in self.params]
        self.second_momentum = [(name, xp.zeros_like(param.data)) for name, param in self.params]
        self.beta1 = beta1
        self.beta2 = beta2
        self.epsilon = epsilon
        self.t = 0


    def step(self) -> None:
        self.t += 1
        for i, (name, param) in enumerate(self.params):
            if param.requires_grad and param.grad is not None:
                m = self.first_momentum[i][1]
                v = self.second_momentum[i][1]
                # Weight decay before momentum updates
                if self.weight_decay > 0:
                    xp.add(param.grad, self.weight_decay * param.data, out=param.grad)
                # Update moments and parameters
                param.data = fused_adam_step(param.data, param.grad, m, v, self.lr,
                                             self.beta1, self.beta2, self.epsilon, self.t)

    
    def state_dict(self) -> dict:
        return {
            "lr": self.lr,
            "beta1": self.beta1,
            "beta2": self.beta2,
            "epsilon": self.epsilon,
            "weight_decay": self.weight_decay,
            "params": self.params,
            "first_momentum": self.first_momentum,
            "second_momentum": self.second_momentum
        }

    def load_state_dict(self, state_dict: dict) -> None:
        self.lr = state_dict["lr"]
        self.beta1 = state_dict["beta1"]
        self.beta2 = state_dict["beta2"]
        self.epsilon = state_dict["epsilon"]
        self.weight_decay = state_dict["weight_decay"]
        self.params = state_dict["params"]
        self.first_momentum = state_dict["first_momentum"]
        self.second_momentum = state_dict["second_momentum"]

    def __repr__(self) -> str:
        return f"Adam(lr={self.lr}, beta1={self.beta1}, beta2={self.beta2}, epsilon={self.epsilon}, weight_decay={self.weight_decay})."

    def __str__(self) -> str:
        return f"Adam with learning rate {self.lr}, beta1 {self.beta1}, beta2 {self.beta2}, epsilon {self.epsilon}, and weight decay {self.weight_decay}."
