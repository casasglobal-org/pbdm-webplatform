# pbdm-workflow

Workflow to run PBDM executables compiled from Pascal source code.

## Trello board

Here we keep track of things:

[PBDM-Workflow Trello board](https://trello.com/b/449PzQuo/pbdm-workflow)

## How to run serverless project

```
sls deploy 
```

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

## Content Description