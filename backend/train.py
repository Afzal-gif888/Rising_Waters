"""Entrypoint for the model training pipeline."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from ml.utils.model_training import run_training_pipeline as _execute_training_pipeline


def run_training_pipeline(
    data_path: str | Path | None = None,
    output_dir: str | Path | None = None,
    target_column: str = "flood",
) -> tuple[Any, Path]:
    return _execute_training_pipeline(
        data_path=data_path,
        output_dir=output_dir,
        target_column=target_column,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the flood model training pipeline.")
    parser.add_argument("--data-path", help="Path to the processed training dataset.", default=None)
    parser.add_argument("--output-dir", help="Directory where reports and figures are written.", default=None)
    parser.add_argument("--target-column", help="Target column name in the dataset.", default="flood")
    args = parser.parse_args()

    summary, report_path = run_training_pipeline(
        data_path=args.data_path,
        output_dir=args.output_dir,
        target_column=args.target_column,
    )
    print("Training pipeline completed.")
    print(f"Report saved to: {report_path}")
