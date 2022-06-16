---
type: docs
title: "Setting up Vertex"
description: "How to set up Vertex for SAME."
---

To begin with Vertex, first, you need to set up the environment. The script below will walk through the steps:

```bash

# Set a series of enviornment variables
export PROJECT_ID="xxx"
export SERVICE_ACCOUNT_ID="xxx"
export USER_EMAIL="xxx"
export BUCKET_NAME="xxx"
export FILE_NAME="xxx"
export GOOGLE_APPLICATION_CREDENTIALS="xxx"
```


```bash
gcloud iam service-accounts create $SERVICE_ACCOUNT_ID \
--description="Service principal for running vertex and creating pipelines/metadata" \
--display-name="$SERVICE_ACCOUNT_ID" \
--project ${PROJECT_ID}

gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member="serviceAccount:$SERVICE_ACCOUNT_ID@$PROJECT_ID.iam.gserviceaccount.com" \
    --role=roles/storage.objectAdmin

gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member="serviceAccount:$SERVICE_ACCOUNT_ID@$PROJECT_ID.iam.gserviceaccount.com" \
    --role=roles/aiplatform.user

gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member="serviceAccount:$SERVICE_ACCOUNT_ID@$PROJECT_ID.iam.gserviceaccount.com" \
    --role=roles/ml.admin

gcloud projects get-iam-policy $PROJECT_ID \
    --flatten="bindings[].members" \
    --format='table(bindings.role)' \
    --filter="bindings.members:serviceAccount:$SERVICE_ACCOUNT_ID@$PROJECT_ID.iam.gserviceaccount.com"

gcloud iam service-accounts add-iam-policy-binding \
    $SERVICE_ACCOUNT_ID@$PROJECT_ID.iam.gserviceaccount.com \
    --member="user:$USER_EMAIL" \
    --role="roles/iam.serviceAccountUser"
    --project ${PROJECT_ID}

gsutil mb -p $PROJECT_ID gs://$BUCKET_NAME

gsutil iam ch \
    serviceAccount:$SERVICE_ACCOUNT_ID@$PROJECT_ID.iam.gserviceaccount.com:roles/storage.objectCreator,objectViewer \
    gs://$BUCKET_NAME

gcloud iam service-accounts keys create $FILE_NAME.json --iam-account=$SERVICE_ACCOUNT_ID@$PROJECT_ID.iam.gserviceaccount.com 
```

From this point, the SAME project should be ready to go!