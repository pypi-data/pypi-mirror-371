import os
from typing import Optional

import torch
from ray.serve import Application
from ray.serve.handle import DeploymentHandle

from ray_embedding.dto import AppConfig, ModelDeploymentConfig, DeployedModel
from ray_embedding.embedding_model import EmbeddingModel
from ray_embedding.model_router import ModelRouter
from ray_embedding.node_health import NodeHealthTracker

DEFAULT_NODE_HEALTH_CHECK_INTERVAL_S = 30


def build_model(model_config: ModelDeploymentConfig, node_health_tracker: Optional[DeploymentHandle] = None) -> DeployedModel:
    deployment_name = model_config.deployment
    model = model_config.model
    served_model_name = model_config.served_model_name or os.path.basename(model)
    device = model_config.device
    backend = model_config.backend or "torch"
    matryoshka_dim = model_config.matryoshka_dim
    trust_remote_code = model_config.trust_remote_code or False
    model_kwargs = model_config.model_kwargs or {}
    cuda_memory_flush_threshold = model_config.cuda_memory_flush_threshold or 0.8

    if "torch_dtype" in model_kwargs:
        torch_dtype = model_kwargs["torch_dtype"].strip()
        if torch_dtype == "float16":
            model_kwargs["torch_dtype"] = torch.float16
        elif torch_dtype == "bfloat16":
            model_kwargs["torch_dtype"] = torch.bfloat16
        elif torch_dtype == "float32":
            model_kwargs["torch_dtype"] = torch.float32
        else:
            raise ValueError(f"Invalid torch_dtype: '{torch_dtype}'")

    deployment = EmbeddingModel.options(name=deployment_name).bind(model=model,
                                                                   served_model_name=served_model_name,
                                                                   device=device,
                                                                   backend=backend,
                                                                   matryoshka_dim=matryoshka_dim,
                                                                   trust_remote_code=trust_remote_code,
                                                                   model_kwargs=model_kwargs,
                                                                   cuda_memory_flush_threshold=cuda_memory_flush_threshold,
                                                                   node_health_tracker=node_health_tracker
                                                                   )
    return DeployedModel(model=served_model_name,
                         deployment_handle=deployment,
                         batch_size=model_config.batch_size,
                         num_retries=model_config.num_retries
                         )


def build_app(args: AppConfig) -> Application:
    model_router, models = args.model_router, args.models
    assert model_router and models
    assert model_router.path_prefix

    node_health_check_interval_s = args.node_health_check_interval_s or DEFAULT_NODE_HEALTH_CHECK_INTERVAL_S
    node_health_tracker = NodeHealthTracker.options(health_check_period_s=node_health_check_interval_s).bind()
    deployed_models = {model_config.served_model_name: build_model(model_config, node_health_tracker=node_health_tracker)
                       for model_config in models}
    router = (ModelRouter.options(name=model_router.deployment)
              .bind(deployed_models=deployed_models,
                    path_prefix=model_router.path_prefix,
                    node_health_tracker=node_health_tracker))
    return router
