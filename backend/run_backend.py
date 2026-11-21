import os
import sys
import io

# Force stdout/stderr to UTF-8 encoding on Windows console
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

os.environ["PYTHONIOENCODING"] = "utf-8"

if __name__ == "__main__":
    import uvicorn
    from app.main import app
    
    print("\n======================================================================")
    print("STARTING CAMPUSAID BACKEND SERVER")
    print("======================================================================")
    port = int(os.getenv("PORT", "8000"))
    print(f"Server listening on 0.0.0.0:{port}")
    print("======================================================================\n")

    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
