# Backup GitHub repositories to AWS S3

## Goal
This script has been created to list all the repositories from a GitHub Organization and backup them in the AWS S3 bucket.

## Description
The script will ask the followings values:
- organization # name of the GitHub Organization
- parameter_github_token # the parameter name from AWS Parameter Store where the GitHub token is saved- region # AWS region
- bucket_name # AWS S3 bucket name
- path # path where the backup will be saved
Once the inputs have been ingressed, the script retrieves a GitHub token from an encrypted parameter (AWS SSM Parameter Store). Then list all the repositories, clone, and compress them in a tar file to be uploaded to an S3 Bucket in the desired path.

## Pre requisites
* Python 3.9.0 or grater
* Pip3
* AWS Credentials 

## Usage
The needed dependencies are in the requirements.txt file. It can be installed via pip3 and then run github_backup.py in the following way:

* pip3 install -r requirements.txt 
* python3 github_backup.py