#!/bin/sh

cd filesystem/pbdm/

cp -r ../../lut/ ./lut
cp ../../Olive.ini ../../Olive.exe ../../pbdm-worker.py ./
mkdir output
find ./ -type f -exec chmod 777 {} \;
python3 pbdm-worker.py
find . -mindepth 1 \( ! -name daily -a ! -name txtfiles -a ! -name punti.dat \) | grep -vE './daily|./txtfiles' | xargs rm -rf

#cd ..
#rm -r $requestId