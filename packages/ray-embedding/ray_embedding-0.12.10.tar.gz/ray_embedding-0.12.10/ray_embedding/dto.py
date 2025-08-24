import dataclasses
from typing import Union, List, Optional, Dict, Any
from pydantic import BaseModel
from ray.serve.handle import DeploymentHandle


class EmbeddingRequest(BaseModel):
    """Schema of embedding requests (compatible with OpenAI)"""
    model: str  # Model name (for compatibility; only one model is used here)
    input: Union[str, List[str]]  # List of strings to embed
    dimensions: Optional[int] = None


class EmbeddingResponse(BaseModel):
    """Schema of embedding response (compatible with OpenAI)"""
    object: str
    data: List[dict]  # Embedding data including index and vector
    model: str  # Model name used for embedding


class ModelRouterConfig(BaseModel):
    deployment: str
    path_prefix: List[str] = []
    max_concurrency: int = 32


class ModelDeploymentConfig(BaseModel):
    model: str
    served_model_name: str
    batch_size: Optional[int] = 8
    num_retries: Optional[int] = 2
    device: Optional[str] = None
    backend: Optional[str] = None
    matryoshka_dim: Optional[int] = 768
    trust_remote_code: Optional[bool] = False
    model_kwargs: Optional[Dict[str, Any]] = {}
    cuda_memory_flush_threshold: Optional[float] = 0.8
    deployment: str


class ReplicaState(BaseModel):
    deployment_name: str
    replica_actor_name: str
    node_ip: str
    state: Optional[str] = None


class AppConfig(BaseModel):
    model_router: ModelRouterConfig
    node_health_check_interval_s: Optional[int] = 30
    models: List[ModelDeploymentConfig]


@dataclasses.dataclass
class DeployedModel:
    model: str
    deployment_handle: DeploymentHandle
    batch_size: int
    num_retries: Optional[int] = 2
