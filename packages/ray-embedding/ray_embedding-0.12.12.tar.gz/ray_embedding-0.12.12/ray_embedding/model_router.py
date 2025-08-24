import asyncio
import logging
import time
from typing import Optional, Dict, List, Tuple

from fastapi import FastAPI, HTTPException
from ray import serve
from ray.serve.handle import DeploymentHandle
from ray.util import get_node_ip_address

from ray_embedding.dto import DeployedModel, EmbeddingRequest, EmbeddingResponse

web_api = FastAPI(title="Ray Embeddings - OpenAI-compatible API")

@serve.deployment
@serve.ingress(web_api)
class ModelRouter:
    def __init__(self, deployed_models: Dict[str, DeployedModel],
                 path_prefix: List[str], max_concurrency: Optional[int] = 32,
                 node_health_tracker: Optional[DeploymentHandle] = None):
        assert deployed_models, "models cannot be empty"
        assert path_prefix, "path_prefix cannot be empty"

        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.deployed_models = deployed_models
        self.path_prefix = [item.removeprefix("/").removesuffix("/") for item in path_prefix]
        self.max_concurrency = max_concurrency
        self.rate_limiter = asyncio.Semaphore(self.max_concurrency)
        self.available_models = [
            {"id": str(item),
             "object": "model",
             "created": int(time.time()),
             "owned_by": "openai",
             "permission": []} for item in self.deployed_models.keys()
        ]
        self.logger.info(f"Successfully registered models: {self.available_models}")
        self.node_health_tracker = node_health_tracker
        replica_context = serve.get_replica_context()
        self.deployment_name = replica_context.deployment
        self.replica_actor_name = replica_context.replica_id.to_full_id_str()
        self.node_ip = get_node_ip_address()
        self.logger.info(f"Successfully initialized model router. "
                         f"Deployment name: {self.deployment_name}, Replica actor name: {self.replica_actor_name}, Node IP: {self.node_ip}")

    async def _compute_embeddings_from_resized_batches(self, model: str, inputs: List[str], dimensions: Optional[int] = None):
        deployed_model = self.deployed_models[model]
        model_handle = deployed_model.deployment_handle
        batch_size = deployed_model.batch_size
        num_retries = deployed_model.num_retries

        # Resize the inputs into batch_size items, and dispatch in parallel
        batches = [inputs[i:i+batch_size] for i in range(0, len(inputs), batch_size)]
        if len(inputs) > batch_size:
            self.logger.info(f"Original input (length {len(inputs)} was resized "
                             f"to {len(batches)} mini-batches, each with max length {batch_size}.")

        # Call embedding model replicas in parallel (rate-limited)
        tasks = [self._compute_embeddings_rate_limited(model_handle, batch, dimensions) for batch in batches]
        all_results = await asyncio.gather(*tasks, return_exceptions=True)

        # Retry any failed model calls
        for i, result in enumerate(all_results):
            if isinstance(result, Exception):
                self.logger.warning(f"Retrying mini-batch {i} due to exception: {result}")
                result_retried, retries = await self._retry_failed_embedding_call(model_handle, batches[i], dimensions,
                                                                                  num_retries)
                if retries >= num_retries and (isinstance(result_retried, Exception) or result_retried is None):
                    raise result_retried or ValueError(f"Failed to compute `{model}` embeddings for mini-batch {i} after {num_retries} retries.")

                all_results[i] = result_retried

        # Flatten the results because `all_results` is a list of lists
        self.logger.info(f"Successfully computed embeddings from {len(batches)} mini-batches")
        return [emb for result in all_results for emb in result]

    async def _compute_embeddings_rate_limited(self, model_handle: DeploymentHandle, batch: List[str], dimensions: int):
        async with self.rate_limiter:
            return await model_handle.remote(batch, dimensions)

    async def _retry_failed_embedding_call(self,  model_handle: DeploymentHandle, batch: List[str],
                                           dimensions: Optional[int] = None, num_retries: Optional[int] = 2) \
            -> Tuple[List[List[float]] | Exception, int]:

        result_retried, retries = None, 0
        while retries < num_retries:
            try:
                result_retried = await model_handle.remote(batch, dimensions)
            except Exception as e:
                result_retried = e
                self.logger.warning(e)
            finally:
                retries += 1
            if not isinstance(result_retried, Exception) and result_retried is not None:
                break

        return result_retried, retries

    @web_api.post("/{path_prefix}/v1/embeddings", response_model=EmbeddingResponse)
    async def compute_embeddings(self, path_prefix: str, request: EmbeddingRequest):
        try:
            assert path_prefix in self.path_prefix, f"The API path prefix specified is invalid: '{path_prefix}'"
            assert request.model in self.deployed_models, f"The model specified is invalid: {request.model}"

            inputs = request.input if isinstance(request.input, list) else [request.input]
            self.logger.info(f"Computing embeddings for a batch of {len(inputs)} texts using model: {request.model}")
            embeddings = await self._compute_embeddings_from_resized_batches(request.model, inputs, request.dimensions)
            response_data = [
                {"index": idx, "embedding": emb}
                for idx, emb in enumerate(embeddings)
            ]
            return EmbeddingResponse(object="list", data=response_data, model=request.model)
        except Exception as e:
            status_code = 400 if isinstance(e, AssertionError) else 500
            self.logger.error(f"Failed to create embeddings: {e}")
            raise HTTPException(status_code=status_code, detail=str(e))

    @web_api.get("/{path_prefix}/v1/models")
    async def list_models(self, path_prefix: str):
        """Returns the list of available models in OpenAI-compatible format."""
        if path_prefix not in self.path_prefix:
            raise HTTPException(status_code=400, detail=f"The API path prefix specified is invalid: '{path_prefix}'")
        return {"object": "list", "data": self.available_models}

    async def check_health(self):
        if self.node_health_tracker:
            if await self.node_health_tracker.is_bad_gpu_or_no_tracked_model_on_node.remote(self.node_ip):
                raise RuntimeError(f"The node {self.node_ip} is marked bad, or there are no tracked models running on it.")
