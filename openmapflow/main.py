from typing import List
import tarfile

from .config import full_paths
from .all_features import AllFeatures
from .dataset import LabeledDataset

training_data_path_keys = ["raw", "processed", "compressed_features.tar.gz"]


def create_features(datasets: List[LabeledDataset]):

    report = "DATASET REPORT (autogenerated, do not edit directly)"
    for d in datasets:
        text = d.create_features()
        report += "\n\n" + text

    all_features = AllFeatures()
    empty_text = all_features.check_empty()
    print(empty_text)
    duplicates_text = all_features.check_duplicates()
    print(duplicates_text)
    report += "\n\nAll data:\n" + empty_text + "\n" + duplicates_text

    with full_paths["datasets"].open("w") as f:
        f.write(report)

    # Compress features for faster CI/CD
    print("Compressing features...")
    with tarfile.open(full_paths["datasets"], "w:gz") as tar:
        tar.add(full_paths["datasets"], arcname="features")