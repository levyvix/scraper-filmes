from prefect.infrastructure import DockerContainer
from prefect.deployments import Deployment
from prefect_flow_se import comandola_filmes

docker_zoom = DockerContainer.load("zoom")

dep = Deployment.build_from_flow(
    flow=comandola_filmes,
    name="comandola_filmes_sem_date",
    version=1,
    infrastructure=docker_zoom,
    work_queue_name="dev",
)

dep.apply()
