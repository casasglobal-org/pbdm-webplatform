#!/bin/sh
set -e

#aws s3 cp s3://dev-pbdm-workflow/agmerra/p/ESP-AN/points/agmerra_10_191_ESP.txt ./agmerra_10_191_ESP.txt
cd filesystem/pbdm/
mkdir $requestId
cp -r ../../lut/ ./$requestId/lut
cp ../../Olive.ini ../../Olive.exe ../../pbdm-worker.py ./$requestId/
echo "dentro pbdm"
cd $requestId/
echo "dentro $requestId"
mkdir txtfiles && mkdir daily && mkdir output
echo "lancio worker"
python3 pbdm-worker.py > /proc/1/fd/1 2>&1

# Verifica il codice di uscita dello script Python
if [ $? -ne 0 ]; then
    echo "Lo script Python è terminato con errore"
    # Termina lo script con un codice di errore
    exit 1
fi

# Resto dello script, se necessario...
cd ..
rm -r $requestId
# Termina con successo se non ci sono stati errori
exit 0

