#This file will publish experiment in Workspace 

import os
import urllib
import shutil
import azureml
from azureml.core.authentication import ServicePrincipalAuthentication
from azureml.core import Experiment
from azureml.core import Workspace, Run
from azureml.core.compute import ComputeTarget, AmlCompute
from azureml.core.compute_target import ComputeTargetException
from azureml.train.sklearn import SKLearn
import argparse
from dotenv import load_dotenv
load_dotenv()

parser = argparse.ArgumentParser()
parser.add_argument("--ws",
                    dest="ws",
                    )

parser.add_argument("--rg",
                    dest="rg",
                    )

parser.add_argument("--experiment",
                    dest="experiment",
                    )

parser.add_argument("--trcompute",
                    dest="trcompute",
                    )

parser.add_argument("--trainingscript",
                    dest="trainingscript",
                    )
parser.add_argument("--datastore",
                    dest="datastore",
                    )

parser.add_argument("--dataset",
                    dest="dataset",
                    )


args = parser.parse_args()

ws = Workspace.get(args.ws, ServicePrincipalAuthentication(
    tenant_id=os.getenv('tenant_id'),
    service_principal_id=os.getenv('service_principal_id'),
    service_principal_password=os.getenv('service_principal_password')
), 
    subscription_id=os.getenv('subscription_id'),
    resource_group=args.rg
)

print(ws)

project_folder = '.'
os.makedirs(project_folder, exist_ok=True)


exp = Experiment(workspace=ws, name=args.experiment)

print(exp)

cluster_name = args.trcompute

try:
    compute_target = ComputeTarget(workspace=ws, name=cluster_name)
    print('Found existing compute target')
except ComputeTargetException:
    print('Creating a new compute target...')

# Parameters to be passed in training scrript

script_params = {
     '--ws': args.ws,
     '--rg': args.rg,
     '--datastore': args.datastore,
     '--dataset': args.dataset,}

estimator = SKLearn(source_directory=project_folder, 
script_params=script_params,
compute_target=compute_target,
entry_script=args.trainingscript,
conda_dependencies_file="env.yml"
)
print("submitting experiment")
run = exp.submit(estimator)
print("experiment submitted")
run.wait_for_completion(show_output=True)
