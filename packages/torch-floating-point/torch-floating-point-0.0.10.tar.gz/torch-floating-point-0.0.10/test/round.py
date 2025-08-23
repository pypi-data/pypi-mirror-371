import unittest

import torch
from parameterized import parameterized
from torch import FloatTensor, bfloat16, finfo, float8_e4m3fn, float8_e5m2, float16, float32, randn

from floating_point import round
from floating_point.data_types import FloatingPoint
from floating_point.round import Round


class TestRoundFunctionDifferentiability(unittest.TestCase):
    @parameterized.expand([
        ("fp8e5m2", FloatingPoint(1, 5, 2, 16, 8), "cpu"),
        ("fp8e4m3", FloatingPoint(1, 4, 3, 7, 8), "cpu"),
    ] + ([("fp8e5m2", FloatingPoint(1, 5, 2, 16, 8), "cuda"),
          ("fp8e4m3", FloatingPoint(1, 4, 3, 7, 8), "cuda")]
    if torch.cuda.is_available() else []))
    def test_round_differentiability(self, name, data_type, device):
        rounder = Round(data_type)
        x = randn(100, requires_grad=True, device=device)
        x[x < data_type.minimum].fill_(data_type.minimum)
        x[x > data_type.maximum].fill_(data_type.maximum)
        x_val = x.clone().detach().requires_grad_(True)
        z = rounder(x).sum()
        z.backward()
        x_grad_round = x.grad.clone().detach()
        self.assertIsNotNone(x_grad_round, "Gradient is None, the function is not differentiable.")
        self.assertEqual(x_grad_round.shape, x.shape, "Gradient shape incorrect.")
        z = x_val.sum()
        z.backward()
        x_grad_val = x_val.grad.clone().detach()
        self.assertTrue(torch.allclose(x_grad_round, x_grad_val, rtol=1e-5, atol=1e-5), "Gradient mismatch.")

class TestFloatingPointRounding(unittest.TestCase):
    __float8e5m2__ = FloatingPoint(1, 5, 2, 16, 8, reserved_exponent=False)
    __float8e4m3fn__ = FloatingPoint(1, 4, 3, 7, 8, max_mantissa_at_max_exponent=6, reserved_exponent=False)
    __float16__ = FloatingPoint(1, 5, 10, 15, 16)
    __bfloat16__ = FloatingPoint(1, 8, 7, 127, 16)
    __float32__ = FloatingPoint(1, 8, 23, 127, 32)
    @parameterized.expand([
        ("float8e5m2", __float8e5m2__, float8_e5m2, "cpu"),
        ("float8e4m3fn", __float8e4m3fn__, float8_e4m3fn, "cpu"),
        ("float16", __float16__, float16, "cpu"),
        ("bfloat16", __bfloat16__, bfloat16, "cpu"),
        ("float32", __float32__, float32, "cpu"),
    ] + ([("float8e5m2", __float8e5m2__, float8_e5m2, "cuda"),
          ("float8e4m3fn", __float8e4m3fn__,float8_e4m3fn, "cuda"),
          ("float16", __float16__, float16, "cuda"),
          ("bfloat16", __bfloat16__, bfloat16, "cuda"),
          ("float32", __float32__, float32, "cuda")] if torch.cuda.is_available() else []))
    def test_rounding(self, name, fp, dtype, device):
        a, b = finfo(dtype).min, finfo(dtype).max
        assert a == fp.minimum and b == fp.maximum
        a = -3e37 if a < -3e37 else a
        b = 3e37 if b > 3e37 else b
        x = FloatTensor(100).uniform_(a, b).clamp(min=a, max=b).to(device=device)
        quantized_x = round(x, fp.exponent_bits, fp.mantissa_bits, fp.bias)
        torch_rounded_x = x.to(dtype).float()
        l1_error = (quantized_x - torch_rounded_x).abs().sum().item()
        self.assertTrue(l1_error == 0.0, f"Rounding mismatch in {l1_error}, for {name} ({dtype}) on {device}.")

if __name__ == "__main__":
    unittest.main()
