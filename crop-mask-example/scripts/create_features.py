"""
Combines the earth observation data with the labels to create (x, y) training data
"""
import os
import pandas as pd
import sys
import tarfile

from pathlib import Path

project_root = Path(__file__).parent.parent.resolve()

# Change the working directory to the directory of this script
os.chdir(os.path.dirname(os.path.realpath(__file__)))

sys.path.append("..")

from openmapflow import get_config, get_paths, load_all_features_as_df  # noqa: E402
from datasets import datasets  # noqa: E402

tif_bucket_name = get_config(project_root)["labeled_tifs_bucket"]
paths = get_paths(project_root)


def check_empty_features(features_df: pd.DataFrame) -> str:
    """
    Some exported tif data may have nan values
    """
    empties = features_df[features_df["labelled_array"].isnull()]
    num_empty = len(empties)
    if num_empty > 0:
        return f"\u2716 Found {num_empty} empty features"
    else:
        return "\u2714 Found no empty features"


def check_duplicates(features_df: pd.DataFrame) -> str:
    """
    Can happen when not all tifs have been downloaded and different labels are matched to same tif
    """
    cols_to_check = ["instance_lon", "instance_lat", "source_file"]
    duplicates = features_df[features_df.duplicated(subset=cols_to_check)]
    num_dupes = len(duplicates)
    if num_dupes > 0:
        return f"\u2716 Found {num_dupes} duplicates"
    else:
        return "\u2714 No duplicates found"


if __name__ == "__main__":
    report = "DATASET REPORT (autogenerated, do not edit directly)"
    for d in datasets:
        d.set_attributes(paths=paths, tif_bucket_name=tif_bucket_name)
        text = d.create_features()
        report += "\n\n" + text

    features_df = load_all_features_as_df(
        features_dir=paths["features"], duplicates_file=paths["duplicates"]
    )
    empty_text = check_empty_features(features_df)
    print(empty_text)
    duplicates_text = check_duplicates(features_df)
    print(duplicates_text)
    report += "\n\nAll data:\n" + empty_text + "\n" + duplicates_text

    with paths["datasets"].open("w") as f:
        f.write(report)

    # Compress features for faster CI/CD
    print("Compressing features...")
    with tarfile.open(paths["compressed_features"], "w:gz") as tar:
        tar.add(paths["features"], arcname="features")
