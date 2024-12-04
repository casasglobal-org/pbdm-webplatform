#!/bin/sh
pwd
ls -la
cd filesystem/pbdm/
echo $model
cp -r ../../lut/ ./lut
cp ../../${model}.ini ../../${model}.exe ../../pbdm-worker.py ./
mkdir output
pwd
echo 'dentro run local'
find ./ -type f -exec chmod 777 {} \;
ls
python3 pbdm-worker.py
find . -mindepth 1 \( ! -name daily -a ! -name txtfiles -a ! -name punti.dat \) | grep -vE './daily|./txtfiles' | xargs rm -rf

#cd ..
#rm -r $requestId