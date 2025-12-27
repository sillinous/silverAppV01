import logging
import os
from ximilar.client import RecognitionClient

logger = logging.getLogger(__name__)

def analyze_image_for_hallmarks(image_path: str) -> dict:
    """
    Analyzes an image to identify silver hallmarks using the Ximilar AI API.

    This function requires the following environment variables to be set:
    - `XIMILAR_API_TOKEN`
    - `XIMILAR_WORKSPACE_ID`
    - `XIMILAR_TASK_ID`

    Args:
        image_path: The local path to the image file.

    Returns:
        A dictionary containing the analysis from the Ximilar API.
    """
    api_token = os.getenv("XIMILAR_API_TOKEN")
    workspace_id = os.getenv("XIMILAR_WORKSPACE_ID")
    task_id = os.getenv("XIMILAR_TASK_ID")

    if not all([api_token, workspace_id, task_id]):
        error_msg = (
            "One or more Ximilar environment variables are not set: "
            "XIMILAR_API_TOKEN, XIMILAR_WORKSPACE_ID, XIMILAR_TASK_ID"
        )
        logger.error(error_msg)
        raise ValueError(error_msg)

    client = RecognitionClient(token=api_token, workspace=workspace_id)
    
    result = client.recognize(task_id=task_id, records=[{"_file": image_path}])

    return result

