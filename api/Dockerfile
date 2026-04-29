FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# On copie tout le dossier api dans le conteneur
COPY . .


# LA MODIFICATION EST ICI : on pointe vers api.app.main
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]