import kopf, logging, random
import asyncio,os,yaml,logging
from kubernetes import client, config
from kubernetes.client.rest import ApiException
from jinja2 import Environment, FileSystemLoader


def genDeployment(name,namespace,spec):
  file_path = os.path.dirname(os.path.realpath(__file__)) + "/templates"
  environment = Environment(loader=FileSystemLoader(file_path))
  template = environment.get_template("deployment.j2")
  resources = spec.get('resources')
  if 'limits' not in resources.keys():
    limits={}
  else:
    limits=spec.get('resources')['limits']
  body = template.render(
    name=name.replace('.','-'),
    namespace=namespace,
    image=str(spec.get('image')),
    password=str(spec.get('password')),
    requests=spec.get('resources')['requests'],
    limits=limits
    )
  return(yaml.safe_load(body))  

def genPVC(name,namespace,spec):
  file_path = os.path.dirname(os.path.realpath(__file__)) + "/templates"
  environment = Environment(loader=FileSystemLoader(file_path))
  template = environment.get_template("pvc.j2")
  body = template.render(
    name=name.replace('.','-'),
    namespace=namespace,
    volumeSize=str(spec.get('volumeSize')),
    storageClassName=str(spec.get('storageClassName'))
    )
  return(yaml.safe_load(body))  

def genService(name,namespace,spec):
  file_path = os.path.dirname(os.path.realpath(__file__)) + "/templates"
  environment = Environment(loader=FileSystemLoader(file_path))
  template = environment.get_template("service.j2")
  body = template.render(
    name=name.replace('.','-'),
    namespace=namespace,
    )
  return(yaml.safe_load(body))  

def genIngress(name,namespace,spec):
  file_path = os.path.dirname(os.path.realpath(__file__)) + "/templates"
  environment = Environment(loader=FileSystemLoader(file_path))
  template = environment.get_template("ingress.j2")
  body = template.render(
    name=name.replace('.','-'),
    namespace=namespace,
    ingressclass=str(spec.get('ingress-class')),
    ingresshost=str(spec.get('ingress-host'))
    )
  return(yaml.safe_load(body)) 

#https://kopf.readthedocs.io/en/stable/peering/?highlight=wait#multi-pod-operators
@kopf.on.startup()
def configure(settings: kopf.OperatorSettings, **_):
    settings.peering.priority = random.randint(0, 32767) 
    settings.peering.stealth = True
    settings.peering.standalone = False
    settings.posting.level = logging.INFO

@kopf.on.create('vcodeworkspaces')
async def create_vcodeworkspaces(spec, name, namespace, logger, **kwargs):
  deployment = genDeployment(name,namespace,spec)
  pvc = genPVC(name,namespace,spec)
  service = genService(name,namespace,spec)
  ingress = genIngress(name,namespace,spec)
  try:
      v1_core = client.CoreV1Api()
      v1_apps = client.AppsV1Api()
      v1_networking = client.NetworkingV1Api()
      # Make unnecesary to manage deletion
      kopf.adopt(deployment)
      kopf.adopt(pvc)
      kopf.adopt(service)
      kopf.adopt(ingress)
      v1_apps.create_namespaced_deployment(namespace,deployment,pretty='true')
      v1_core.create_namespaced_persistent_volume_claim(namespace,pvc,pretty='true')
      v1_core.create_namespaced_service(namespace,service,pretty='true')
      v1_networking.create_namespaced_ingress(namespace,ingress,pretty='true')
      await asyncio.sleep(2.0)
  except ApiException as e:
      e=str(e).replace('\n','\\n')
      error_msg=f'{{"error": {e}}}'
      logger.error("Exception when calling create_vcodeworkspaces: %s\n" % error_msg)


@kopf.on.update('vcodeworkspaces')
async def update_vcodeworkspaces(spec, old, new, name, namespace, logger, diff, **_):
  changed_deployment = bool([item for item in diff if item[1][1] == 'resources']) or bool([item for item in diff if item[1][1] == 'image']) or bool([item for item in diff if item[1][1] == 'password']) 
  changed_pvc = bool([item for item in diff if item[1][1] == 'volumeSize']) or bool([item for item in diff if item[1][1] == 'storageClassName'])
  changed_ingress = bool([item for item in diff if item[1][1] == 'ingress-host']) or bool([item for item in diff if item[1][1] == 'ingress-class'])
  res_name=f"vcode-operator-{name}".replace('.','-')
  try:
      if changed_ingress:
        ingress = genIngress(name,namespace,spec)
        v1_networking = client.NetworkingV1Api()
        kopf.adopt(ingress)
        v1_networking.replace_namespaced_ingress(res_name,namespace,ingress,pretty='true')
        logger.info("Updating ingress")
      if changed_pvc:
        pvc = genPVC(name,namespace,spec)
        v1_core = client.CoreV1Api()
        kopf.adopt(pvc)
        if bool([item for item in diff if item[1][1] == 'volumeSize']):
          # Patch pvc size
          pass
        else:
          # Delete and create pvc
          changed_deployment=True  # To recreate home files
          pass
        logger.info("Updating pvc")
      if changed_deployment:
        deployment = genDeployment(name,namespace,spec)
        v1_apps = client.AppsV1Api()
        kopf.adopt(deployment)
        v1_apps.replace_namespaced_deployment(res_name,namespace,deployment,pretty='true')
        logger.info("Updating deployment")
      await asyncio.sleep(2.0)
  except ApiException as e:
      e=str(e).replace('\n','\\n')
      error_msg=f'{{"error": {e}}}'
      logger.error("Exception when calling update_vcodeworkspaces: %s\n" % error_msg)

#config.load_kube_config()  # for local environment
#config.load_incluster_config()  