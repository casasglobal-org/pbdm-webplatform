# mgd-ict-platform-pbdm-wf

## Table of contents

| Path | Description |
| ------------- | ------------- |
| ./resources/worker-container  | Files needed to build the Worker image that run in AWS::ECS |
| ./resources/worker-container/Dockerfile | Dockerfile used to build the Worker image |
| ./resources/worker-container/winetricks  | Bash script to optimize Wine software to execute .exe files in Worker image |
| ./resources/worker-container/run.sh  | Bash script used by Worker container as first command |
| ./resources/worker-container/build.sh  | Bash script to build and push the Worker image into AWS ECR |
| ./resource/iam-role.yml  | iam role creation yaml file |
| ./resource/stepFunctions.yml  | AWS Step function yaml file |
| ./resource/ecs.yml  | Cluster, Task Definition and ECR creation yaml file |
| ./resource/vpc.yml  | VPC creation yaml file needed by ECS Cluster(Fargate) |
| ./serverless.yml  | main yaml file |



## AWS Resources

| Name | Type | Description | File |
| ------------- | ------------- | ------------- | ------------- |
| mgd-pbdm-workflow-StepFunctionRole | AWS::IAM::Role | role for granting ecs:RunTask access to state machine | iam-role.yml |
| mgd-pbdm-workflow-ecsTaskExecutionRole | AWS::IAM::Role | role for granting ECS Cluster access to S3 | iam-role.yml |
| mgd-pbdm-workflow-cluster| AWS::ECS::Cluster | main cluster | ecs.yml |
| mgd-pbdm-workflow-task-definition | AWS::ECS::TaskDefinition | task definition for Fargate Worker container | ecs.yml |
| mgd-pbdm-workflow-worker-image | AWS::ECR::Repository | container repository for Worker image | ecs.yml |
| mgd-pbdm-workflow-vpc | AWS::EC2::VPC | vpc used by subnet and security group | vpc.yml |
| mgd-pbdm-workflow-subnet | AWS::EC2::Subnet | subnet for Fargate Worker container | vpc.yml |
| mgd-pbdm-workflow-rt | AWS::EC2::RouteTable | route applied to vpc | vpc.yml |
| mgd-pbdm-workflow-sg | AWS::EC2::SecurityGroup | security group for Fargate Worker container | vpc.yml |
| mgd-pbdm-workflow-StepFunction | AWS Step Function | step function definition | stepFunctions.yml |

# Requirements
## Install node.js, npm and serverless
```
brew install node
```
`serverless` framework
```
npm install -g serverless
```

## Install plugins
```
npm install serverless-pseudo-parameters && \
npm install serverless-python-requirements && \
sls plugin install --name serverless-step-functions

```


# Deploy
```
sls deploy
```

## Build Docker file
```
cd ./resources/worker-container
sh build.sh
```