
from azureml.core import Model, Workspace, ComputeTarget, Webservice
from azureml.core.authentication import ServicePrincipalAuthentication
from azureml.core.image.image import ImageConfig
from typing import List
from azureml.core.image import ContainerImage
from azureml.core.webservice import AksWebservice


#ws = Run.get_context()
#Create Service Function
def create_aks_service(
        name: str,
        image_config: ImageConfig,
        models: List[Model],
        target: ComputeTarget,
        ws: Workspace) -> Webservice:
    """
    Creates a new web service
    :param name: name of the service
    :param image_config: image configuration
    :param models: ML model object
    :param target: ComputeTarget
    :param ws:
    :return: Webservice
    """
    print("Loading AKS deploy config from deployconfig_aks.yml")
    #conf_params = yaml.safe_load(open("./config/deployconfig_aks.yml"))
    deploy_conf = AksWebservice.deploy_configuration()
    print(models)
    service = Webservice.deploy_from_model(workspace=ws,
                                           name=name,
                                           deployment_target=target,
                                           models=models,
                                           deployment_config=deploy_conf,
                                           image_config=image_config)

    service.wait_for_deployment(show_output=True)
    return service

#Create image config Function used in creation of service
def create_image_config(script_name, conda_env):
    # environment = os.getenv("ENVIRONMENT", "DEV")
    # if os.path.exists("azureml-models"):
    #     print("WARNING! Deleting azureml-models folder")
    #     rmtree("azureml-models")
    # if os.path.exists("assets"):
    #     print("WARNING! Deleting assets folder")
    #     rmtree("assets")
    image_config = ContainerImage.image_configuration(execution_script=script_name,
                                                      runtime="python",
                                                      #docker_file="config/" + environment.lower() + ".dockerfile",
                                                      dependencies=["./"],
                                                      conda_file=conda_env)
    return image_config

def update_service(service, models, image_config, ws):
    image = ContainerImage.create(name=service.name,
                                  models=models,
                                  image_config=image_config,
                                  workspace=ws)
    image.wait_for_creation()
    print("Created Image: ", image)
    service.update(image=image)
    service.wait_for_deployment(show_output=True)
    return service

# Authentication via service principle
ws = Workspace.get("ws-ml", ServicePrincipalAuthentication(
    tenant_id=",
    service_principal_id="",
    service_principal_password=""
), 
    subscription_id="",
    resource_group=""
)



model  = Model(ws, "new_model")
deployment_target=ComputeTarget(ws, "akscluster")

img = create_image_config("score.py","scoringenv.yml")

servicename = "myservice2"
try:
    service = Webservice(ws, servicename)
except WebserviceException as e:
    print(e)
    service = None
if service:
    print("Updating existing service with new image...")
    try:
        # create new image
        service = update_service(
            service, [model], img, ws)
    except Exception as e:
        print("Unable to link existing service.\n {}".format(e))
else:
    create_aks_service(servicename,img,[model],deployment_target,ws)
