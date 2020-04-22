#This file will publish experiment in Workspace 

import os
import urllib
import shutil
import azureml

from azureml.core import Experiment
from azureml.core import Workspace, Run
from azureml.core.compute import ComputeTarget, AmlCompute
from azureml.core.compute_target import ComputeTargetException
from azureml.train.sklearn import SKLearn


ws = Workspace.from_config()

project_folder = '.'
os.makedirs(project_folder, exist_ok=True)


exp = Experiment(workspace=ws, name='sklearn-iris')


cluster_name = "mytrcompute44"

try:
    compute_target = ComputeTarget(workspace=ws, name=cluster_name)
    print('Found existing compute target')
except ComputeTargetException:
    print('Creating a new compute target...')
    #compute_config = AmlCompute.provisioning_configuration(vm_size='STANDARD_D2_V2', 
                                                           #max_nodes=4)

    #compute_target = ComputeTarget.create(ws, cluster_name, compute_config)

    #compute_target.wait_for_completion(show_output=True, min_node_count=None, timeout_in_minutes=20)

# script_params = {
#     '--kernel': 'linear',
#     '--penalty': 1.0,}


estimator = SKLearn(source_directory=project_folder, 
#script_params=script_params,
compute_target=compute_target,
entry_script='test2.py',
conda_dependencies_file="env.yml"
)
print("submitting experiment")
run = exp.submit(estimator)
print("experiment submitted")
run.wait_for_completion(show_output=True)