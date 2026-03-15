# ./main.py

from app import create_app
import os

app = create_app()

if __name__ == "__main__":
    # Escuchar en 0.0.0.0 es obligatorio en Docker/Dokploy
    # El puerto lo ideal es que sea dinámico o coincida con Dokploy
    port = int(os.environ.get("PORT", 5000)) 
    app.run(host='0.0.0.0', port=port, debug=False)
