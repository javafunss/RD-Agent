import pickle
import shutil
from pathlib import Path
from typing import Any, Tuple

from rdagent.core.developer import Developer
from rdagent.core.experiment import ASpecificExp, Experiment
from rdagent.oai.llm_utils import md5_hash


class CachedRunner(Developer[ASpecificExp]):
    def get_cache_key(self, exp: Experiment) -> str:
        if exp is None:
            return "None"
        all_tasks = []
        for based_exp in exp.based_experiments:
            all_tasks.extend(based_exp.sub_tasks)
        all_tasks.extend(exp.sub_tasks)
        task_info_list = [task.get_task_information() for task in all_tasks]
        task_info_str = "\n".join(task_info_list)
        return md5_hash(task_info_str)

    def assign_cached_result(self, exp: Experiment, cached_res: Experiment) -> Experiment:
        if exp is None:
            return None
        if exp.based_experiments and exp.based_experiments[-1].result is None:
            exp.based_experiments[-1].result = cached_res.based_experiments[-1].result
        if cached_res.experiment_workspace.workspace_path.exists():
            for csv_file in cached_res.experiment_workspace.workspace_path.glob("*.csv"):
                shutil.copy(csv_file, exp.experiment_workspace.workspace_path)
            for py_file in (cached_res.experiment_workspace.workspace_path / "feature").glob("*.py"):
                shutil.copy(py_file, exp.experiment_workspace.workspace_path / "feature")
            for py_file in (cached_res.experiment_workspace.workspace_path / "model").glob("*.py"):
                shutil.copy(py_file, exp.experiment_workspace.workspace_path / "model")
        exp.result = cached_res.result
        return exp
