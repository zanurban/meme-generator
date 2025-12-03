# Uporabimo uradno Python 3.12 slim sliko
FROM python:3.12-slim

# Nastavimo delovni direktorij
WORKDIR /app

# Namestimo sistemske odvisnosti (za Pillow in fontove)
RUN apt-get update && apt-get install -y \
    fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

# Kopiramo requirements.txt in namestimo Python odvisnosti
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Kopiramo vse datoteke v kontejner
COPY . .

# Nastavimo okoljske spremenljivke
ENV FLASK_APP=app.py
ENV PYTHONUNBUFFERED=1
ENV PORT=5000

# Odpiramo port 5000
EXPOSE 5000

# Ustvarimo mapo za nalaganje slik
RUN mkdir -p /app/uploads

# Nastavimo CMD za zagon aplikacije
CMD ["python", "app.py"]

