import json
import logging
import signal
import time
from typing import Any

try:
    import redis as valkey  # valkey is redis-compatible
except ImportError:
    valkey = None

from sids_ai.inference.orchestrator import analyze_image
from sids_ai.schemas.image import AnalysisRequest

logger = logging.getLogger(__name__)

class ValkeyWorker:
    def __init__(self, valkey_url: str, stream_name: str = "ai_analysis_stream", group_name: str = "ai_service_group", consumer_name: str = "worker-1"):
        self.valkey_url = valkey_url
        self.stream_name = stream_name
        self.group_name = group_name
        self.consumer_name = consumer_name
        self.running = False
        
        if valkey:
            self.client = valkey.Redis.from_url(valkey_url, decode_responses=True)
            # Ensure stream and group exist
            try:
                self.client.xgroup_create(self.stream_name, self.group_name, id="0", mkstream=True)
            except valkey.exceptions.ResponseError as e:
                if "BUSYGROUP" not in str(e):
                    raise
        else:
            self.client = None

    def start(self):
        self.running = True
        logger.info(f"Starting ValkeyWorker {self.consumer_name} on stream {self.stream_name}")
        
        # Graceful shutdown handlers
        signal.signal(signal.SIGINT, self.stop)
        signal.signal(signal.SIGTERM, self.stop)

        while self.running:
            if not self.client:
                logger.warning("Valkey/Redis client not available. Sleeping...")
                time.sleep(5)
                continue
                
            try:
                # Blocking read, wait up to 5000ms
                messages = self.client.xreadgroup(
                    self.group_name,
                    self.consumer_name,
                    {self.stream_name: ">"},
                    count=10,
                    block=5000
                )
                
                if not messages:
                    continue
                    
                for stream, stream_messages in messages:
                    for message_id, payload in stream_messages:
                        try:
                            self.process_job(payload.get("data", "{}"))
                            self.client.xack(self.stream_name, self.group_name, message_id)
                        except Exception as e:
                            logger.error(f"Failed to process message {message_id}: {e}")
                            
            except Exception as e:
                logger.error(f"Error reading from stream: {e}")
                time.sleep(2)
                
        logger.info("Worker stopped gracefully.")

    def stop(self, signum=None, frame=None):
        logger.info("Shutdown signal received. Stopping worker...")
        self.running = False

    def process_job(self, job_payload: str) -> dict[str, Any]:
        try:
            job = json.loads(job_payload)
            if job.get("type") != "AI_ANALYSIS":
                logger.warning(f"Unknown job type: {job.get('type')}")
                return {"status": "IGNORED"}
            
            # Map job dict to AnalysisRequest
            request = AnalysisRequest(**job.get("request", {}))
            response = analyze_image(request)
            
            # Here we might write the result back to another stream or DB
            logger.info(f"Processed analysis {request.analysisId} in {response.latencyMs}ms")
            return {"status": "SUCCESS", "jobId": job.get("jobId"), "response": response.model_dump()}
        except Exception as e:
            logger.error(f"Job processing failed: {e}")
            return {"status": "ERROR"}

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    worker = ValkeyWorker("redis://localhost:6379/0")
    worker.start()
