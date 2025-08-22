from __future__ import annotations

import os
import uvicorn


def main():
    # Ensure log dir exists
    log_dir = os.environ.get("LLM_LOG_DIR")
    if log_dir:
        os.makedirs(log_dir, exist_ok=True)
    uvicorn.run("dashboard.server:app", host="127.0.0.1", port=8000, reload=False)


if __name__ == "__main__":
    main()


