from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any


EPS = 1e-6
DEFAULT_CANDIDATE_ID = "v28s_boundary_monotonic_time_safe_v001"
DEFAULT_MODEL_HASH = "9b461a310d06c06b55af2e2d"


def _as_float(value: Any, default: float | None = None) -> float | None:
    if value is None or isinstance(value, bool):
        return default
    try:
        parsed = float(str(value).strip())
    except (TypeError, ValueError):
        return default
    if not math.isfinite(parsed):
        return default
    return parsed


def _clamp_probability(value: Any) -> float:
    parsed = _as_float(value, 0.5)
    return min(1.0 - EPS, max(EPS, float(parsed if parsed is not None else 0.5)))


def _p_bucket(probability: float, bins: int) -> int:
    return min(bins - 1, max(0, int(math.floor(probability * bins))))


@dataclass(frozen=True)
class V28SuccessorPrediction:
    p_yes: float
    raw_p_yes: float
    calibrated_p_yes: float
    corrected_p_yes: float
    correction_scale: float
    boundary_weight: float
    time_weight: float
    effective_weight: float
    bucket: int
    candidate_id: str
    model_hash: str

    @property
    def correction(self) -> float:
        return self.p_yes - self.raw_p_yes


@dataclass(frozen=True)
class V28SuccessorSurface:
    candidate_id: str
    model_hash: str
    model_type: str
    model_track: str
    model_parameters: dict[str, Any]

    def _boundary_weight(self, features: dict[str, Any]) -> float:
        config = self.model_parameters.get("boundary_blend")
        if not isinstance(config, dict) or not config:
            return 1.0
        feature_names = [str(config.get("distance_feature") or "abs_d_sigma")]
        feature_names.extend(str(name) for name in config.get("fallback_distance_features", []) if str(name))
        distance = None
        for feature_name in feature_names:
            distance = _as_float(features.get(feature_name))
            if distance is not None:
                break
        if distance is None:
            return 0.0

        distance = abs(distance)
        inner = _as_float(config.get("full_correction_abs_d_lte"), 1.0) or 1.0
        outer = _as_float(config.get("zero_correction_abs_d_gte"), 2.0) or 2.0
        if outer <= inner:
            return 1.0 if distance <= inner else 0.0
        if distance <= inner:
            return 1.0
        if distance >= outer:
            return 0.0
        return (outer - distance) / (outer - inner)

    def _time_weight(self, features: dict[str, Any]) -> float:
        config = self.model_parameters.get("boundary_blend")
        if not isinstance(config, dict) or not config:
            return 1.0
        time_gate = config.get("time_gate")
        if not isinstance(time_gate, dict) or not time_gate:
            return 1.0

        feature_names = [str(time_gate.get("seconds_to_close_feature") or "seconds_to_close")]
        feature_names.extend(str(name) for name in time_gate.get("fallback_seconds_to_close_features", []) if str(name))
        seconds_to_close = None
        for feature_name in feature_names:
            seconds_to_close = _as_float(features.get(feature_name))
            if seconds_to_close is not None:
                break
        if seconds_to_close is None:
            return 1.0 if time_gate.get("missing_time_policy", "full_correction") == "full_correction" else 0.0

        zero_lte = _as_float(time_gate.get("zero_correction_seconds_lte"), 0.0) or 0.0
        full_gte = _as_float(time_gate.get("full_correction_seconds_gte"), 0.0) or 0.0
        if full_gte <= zero_lte:
            return 1.0 if seconds_to_close > zero_lte else 0.0
        if seconds_to_close <= zero_lte:
            return 0.0
        if seconds_to_close >= full_gte:
            return 1.0
        return (seconds_to_close - zero_lte) / (full_gte - zero_lte)

    def predict(self, *, raw_p_yes: Any, features: dict[str, Any]) -> V28SuccessorPrediction:
        if self.model_type != "monotonic_tabular_calibration":
            raise ValueError(f"Unsupported live successor model type: {self.model_type}")
        p = _clamp_probability(raw_p_yes)
        bins = int(self.model_parameters["bins"])
        table = list(self.model_parameters["bucket_table"])
        bucket = _p_bucket(p, bins)
        calibrated = _clamp_probability(table[bucket]["monotonic_p_yes"])
        corrected = 0.80 * calibrated + 0.20 * p
        boundary_weight = self._boundary_weight(features)
        time_weight = self._time_weight(features)
        config = self.model_parameters.get("boundary_blend")
        correction_scale = 1.0
        if isinstance(config, dict):
            parsed_scale = _as_float(config.get("correction_scale"), 1.0)
            correction_scale = 1.0 if parsed_scale is None else parsed_scale
        correction_scale = max(0.0, min(1.0, correction_scale))
        effective_weight = correction_scale * boundary_weight * time_weight
        p_yes = min(1.0 - EPS, max(EPS, p + effective_weight * (corrected - p)))
        return V28SuccessorPrediction(
            p_yes=p_yes,
            raw_p_yes=p,
            calibrated_p_yes=calibrated,
            corrected_p_yes=corrected,
            correction_scale=correction_scale,
            boundary_weight=boundary_weight,
            time_weight=time_weight,
            effective_weight=effective_weight,
            bucket=bucket,
            candidate_id=self.candidate_id,
            model_hash=self.model_hash,
        )


def load_surface(
    manifest_path: Path,
    *,
    candidate_id: str = DEFAULT_CANDIDATE_ID,
    expected_model_hash: str = DEFAULT_MODEL_HASH,
) -> V28SuccessorSurface:
    payload = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError(f"Expected list manifest at {manifest_path}")
    for row in payload:
        if not isinstance(row, dict):
            continue
        if str(row.get("candidate_id") or "") != candidate_id:
            continue
        model_hash = str(row.get("model_hash") or "")
        if expected_model_hash and model_hash != expected_model_hash:
            raise ValueError(
                f"Candidate {candidate_id} model hash mismatch: expected {expected_model_hash}, got {model_hash}"
            )
        return V28SuccessorSurface(
            candidate_id=candidate_id,
            model_hash=model_hash,
            model_type=str(row.get("model_type") or ""),
            model_track=str(row.get("model_track") or ""),
            model_parameters=dict(row.get("model_parameters") or {}),
        )
    raise ValueError(f"Candidate {candidate_id} not found in {manifest_path}")
