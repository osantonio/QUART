# main.py — producción (Dokploy / Hypercorn)

import os

from hypercorn.config import Config

from app import create_app

app = create_app()

config = Config()
config.bind = [f"0.0.0.0:{os.environ.get('PORT', 2000)}"]
config.worker_count = int(os.environ.get('WORKERS', 2))
config.accesslog = "-"
config.errorlog = "-"
