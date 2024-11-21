#!/bin/bash

docker-compose down

cd ./container

# Caricamento delle variabili d'ambiente da un file di configurazione
if [ -f ../env.config ]; then
    export $(cat ../env.config | sed 's/#.*//g' | xargs)
else
    echo "File di configurazione env.config non trovato."
    exit 1
fi

# Esecuzione di Docker Compose
docker compose up --no-deps -d app
