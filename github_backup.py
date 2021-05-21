import boto3, base64, tarfile, shutil, os, json
from github3 import login
from datetime import datetime
from git import Repo
import time
from threading import Thread

# Github Details
organisation = input("Ingress GitHub Org name \n")

# This is, a github access token with appropriatly minimal permissions, that has been encrypted against our specific AWS KMS ARN.  It's therefore safe to make public
parameter_github_token = input("Ingress the parameter name from AWS Parameter Store where the GitHub token is saved \n")

# AWS Details
region = input("Ingress AWS region \n")
bucket_name = input("Ingress AWS S3 bucket name \n")
path = input("Ingress the path where the backup will be stored \n")

# Trivia
timestring = datetime.now().strftime('%Y%m%d')

# Get the token from SSM Parameter Store
def get_secret_token(parameter_github_token):
    client = boto3.client('ssm')
    get_secret_value_response = client.get_parameter(Name= parameter_github_token, WithDecryption=True)
    return get_secret_value_response['Parameter']['Value']


def get_github3_client(token):
    gh = login(token=token)
    return gh


def clone_compress_upload_repo(repo, github_token, bucket_name):
    r = str(repo)
    directory = path + r + "/"
    print ("Archiving: " + r)

    ## Clone Repository
    from_url = "https://" + github_token + ":x-oauth-basic@github.com/" + r + ".git"
    dst_path = r + "-" + timestring + ".git"
    current_repo = Repo.clone_from(from_url, dst_path, mirror=True)
         
    ## Archive to file
    tar_filename = os.path.basename(r) + "-" + timestring + ".tar.gz"
    tar = tarfile.open(tar_filename, "w:gz")
    tar.add(dst_path)
    tar.close()

    # ## Stream to a file in an S3 bucket
    # s3 = boto3.resource('s3')
    # data = open(tar_filename, 'rb')
    # object_name = directory + tar_filename
    # s3.Bucket(bucket_name).put_object(Key=object_name, Body=data)

    ## Cleanup
    shutil.rmtree(dst_path, ignore_errors=True)
    os.remove(tar_filename)



def backup_github(gh,github_token):
    org = gh.organization(organisation)
    repos = list(org.iter_repos(type="private"))  # Or type="all"

    threads = list()

    for repo in repos:
        thread = Thread(target=clone_compress_upload_repo, args=(repo, github_token, bucket_name))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

def handler(event, context):
    github_token = get_secret_token(parameter_github_token)
    gh = get_github3_client(github_token)
    backup_github(gh)


def main():
    boto3.setup_default_session(region_name=region)
    github_token = get_secret_token(parameter_github_token)
    gh = get_github3_client(github_token)
    backup_github(gh,github_token)

if __name__ == "__main__":
    main()