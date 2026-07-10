from pathlib import Path

import pandas as pd

from utils.eda import generate_eda_report
from utils.preprocessing import PreprocessingPipeline, cap_outliers, detect_duplicates, handle_missing_values, remove_duplicates


def test_handle_missing_values():
    df = pd.DataFrame({"a": [1.0, None, 3.0], "b": ["x", None, "z"]})
    result = handle_missing_values(df)
    assert result.isnull().sum().sum() == 0


def test_remove_duplicates():
    df = pd.DataFrame({"a": [1, 1, 2], "b": [3, 3, 4]})
    result = remove_duplicates(df)
    assert len(result) == 2


def test_cap_outliers():
    df = pd.DataFrame({"a": [1, 2, 100], "flood": [0, 1, 0]})
    result = cap_outliers(df)
    assert result["a"].max() < 100


def test_preprocessing_pipeline_runs():
    pipeline = PreprocessingPipeline(Path("dataset/raw/flood_dataset.xlsx"), output_dir=Path("."))
    result = pipeline.run_pipeline()
    assert "processed_path" in result


def test_generate_eda_report_falls_back_without_tabulate(tmp_path, monkeypatch):
    df = pd.DataFrame({"a": [1, 2, 3], "flood": [0, 1, 0]})

    def broken_to_markdown(self, *args, **kwargs):
        raise ImportError("Missing optional dependency 'tabulate'")

    monkeypatch.setattr(pd.DataFrame, "to_markdown", broken_to_markdown)
    output_path = tmp_path / "eda_report.md"

    report_path = generate_eda_report(df, output_path=output_path)

    assert report_path.exists()
    assert "Exploratory Data Analysis Report" in output_path.read_text(encoding="utf-8")
