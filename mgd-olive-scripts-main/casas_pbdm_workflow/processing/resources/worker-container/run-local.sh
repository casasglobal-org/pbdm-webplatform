#!/bin/sh
#cd filesystem/pbdm/
ls
mkdir $requestId
cp -r ../../lut/ ./$requestId/lut
cp ../../Olive.ini ../../Olive.exe ../../pbdm-worker.py ./$requestId/
cd $requestId/
mkdir txtfiles && mkdir daily && mkdir output
#sostituisci con file su efs
aws s3 cp --recursive s3://dev-pbdm-workflow/$dataset/p/$country/points/ ./txtfiles
aws s3 cp s3://dev-pbdm-workflow/$dataset/p/$country/coords/punti.dat punti_250m.dat
python3 pbdm-worker.py
sleep 300
cd ..
rm -r $requestId