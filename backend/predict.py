"""Entrypoint for the flood prediction pipeline."""

from __future__ import annotations

import argparse
from typing import Mapping

from backend.services.prediction_service import predict_flood


def run_prediction_pipeline(inputs: Mapping[str, object]) -> int:
    return predict_flood(inputs)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run flood prediction using serialized model artifacts.")
    parser.add_argument("--temperature", required=True, type=float)
    parser.add_argument("--humidity", required=True, type=float)
    parser.add_argument("--cloud-cover", required=True, type=float)
    parser.add_argument("--annual-rainfall", required=True, type=float)
    parser.add_argument("--jan-feb", required=True, type=float)
    parser.add_argument("--mar-may", required=True, type=float)
    parser.add_argument("--jun-sep", required=True, type=float)
    parser.add_argument("--oct-dec", required=True, type=float)
    parser.add_argument("--average-june", required=True, type=float)
    parser.add_argument("--sub", required=True, type=float)
    args = parser.parse_args()

    prediction = run_prediction_pipeline(
        {
            "temperature": args.temperature,
            "humidity": args.humidity,
            "cloud_cover": args.cloud_cover,
            "annual_rainfall": args.annual_rainfall,
            "jan_feb": args.jan_feb,
            "mar_may": args.mar_may,
            "jun_sep": args.jun_sep,
            "oct_dec": args.oct_dec,
            "average_june": args.average_june,
            "sub": args.sub,
        }
    )
    print(f"prediction={prediction}")
