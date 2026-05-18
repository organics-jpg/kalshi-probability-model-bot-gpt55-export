from __future__ import annotations

from dataclasses import dataclass
import math


def clamp(value: float, lo: float, hi: float) -> float:
    return min(hi, max(lo, value))


@dataclass
class LabelGatedACICalibrator:
    """Tiny online calibrator whose state changes only after labels arrive."""

    target_coverage: float = 0.9
    step_size: float = 0.02
    q: float = 0.1
    min_q: float = 0.0
    max_q: float = 0.5

    def interval(self, p_raw: float) -> tuple[float, float]:
        p = clamp(p_raw, 0.0, 1.0)
        return clamp(p - self.q, 0.0, 1.0), clamp(p + self.q, 0.0, 1.0)

    def point(self, p_raw: float) -> float:
        # The MVP keeps rank untouched. The interval width is the calibrated
        # uncertainty object until a smoother point recalibrator is added.
        return clamp(p_raw, 0.0, 1.0)

    def predict(self, p_raw: float) -> tuple[float, tuple[float, float]]:
        return self.point(p_raw), self.interval(p_raw)

    def update_with_label(self, p_raw: float, y: int) -> None:
        if y not in (0, 1):
            raise ValueError("binary label must be 0 or 1")
        lo, hi = self.interval(p_raw)
        covered = lo <= y <= hi
        miss = 0.0 if covered else 1.0
        target_miss = 1.0 - self.target_coverage
        self.q = clamp(self.q + self.step_size * (miss - target_miss), self.min_q, self.max_q)


@dataclass
class OnlineLogitCalibrator:
    """Online point calibrator updated only after labels are available."""

    learning_rate: float = 0.03
    l2: float = 0.001
    bias: float = 0.0
    slope: float = 1.0
    min_probability: float = 0.001
    max_abs_logit: float = 6.0
    min_slope: float = 0.05
    max_slope: float = 5.0

    def predict(self, p_raw: float) -> float:
        x = self._logit(p_raw)
        z = clamp(self.slope * x + self.bias, -self.max_abs_logit, self.max_abs_logit)
        return clamp(_sigmoid(z), self.min_probability, 1.0 - self.min_probability)

    def update_with_label(self, p_raw: float, y: int) -> None:
        if y not in (0, 1):
            raise ValueError("binary label must be 0 or 1")
        x = self._logit(p_raw)
        p_cal = self.predict(p_raw)
        error = p_cal - float(y)
        bias_grad = error + self.l2 * self.bias
        slope_grad = error * x + self.l2 * (self.slope - 1.0)
        self.bias = clamp(
            self.bias - self.learning_rate * bias_grad,
            -self.max_abs_logit,
            self.max_abs_logit,
        )
        self.slope = clamp(
            self.slope - self.learning_rate * slope_grad,
            self.min_slope,
            self.max_slope,
        )

    def _logit(self, p_raw: float) -> float:
        p = clamp(float(p_raw), self.min_probability, 1.0 - self.min_probability)
        return clamp(math.log(p / (1.0 - p)), -self.max_abs_logit, self.max_abs_logit)


def _sigmoid(value: float) -> float:
    if value >= 0.0:
        z = math.exp(-value)
        return 1.0 / (1.0 + z)
    z = math.exp(value)
    return z / (1.0 + z)
