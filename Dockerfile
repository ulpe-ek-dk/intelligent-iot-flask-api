FROM python:3.11-slim

# Arbejdsmappe i containeren
WORKDIR /app

# Kopiér requirements og installér
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Kopiér resten af koden
COPY . .

# Flask skal kunne lytte på port 5000
EXPOSE 5000

# Kør appen
CMD ["python", "app.py"]
