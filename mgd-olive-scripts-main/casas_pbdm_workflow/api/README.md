# mgd-ict-platform-pbdm-api

## Table of contents

| Path | Description |
| ------------- | ------------- |
| ./functions/request-api.py  | python scripts of request api |
| ./functions/api.py  | python scripts of pbdm-workflow api  |
| ./resources/iam-role.yml  | iam role creation yaml file |
| ./resources/functions.yml  | AWS::Lambda::Function creation yaml file |
| ./serverless.yml  | main yaml file |

## AWS Resources

| Name | Type | Description | File |
| ------------- | ------------- | ------------- | ------------- |
| mgd-pbdm-api-lambda-role | AWS::IAM::Role | role for granting s3, state machine and cognito access | iam-role.yml |
| mgd-pbdm-state-role | AWS::IAM::Role | role for granting s3 (only read), state machine and cognito access | iam-role.yml |
| mgd-pbdm-api-API | AWS::Lambda::Function - AWS API Gateway | /dataset/pbdm/workflow/pbdm endpoint | functions.yml |
| mgd-pbdm-state-request | AWS::Lambda::Function - AWS API Gateway | /pbdm/request endpoint | functions.yml |

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
npm install serverless-pseudo-parameters
```

# Deploy
```
sls deploy
```