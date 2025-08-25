import logging

from fastapi import FastAPI
from ray import serve

from folder_classifier.classifier import FolderClassifier
from folder_classifier.dto import ModelConfig, FolderClassificationRequest, FolderClassificationResponse

web_api = FastAPI(title=f"Folder Classifier API")

@serve.deployment
@serve.ingress(web_api)
class FolderClassifierAPI:
    def __init__(self, model_config: ModelConfig):
        assert model_config, "model_config is required"
        assert model_config.app_name and model_config.deployment, "Invalid ModelConfig values"
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Initializing Folder Classifier model: {model_config}")
        model_handle = serve.get_deployment_handle(app_name=model_config.app_name, deployment_name=model_config.deployment)
        self.classifier = FolderClassifier(model_handle)
        self.logger.info(f"Successfully initialized Folder Classifier API")

    @web_api.post("/predict")
    async def predict(self, request: FolderClassificationRequest) -> FolderClassificationResponse:
        self.logger.info(f"Received request: {request}")
        category, reasoning = await self.classifier.predict(request)
        return FolderClassificationResponse(category=category, reasoning=reasoning)
