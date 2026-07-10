from pathlib import Path

import pandas as pd

from utils.data_loader import load_dataset


def test_load_dataset_with_excel_file():
    dataset_path = Path("dataset/raw/flood_dataset.xlsx")
    dataframe = load_dataset(dataset_path)
    assert isinstance(dataframe, pd.DataFrame)
    assert not dataframe.empty
