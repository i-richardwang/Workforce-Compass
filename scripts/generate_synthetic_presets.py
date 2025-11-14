import argparse
import os
import random
from typing import List, Dict, Tuple

import numpy as np
import pandas as pd


# -----------------------------
# Helpers
# -----------------------------

def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)


def round_to_step(values: List[float], target_sum: int, step: int = 5, low: List[int] = None, high: List[int] = None) -> List[int]:
    """
    Round a list of float values to integers in multiples of `step` and rebalance to match target_sum.
    Optional per-item lower/upper bounds can be provided via `low` and `high`.
    """
    n = len(values)
    low = low or [0] * n
    high = high or [None] * n

    # Initial rounding
    ints = [int(step * round(v / step)) for v in values]

    # Apply bounds
    for i in range(n):
        if high[i] is not None and ints[i] > high[i]:
            ints[i] = high[i] - (high[i] % step)
        if ints[i] < low[i]:
            ints[i] = low[i]

    # Rebalance to target
    current = sum(ints)
    diff = target_sum - current

    # Helper to try to adjust one index by +/- step under bounds
    def try_adjust(idx: int, delta: int) -> bool:
        new_val = ints[idx] + delta
        if new_val < low[idx]:
            return False
        if high[idx] is not None and new_val > high[idx]:
            return False
        if new_val < 0:
            return False
        ints[idx] = new_val
        return True

    # Distribute difference greedily with cycling
    indices = list(range(n))
    cycles = 0
    while diff != 0 and cycles < n * 1000:  # safety cap
        random.shuffle(indices)
        changed = False
        for idx in indices:
            if diff == 0:
                break
            delta = step if diff > 0 else -step
            if try_adjust(idx, delta):
                diff -= delta
                changed = True
        if not changed:
            # If we cannot change anything further, break
            break
        cycles += 1

    # Final guard: adjust any small residuals by relaxing step to 1 if needed
    if diff != 0:
        for i in range(n):
            if diff == 0:
                break
            delta = 1 if diff > 0 else -1
            new_val = ints[i] + delta
            hi = high[i] if high[i] is not None else float('inf')
            if low[i] <= new_val <= hi:
                ints[i] = new_val
                diff -= delta

    return ints


def normalize(weights: np.ndarray) -> np.ndarray:
    w = np.maximum(weights, 0)
    s = w.sum()
    if s == 0:
        return np.ones_like(w) / len(w)
    return w / s


# -----------------------------
# Core synthetic generation
# -----------------------------

LEVELS_PUBLIC = [f"L{i}" for i in range(1, 8)]  # L1..L7, L1=entry level


def generate_structure_weights(n_levels: int = 7) -> np.ndarray:
    # Base pyramid shape (low to high): heavier at lower levels
    base = np.array([0.25, 0.22, 0.18, 0.15, 0.10, 0.06, 0.04])
    if n_levels != 7:
        base = np.linspace(1.0, 0.3, n_levels)
    noise = np.random.normal(0, 0.005, size=base.shape)
    w = np.clip(base + noise, 0.01, None)
    return normalize(w)


def generate_hiring_weights(n_levels: int = 7) -> np.ndarray:
    # Social hiring concentrated in mid levels
    base = np.array([0.05, 0.30, 0.30, 0.20, 0.10, 0.04, 0.01])
    noise = np.random.normal(0, 0.005, size=base.shape)
    w = np.clip(base + noise, 0.001, None)
    return normalize(w)


def generate_age_profiles(n_levels: int = 7) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    # Campus: ~24 at L1, +1.0 per level
    campus_start = np.random.choice([24.0, 24.5, 25.0])
    campus_step = 1.0
    campus_age = np.array([campus_start + i * campus_step for i in range(n_levels)])
    campus_age = np.round(campus_age * 2) / 2
    campus_age = np.clip(campus_age, 22.5, 40.0)

    # Social: ~28 at L1, +1.5 per level
    social_start = np.random.choice([27.0, 28.0, 29.0])
    social_step = 1.5
    social_age = np.array([social_start + i * social_step for i in range(n_levels)])
    social_age = np.round(social_age * 2) / 2
    social_age = np.clip(social_age, 25.0, 48.0)

    # Social new hire age
    social_nh_age = social_age - np.linspace(1.0, -0.5, n_levels)
    social_nh_age = np.round(social_nh_age * 2) / 2
    social_nh_age = np.clip(social_nh_age, 24.0, 48.0)

    return campus_age, social_age, social_nh_age


def generate_rates(n_levels: int = 7) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    # Promotion rates decrease with level
    campus_prom = np.array([0.15, 0.12, 0.10, 0.06, 0.04, 0.02, 0.01])
    social_prom = np.array([0.12, 0.10, 0.08, 0.05, 0.03, 0.02, 0.01])

    # Attrition rates: higher at low levels
    campus_attr = np.array([0.25, 0.20, 0.18, 0.15, 0.12, 0.10, 0.08])
    social_attr = np.array([0.22, 0.20, 0.18, 0.15, 0.12, 0.10, 0.08])

    for arr, hi in [(campus_prom, 0.20), (social_prom, 0.18), (campus_attr, 0.35), (social_attr, 0.35)]:
        noise = np.random.normal(0, 0.002, size=n_levels)
        arr += noise
        np.clip(arr, 0.0, hi, out=arr)

    return campus_prom, social_prom, campus_attr, social_attr


def format_rates(x: np.ndarray, ndigits: int = 3) -> List[float]:
    return [float(f"{v:.{ndigits}f}") for v in x]


def format_age(x: np.ndarray) -> List[float]:
    return [float(f"{v:.1f}") for v in x]


def generate_counts(n_levels: int, total_headcount: int, campus_ratio: float, struct_w: np.ndarray) -> Tuple[List[int], List[int]]:
    raw_totals = total_headcount * struct_w
    level_totals = round_to_step(raw_totals.tolist(), target_sum=total_headcount, step=10)

    # Campus distribution preference: heavier at lower levels
    pref = np.array([1.6, 1.3, 1.1, 0.9, 0.7, 0.5, 0.3])
    pref = normalize(pref)

    campus_total = int(round(total_headcount * campus_ratio))
    denom = np.sum(np.array(level_totals) * pref)
    scale = (campus_total / denom) if denom > 0 else 0.0
    campus_floats = (np.array(level_totals) * pref * scale).tolist()

    campus_counts = round_to_step(
        campus_floats,
        target_sum=campus_total,
        step=10,
        low=[0] * n_levels,
        high=level_totals,
    )

    social_counts = [lt - c for lt, c in zip(level_totals, campus_counts)]

    return campus_counts, social_counts


def generate_one(seed: int = 42,
                 total_headcount: Tuple[int, int] = (2200, 5800),
                 campus_ratio_range: Tuple[float, float] = (0.03, 0.12)) -> Dict:
    set_seed(seed)
    n_levels = 7

    total_options = [2500, 3000, 3500, 4000, 4500, 5000]
    total = random.choice(total_options)

    campus_ratio_options = [0.05, 0.08, 0.10, 0.12, 0.15]
    campus_ratio = random.choice(campus_ratio_options)

    struct_w = generate_structure_weights(n_levels)
    campus_age, social_age, social_nh_age = generate_age_profiles(n_levels)
    campus_prom, social_prom, campus_attr, social_attr = generate_rates(n_levels)

    campus_counts, social_counts = generate_counts(n_levels, total, campus_ratio, struct_w)

    hiring_w = generate_hiring_weights(n_levels)
    # Round hiring weights to 0.001, ensure sum=1 by adjusting last element
    hiring_ratio = [float(f"{w:.3f}") for w in hiring_w]
    adjust = 1.0 - sum(hiring_ratio)
    hiring_ratio[-1] = float(f"{hiring_ratio[-1] + adjust:.3f}")

    records = []
    for i in range(n_levels):
        leaving_increment = np.random.choice([1.0, 1.5, 2.0])
        rec = {
            "public_level": f"L{i+1}",
            "level_index": 5 + i,
            "campus_employee": campus_counts[i],
            "social_employee": social_counts[i],
            "campus_age": campus_age[i],
            "social_age": social_age[i],
            "campus_leaving_age": np.clip(campus_age[i] + leaving_increment, 23.0, 45.0),
            "social_leaving_age": np.clip(social_age[i] + leaving_increment, 26.0, 50.0),
            "social_new_hire_age": social_nh_age[i],
            "campus_promotion_rate": campus_prom[i],
            "social_promotion_rate": social_prom[i],
            "campus_attrition_rate": campus_attr[i],
            "social_attrition_rate": social_attr[i],
            "hiring_ratio": hiring_ratio[i],
        }
        records.append(rec)

    for rec in records:
        rec["campus_age"] = float(f"{rec['campus_age']:.1f}")
        rec["social_age"] = float(f"{rec['social_age']:.1f}")
        rec["campus_leaving_age"] = float(f"{rec['campus_leaving_age']:.1f}")
        rec["social_leaving_age"] = float(f"{rec['social_leaving_age']:.1f}")
        rec["social_new_hire_age"] = float(f"{rec['social_new_hire_age']:.1f}")

        for k in [
            "campus_promotion_rate", "social_promotion_rate",
            "campus_attrition_rate", "social_attrition_rate",
        ]:
            rec[k] = round(rec[k] * 100) / 100

        rec["hiring_ratio"] = float(f"{rec['hiring_ratio']:.3f}")

    return {
        "seed": seed,
        "total": total,
        "campus_ratio": float(f"{campus_ratio:.3f}"),
        "records": records,
    }


def to_dataframe(payload: Dict) -> pd.DataFrame:
    df = pd.DataFrame(payload["records"])
    df["level"] = df["public_level"]
    cols = [
        "level", "campus_employee", "social_employee", "campus_age", "social_age",
        "campus_leaving_age", "social_leaving_age", "social_new_hire_age",
        "campus_promotion_rate", "social_promotion_rate",
        "campus_attrition_rate", "social_attrition_rate", "hiring_ratio",
    ]
    df = df[cols]
    df = df.sort_values(by="level", key=lambda s: s.str.replace('L', '').astype(int))
    return df


def main():
    parser = argparse.ArgumentParser(description="Generate synthetic presets for talent structure model")
    parser.add_argument("--output", default="data",
                        help="Output directory for L1-L7 format CSVs")
    parser.add_argument("--count", type=int, default=2, help="How many files to generate")
    parser.add_argument("--seed", type=int, default=20241111, help="Random seed base")

    args = parser.parse_args()

    os.makedirs(args.output, exist_ok=True)

    for i in range(args.count):
        seed = args.seed + i
        payload = generate_one(seed=seed)

        file_suffix = chr(ord('A') + i)

        df_pub = to_dataframe(payload)
        pub_path = os.path.join(args.output, f"sample_dept_{file_suffix}.csv")
        df_pub.to_csv(pub_path, index=False)
        print(f"Generated {pub_path}")

    print("Done.")


if __name__ == "__main__":
    main()
