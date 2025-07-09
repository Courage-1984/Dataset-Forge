from dataset_forge.dataset_ops import DatasetCombiner
from dataset_forge.utils.history_log import log_operation


def combine_datasets(src1, src2, dest):
    combiner = DatasetCombiner()
    combiner.run()
    log_operation("combine", f"Combined {src1} and {src2} into {dest}")
