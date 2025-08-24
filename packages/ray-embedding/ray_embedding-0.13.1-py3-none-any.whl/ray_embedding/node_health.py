import logging
import threading
from typing import Set, List

import ray
from ray import serve
from ray._private.services import get_node_ip_address
from ray.util.state import list_actors


@serve.deployment(autoscaling_config=dict(min_replicas=1, max_replicas=1),
                  ray_actor_options=dict(num_cpus=0.1))
class NodeHealthTracker:
    """Maintains a list of bad nodes, as reported by replicas that call the report_bad_node func.
    Bad nodes are those that fail GPU/CUDA health check.
    What's the purpose? Because when an embedding model replica becomes unhealthy
    (due to GPU/CUDA issues), we want Ray to kill all replicas running on the node.
    When Ray detects that there are no running replicas on a node, the node is stopped
    and replaced with a new one.
    """
    def __init__(self, tracked_model_deployments: List[str] = None):
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.tracked_model_deployments = tracked_model_deployments or []
        self.bad_gpu_node_ips: Set[str] = set()
        self.lock = threading.RLock()
        replica_context = serve.get_replica_context()
        self.deployment_name = replica_context.deployment
        self.replica_actor_name = replica_context.replica_id.to_full_id_str()
        self.node_ip = get_node_ip_address()
        self.logger.info(f"Successfully initialized NodeHealthTracker. Tracked model deployments: {self.tracked_model_deployments}")

    async def report_bad_gpu_node(self, node_ip: str, deployment_name: str, replica_actor_name: str):
        with self.lock:
            if node_ip not in self.bad_gpu_node_ips:
                self.bad_gpu_node_ips.add(node_ip)
                self.logger.warning(
                    f"[Bad GPU node reported] Deployment: {deployment_name}, Replica: {replica_actor_name}, Node IP: {node_ip}"
                )

    async def is_bad_gpu_node(self, node_ip: str) -> bool:
        with self.lock:
            return node_ip in self.bad_gpu_node_ips

    async def is_bad_gpu_or_no_tracked_model_on_node(self, node_ip: str):
        return (await self.is_bad_gpu_node(node_ip) or
                not await self.is_tracked_model_running_on_node(node_ip))

    async def check_health(self):
        """Called periodically by Ray Serve. Used here to clean up stale node IDs."""
        try:
            current_node_ips = {node["NodeManagerAddress"] for node in ray.nodes() if node["Alive"]}
            with self.lock:
                stale_nodes = self.bad_gpu_node_ips - current_node_ips
                if stale_nodes:
                    self.logger.info(f"Removing stale bad node_ips: {stale_nodes}")
                self.bad_gpu_node_ips.intersection_update(current_node_ips)
            self.logger.info(f"Current nodes: {current_node_ips}. Bad GPU nodes: {self.bad_gpu_node_ips}.")
        except Exception as e:
            raise RuntimeError(f"An error occurred in check_health during bad node cleanup: {e}")

    async def is_tracked_model_running_on_node(self, node_ip: str) -> bool:
        """
        Return True if there is at least one replica of any of the self.tracked_model_deployments
        running on the specified node_ip.
        """
        try:
            target_node_id = next(node["NodeID"] for node in ray.nodes() if node["Alive"] and node["NodeManagerAddress"] == node_ip)
            assert target_node_id, f"No node found with IP {node_ip}"
            prefixes = tuple(f"SERVE_REPLICA::{d}" for d in self.tracked_model_deployments)

            for actor in list_actors(detail=False):
                if (actor.state in ["DEPENDENCIES_UNREADY", 'PENDING_CREATION', 'ALIVE', 'RESTARTING'] and
                        actor.node_id == target_node_id and
                            actor.name.startswith(prefixes)):
                    self.logger.info(f"There is at least one replica of tracked_deployments={self.tracked_model_deployments} "
                        f"running on node {node_ip}")
                    return True

            self.logger.info(f"No replicas of tracked deployments={self.tracked_model_deployments} running on node: {node_ip}.")
            return False
        except Exception as e:
            self.logger.error(f"An error occurred while checking replicas on node {node_ip}: {e}")
            return False