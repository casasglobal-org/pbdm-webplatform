# Usa l'immagine ufficiale di Python come immagine di base
FROM python:3.10

# Imposta la directory di lavoro nel container
WORKDIR /app

# Installa pacchetti di sistema necessari per cdsapi e per gestire archivi ZIP
RUN apt-get update && \
    apt-get install -y --no-install-recommends cdo && \
    rm -rf /var/lib/apt/lists/* # Aggiunta la pulizia della cache di apt per ridurre le dimensioni dell'immagine

# Copia il file delle dipendenze Python nella directory corrente del container
COPY requirements.txt .

# Installa le dipendenze Python specificate in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copia il tuo script Python e altri file necessari nella directory di lavoro del container
COPY src/ /app/

# Specifica il comando per eseguire lo script Python quando il container viene lanciato
CMD ["python", "./merge.py"]
