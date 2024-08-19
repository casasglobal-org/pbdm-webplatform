# pbdm-workflow

Workflow to run PBDM executables compiled from Pascal source code.

## Description

This repository includes code for the CASAS-PBDM Web API workflow, initially developed for the case study on olive/olive oil under the MED-GOLD project  (<https://doi.org/10.3030/776467>), as part of the MED-GOLD ICT ecosystem for climate services in agriculture (<https://ec.europa.eu/info/funding-tenders/opportunities/portal/screen/opportunities/horizon-results-platform/32534;keyword=med-gold>), and further developed under the TEBAKA project (<https://www.dtascarl.org/en/projects-and-initiatives/use-case-technology-transfer/tebaka/>).

The MED-GOLD project has received funding from the European Union's Horizon 2020 Research and Innovation programme under Grant agreement No. 776467. Project TEBAKA (project ID: ARS01_00815) was co-funded by the European Union - ERDF and ESF, “PON Ricerca e Innovazione 2014-2020”.

The following folders:

```
/mgd-olive-scripts-main/casas_pbdm_coffee/
/mgd-olive-scripts-main/casas_pbdm_coffee/
```

include code developed for analyzing the olive and coffee systems using physiologically based demographic models (PBDMs) in a geographic information system (GIS) context.

The following folder:

```
/mgd-olive-scripts-main/casas_pbdm_workflow/
```

includes code for the CASAS-PBDM Web API workflow to run the Windows executable for the olive PBDM system model compiled from the Pascal source code (see below).

A short introduction and description follows that provides context for the CASAS-PBDM related code:

CASAS Global (Center for the Analysis of Sustainable Agricultural Systems, see <http://www.casasglobal.org/>) physiologically based demographic models (CASAS-PBDMs) are one of the key existing technology components of the MED-GOLD project (Turning climate-related information into added value for traditional MEDiterranean Grape, OLive and Durum wheat food systems, see <https://doi.org/10.3030/776467>). Note that CASAS Global CEO Andrew Paul Gutierrez was part of the project's External Advisory Committee. The coffee system has been already developed using the PBDM approach and provides some basic info about the crop in Colombia, such as main climate-related problems including key pests. This info would serve as a starting point for developing a climate service for coffee (see Task 6.2). The model can be extended to different coffee species/cultivars and to explore its possibilities in a given set of climate conditions.

The source code for PBDMs is Borland Pascal code that is embedded in a much larger code base including PBDMs for 40 different species of plants, herbivores, parasitoids, predators, and pathogens that were published as PBDM analyses implemented in a GIS context (1), and are simply a subset of all species modeled using PBDMs. Like the rest of the PBDM code base developed over the last three decades, the Pascal code for olive and coffee is currently not licensed nor it is deposited in a code repository, and is managed by the nonprofit scientific consortium CASAS Global (<http://www.casasglobal.org/>). The PBDM algorithms as well as key innovative code such as the Pascal subroutine for distributed maturation times with and without attrition, have been published in detail (2).

The code included in this repository has been used in a research context under the MED-GOLD (3) and TEBAKA (4) projects.

1. A. P. Gutierrez, L. Ponti, in Invasive Species and Global Climate Change, L. H. Ziska, J. S. Dukes, Eds. (CABI Publishing, Wallingford, UK, 2014), pp. 271–288.

2. A. P. Gutierrez, Applied population ecology: a supply-demand approach (John Wiley and Sons, New York, USA, 1996; <https://www.wiley.com/en-us/Applied+Population+Ecology%3A+A+Supply+Demand+Approach-p-9780471135869>).

3. Ponti, L., Gutierrez, A. P., Giannakopoulos, C., Varotsos, K. V., López Nevado, J., López Feria, S., Rivas González, F. W., Caboni, F., Stocchino, F., Rosati, A., Marchionni, D., Cure, J. R., Rodríguez, D., Terrado, M., De Felice, M., Dell’Aquila, A., Calmanti, S., Arjona, R., & Sanderson, M. (2024). Prospective regional analysis of olive and olive fly in Andalusia under climate change using physiologically based demographic modeling powered by cloud computing. Climate Services, 34, 100455. <https://doi.org/10.1016/j.cliser.2024.100455>


4. Ponti, L., Gutierrez, A. P., Metz, M., Haas, J., Panzenböck, E., Neteler, M., Baldacchino, F., Ambrico, A., Baviello, G., Calvitti, M., Dell’Aquila, A., Calmanti, S., Lampazzi, E., Miceli, V., Cuna, D., Stocchino, F., & Carroccio, D. (2024, May 29). Realistic daily dynamics of olive and olive fly at 250 m resolution using cloud-gap-filled canopy temperature data from MODIS LST calibrated with MODIS NDVI. Super-Resolution and Downscaling for EO and Earth Science (SUREDOS24), 29-31 May 2024, ESA-ESRIN, Frascati, Italy, <https://suredos24.esa.int/>, Frascati, Italy. <https://doi.org/10.5281/zenodo.11374208>

For further information, please contact Luigi Ponti (<luigi.ponti@enea.it>)


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
