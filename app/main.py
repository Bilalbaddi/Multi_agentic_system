import os
import sys
import subprocess
import threading
import time
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.common.logging import get_logger
from app.common.custom_exception import CustomException

logger=get_logger(__name__)

load_dotenv()

def _child_env() -> dict:
    env = os.environ.copy()
    existing_pythonpath = env.get("PYTHONPATH", "")
    project_path = str(PROJECT_ROOT)
    env["PYTHONPATH"] = f"{project_path}{os.pathsep}{existing_pythonpath}" if existing_pythonpath else project_path
    return env

def run_backend():
    try:
        logger.info("starting backend service..")
        subprocess.run(
            [sys.executable , "-m" , "uvicorn" , "app.backend.api:app" , "--host" , "127.0.0.1" , "--port" , "9999"],
            check=True,
            cwd=str(PROJECT_ROOT),
            env=_child_env()
        )
    except Exception as e:
        logger.error("Problem with backend service")
        raise CustomException("Failed to start backend" , e)
    
def run_frontend():
    try:
        logger.info("Starting Frontend service")
        subprocess.run(
            [sys.executable , "-m" , "streamlit" , "run" , str(PROJECT_ROOT / "app" / "frontend" / "ui.py")],
            check=True,
            cwd=str(PROJECT_ROOT),
            env=_child_env()
        )
    except Exception as e:
        logger.error("Problem with frontend service")
        raise CustomException("Failed to start frontend" , e)
    
if __name__=="__main__":
    try:
        threading.Thread(target=run_backend).start()
        time.sleep(2)
        run_frontend()

    except KeyboardInterrupt:
        logger.info("Shutdown requested by user")
    except CustomException as e:
        logger.exception(f"CustomException occured : {str(e)}")


    