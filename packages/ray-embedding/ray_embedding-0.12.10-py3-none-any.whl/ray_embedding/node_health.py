import logging
import threading
from typing import Set

import ray
from ray import serve


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
    def __init__(self):
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.bad_node_ips: Set[str] = set()
        self.lock = threading.RLock()
        self.logger.info(f"Successfully initialized NodeHealthTracker.")

    async def report_bad_node(self, node_ip: str, deployment_name: str, replica_actor_name: str):
        with self.lock:
            if node_ip not in self.bad_node_ips:
                self.bad_node_ips.add(node_ip)
                self.logger.warning(
                    f"[Bad Node Reported] Deployment: {deployment_name}, Replica: {replica_actor_name}, Node IP: {node_ip}"
                )

    async def is_bad_node(self, node_ip: str) -> bool:
        with self.lock:
            return node_ip in self.bad_node_ips

    async def check_health(self):
        """Called periodically by Ray Serve. Used here to clean up stale node IDs."""
        try:
            current_node_ips = {node["NodeManagerAddress"] for node in ray.nodes() if node["Alive"]}
            with self.lock:
                stale_nodes = self.bad_node_ips - current_node_ips
                if stale_nodes:
                    self.logger.info(f"Removing stale bad node_ips: {stale_nodes}")
                self.bad_node_ips.intersection_update(current_node_ips)
            self.logger.info(f"Current nodes: {current_node_ips}. Bad nodes: {self.bad_node_ips}.")
        except Exception as e:
            raise RuntimeError(f"Exception in check_health during bad node cleanup: {e}")