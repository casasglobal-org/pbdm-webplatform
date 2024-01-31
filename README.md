# pbdm-workflow

Workflow to run PBDM executables compiled from Pascal source code.

## Trello board

Here we keep track of things:

[PBDM-Workflow Trello board](https://trello.com/b/449PzQuo/pbdm-workflow)

## How to run serverless project
Navigate to the foldere where is the serverless.yaml file and run:

```
sls deploy 
```
N.B you have to previously set aws credentials in order to launch the cloudformation stack creation

## How to run container locally
In order to launch docker container locally you have to install Docker Desktop.

Then, you have to run the following commands:

```
cd mgd-olive-scripts-main/casas_pbdm_workflow/processing/resources/worker-container
docker build -t app . 
docker compose up --no-deps -d app
```

N.B you have to use the Dockerfile with ENVs defined (NOT remove the other Dockerfile, just rename it)

## File tree
```
├── pre-processing
│   ├── agmerra_review.py -> pre-processing for agmerra files
│   ├── bounding_box.py -> cut agera5 files
│   ├── generate_points.py -> generate punti.dat file for Puglia (you can use it for different location changing the latitudes and longitudes)
│   ├── pre-processing-puglia.py -> pre-processing for agera5 files and Puglia location
│   ├── pre-processing.py -> same of above but for Andalusia (only change lat&lon values)
List of points for different locations:
│   ├── punti_di_terra_Spain_Portugal.dat 
│   ├── punti_di_terra_agera5_andalusia.dat
│   ├── punti_di_terra_agera5_colombia.dat

├── processing
│   ├── README.md
│   ├── package-lock.json
│   ├── package.json
│   ├── resources
│   │   ├── container
│   │   │   ├── Dockerfile
│   │   │   ├── MIRRORS.txt
│   │   │   ├── Makefile
│   │   │   ├── README.md
│   │   │   ├── apk-tools-static-2.10.6-r0.apk
│   │   │   ├── etc
│   │   │   │   └── apk
│   │   │   └── repositories
│   │   │   ├── sbin
│   │   │   │   └── apk.static
│   │   │   └── winetricks.sh
│   │   ├── dynamodb.yml
│   │   ├── ecs.yml
│   │   ├── iam-roles.yml
│   │   ├── s3.yml
│   │   ├── stepFunctions.yml
│   │   ├── vpc.yml
│   │   └── worker-container
│   ├── Dockerfile
│   ├── Dockerfile-build
│   ├── build.sh
│   ├── docker-compose.yml
│   ├── etc
│   │   └── apk
│   └── repositories
│   ├── pbdm
│   │   ├── Olive.ini
│   │   ├── Olive_no-w.exe
│   │   ├── dat
│   │   │   ├── VEN.dat
│   │   │   ├── Venezuela.dat
│   │   │   └── agmerra_grid_with_coords_admin_code.txt
│   │   ├── lut
│   │   │   ├── CAMYAAB2.002
│   │   │   ├── CAMYAAE5.006
│   │   │   ├── CAMYAAH8.001
│   │   │   ├── CAMYAAH8.zip
│   │   │   ├── CAMYAAJ1.002
│   │   │   ├── CAMYAAK2.001
│   │   │   ├── CAYOAAA2.014
│   │   │   ├── CAYOAAB3.012
│   │   │   ├── CAYUAAA5.014
│   │   │   ├── Copy of yellowstar.txt
│   │   │   ├── Olive.exe
│   │   │   ├── OliveSoilWater.txt
│   │   │   ├── OliveSoilWater_original.txt
│   │   │   ├── YSTSoilWater.txt
│   │   │   ├── YSTSoilWater.txt.$$$
│   │   │   ├── YellowStar.txt
│   │   │   ├── agmerra_review.py
│   │   │   ├── get_agmerra.py
│   │   │   ├── y.txt
│   │   │   ├── yellow.txt
│   │   │   └── ystsoilwater.bak
│   │   └── pbdm-worker.py
│   ├── run.sh
│   ├── sbin
│   │   ├── apk.static
│   │   └── apk.static.dis
│   ├── winetricks
│   ├── winetricks.sh
│   └── winetricks.sh.dis
│   └── serverless.yml
└── temporary_infrastructure
    ├── functions
    │   ├── api.py
    │   └── request-api.py
    ├── node_modules
    │   ├── 2-thenable
    │   │   ├── CHANGELOG.md
    │   │   ├── LICENSE
    │   │   ├── README.md
    │   │   ├── index.js
    │   │   ├── package.json
    │   │   └── test
    │   └── index.js
    │   ├── @colors
    │   │   └── colors
    │   ├── LICENSE
    │   ├── README.md
    │   ├── examples
    │   │   ├── normal-usage.js
    │   │   └── safe-string.js
    │   ├── index.d.ts
    │   ├── lib
    │   │   ├── colors.js
    │   │   ├── custom
    │   │   │   ├── trap.js
    │   │   │   └── zalgo.js
    │   │   ├── extendStringPrototype.js
    │   │   ├── index.js
    │   │   ├── maps
    │   │   │   ├── america.js
    │   │   │   ├── rainbow.js
    │   │   │   ├── random.js
    │   │   │   └── zebra.js
    │   │   ├── styles.js
    │   │   └── system
    │   ├── has-flag.js
    │   └── supports-colors.js
    │   ├── package.json
    │   ├── safe.d.ts
    │   ├── safe.js
    │   └── themes
    │       └── generic-logging.js
```

## API utilization:

In order to launch an execution, you have to send this api call:

- https://{{api-endpoint}}.execute-api.{{region}}.amazonaws.com/dev/dataset/{{dataset}}/workflow/{{wf}}?country={{country}}&sdate={{sdate}}&model={{model}}&output_time_interval={{output_time_interval}}&edate={{edate}}&resolution{{resolution}}

where: 
- dataset can take the values: agmerra or AgERA5
- wf can take the value: pbdm
- country can take the values:
    - ESP-POR if dataset value is equal to agmerra
    - ESP-AN, ITA-PUG-250m, ITA-PUG-1km
- sdate can take the values:
    - from 1979 to 2022 for AgERA5
    - from 1980 to 2010 for agmerra 
    - the format is YYYY/MM/DD
- edate can take the values:
    - from 1979 to 2022 for AgERA5
    - from 1980 to 2010 for agmerra 
    - the format is YYYY/MM/DD
- model can take the value: olive
- output_time_interval can take the value: 365
- resolution can take values:
    - standard-250m, zeuli-250m, uliveti-250m if country is ITA-PUG-250m
    - standard-1km if country is ITA-PUG-1km

In order to check the worker state, you have to send this api call:

- https://{{api-endpoint}}.execute-api.{{region}}.amazonaws.com/dev/{{wf}}/request?id={{id}}&dataset={{dataset}}

where id is the request-id returned from the previous api call
