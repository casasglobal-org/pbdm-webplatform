# Climate Data Integration and Processing System

## Overview

This project automates the integration and processing of climate data from Copernicus Data Store ( CDS ), utilizing AWS services for efficient and scalable operations. The system is divided into two main components: a set of AWS Lambda functions for data retrieval and initial processing, and an AWS Fargate application for more intensive yearly data merging tasks. AWS Step Functions orchestrate the Lambda functions on a monthly schedule, while an AWS Fargate task is scheduled to run annually, leveraging AWS ECS's capabilities for container management.

## Project Structure

```plaintext
.
├── ECS-Yearly-Merge          # Container application for yearly data processing
│   ├── Dockerfile            # Dockerfile for building the Fargate application image
│   ├── README.md             # Documentation specific to the Fargate application
│   ├── env.list              # Environment variables for the Fargate application
│   ├── requirements.txt      # Python dependencies for the Fargate application
│   └── src
│       └── merge.py          # Main script for the Fargate application
├── README.md                 # This file
├── buildspec.yml             # Build specifications for AWS CodeBuild
├── container.yaml            # AWS CloudFormation template for container resources
├── events
│   └── event.json            # Sample event for local Lambda testing
├── lambdas.yaml              # CloudFormation template for Lambda functions
├── samconfig.toml            # SAM configuration file
├── src                       # Source code for Lambda functions
│   ├── 10m_wind_speed.py     # Lambda function for wind speed data processing
│   ├── 2m_temperature.py     # Lambda function for temperature data processing
│   ├── download_old.py       # Lambda function for historical data retrieval - `unused`
│   ├── precipitation_flux.py # Lambda function for precipitation data processing
│   ├── relative_humidity.py  # Lambda function for humidity data processing
│   ├── requirements.txt      # Python dependencies for Lambda functions
│   └── solar_radiation_flux.py # Lambda function for solar radiation data processing
└── template.yaml             # Master CloudFormation template linking all resources
```

## Prerequisites

- AWS CLI configured with Administrator permission
- Docker installed for building and running the Fargate application locally
- Python 3.x and pip for managing Lambda function dependencies
- SAM CLI for building, testing, and deploying the AWS resources

## Deployment

### AWS Lambda Functions and Step Functions

Deploy the Lambda functions and orchestrate them with AWS Step Functions for monthly execution using the SAM CLI:

1. Navigate to the `src` directory to install Python dependencies:
   ```bash
   cd src
   pip install -r requirements.txt
   ```
2. Use the SAM CLI to build and deploy the resources:
   ```bash
   sam build
   sam deploy --guided
   ```

### AWS Fargate Application

For deploying the Fargate application which is scheduled annually:

- Build the Docker image and push it to Amazon ECR as detailed in the `ECS-Yearly-Merge/README.md`.
- Schedule the Fargate task on ECS to run annually, using AWS CLI or the AWS Management Console.

## Usage

The Lambda functions, orchestrated by AWS Step Functions, automatically run on a monthly schedule. They process and prepare data for the annual merging task, executed by the AWS Fargate application.

## Contributing

Contributions are welcome. To contribute:

- Fork the repository.
- Create a new branch for your feature or fix.
- Commit changes and push to your fork.
- Submit a pull request against the main branch.

Please ensure your code adheres to the project's standards and has passed all tests.

## Additional Notes

- For local testing and development, refer to each component's specific README within this repository.
- Ensure all AWS services are correctly configured and have the necessary permissions.



## Resources

See the [AWS SAM developer guide](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/what-is-sam.html) for an introduction to SAM specification, the SAM CLI, and serverless application concepts.

Next, you can use AWS Serverless Application Repository to deploy ready to use Apps that go beyond hello world samples and learn how authors developed their applications: [AWS Serverless Application Repository main page](https://aws.amazon.com/serverless/serverlessrepo/)


## How To 
### open .nc files

Install nrtcdf-bin (for ubuntu)
```bash
sudo apt-get install netcdf-bin
```
Open file.nc
```bash
ncdump -h Precipitation-Flux_C3S-glob-agric_AgERA5_20231201_final-v1.1.nc
```
```
sam deploy --stack-name nome-stack --capabilities CAPABILITY_IAM \
--parameter-overrides CDSAPIKEY='tua_chiave_api'
```