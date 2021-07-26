import os
from typing import List

# modified from https://github.com/ray-project/ray/issues/4569#issuecomment-809543802
# retrive latest checkpoint
def retrieve_latest_checkpoint(path: str = "data/results", prefix: str = "train_fn") -> str:
    """Returns a latest checkpoint unless there are none, then it returns None."""
    def all_dirs_under(path):
        """Iterates through all files that are under the given path."""
        for cur_path, dirnames, filenames in os.walk(path):
            for dir_ in dirnames:
                yield os.path.join(cur_path, dir_)

    def retrieve_checkpoints(paths: List[str]) -> List[str]:
        checkpoints = list()
        for path in paths:
            for cur_path, dirnames, _ in os.walk(path):
                for dirname in dirnames:
                    if dirname.startswith("checkpoint_"):
                        checkpoints.append(os.path.join(cur_path, dirname))
        return checkpoints

    sorted_checkpoints = retrieve_checkpoints(
        sorted(
            filter(
                lambda x: x.startswith(path + "/" + prefix), all_dirs_under(path)
            ),
            key=os.path.getmtime
        )
    )[::-1]
    
    latest_checkpoint = None
    latest_checkpoint_iter = 0
    
    for checkpoint in sorted_checkpoints:
        if checkpoint is not None and 'checkpoint' in checkpoint:
            checkpoint_iter = int(checkpoint.rsplit('_', 1)[1])
            checkpoint_filepath = checkpoint + '/checkpoint-' + checkpoint.split('_')[-1]
            if checkpoint_iter > latest_checkpoint_iter and os.path.isfile(checkpoint_filepath):
                latest_checkpoint_iter = checkpoint_iter
                latest_checkpoint = checkpoint_filepath

    return latest_checkpoint 