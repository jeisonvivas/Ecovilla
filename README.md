# EcoVilla - Proyecto completo (Conectado a tu BD local)

## Qué contiene
- `backend/` - API en Flask que usa SQLAlchemy (automap) para reflejar tus tablas existentes.
- `frontend/` - HTML + JS para registrar reciclajes y ver ranking.
- `.env.example` - ejemplo de variable de entorno para tu conexión.

## Requisitos
- Python 3.8+
- PostgreSQL local con la base `proyect13` (usuario: postgres, contraseña: 921535)

## Instalación rápida (local)
```bash
cd backend
python -m venv venv
source venv/bin/activate    # Linux/Mac
venv\Scripts\activate     # Windows (PowerShell)
pip install -r requirements.txt
# (opcional) exporta la URL de la base (si no quieres usar la que viene por defecto)
export DATABASE_URL="postgresql+psycopg2://postgres:921535@localhost:5432/proyect13"
python app.py
```
El backend levantará en http://localhost:5000

Para el frontend puedes abrir `frontend/index.html` directamente en el navegador
o servirlo con `python -m http.server` desde la carpeta `frontend`.

## Notas
- El backend usa **automap** para reflejar tus tablas actuales (`usuarios`, `reciclaje`, `bonificaciones`).
- Cuando se registra un reciclaje (`POST /reciclaje`) se calcula una **recompensa** (puntos)
  según el material y se inserta un registro en `bonificaciones` para ese usuario.
- Revisa y ajusta los valores de puntos por material en `backend/app.py` (diccionario `POINTS_PER_KG`).
