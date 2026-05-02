#!/bin/bash
set -e
PROJECT_ID="clinicalchain"
REPO="mxasalam/ClinicalChain"
SA_NAME="github-actions-sa"

echo "Enabling IAM Credentials API..."
gcloud services enable iamcredentials.googleapis.com

echo "Creating Service Account ($SA_NAME)..."
gcloud iam service-accounts create $SA_NAME --display-name="GitHub Actions Service Account" || true

echo "Granting IAM Roles..."
for ROLE in roles/cloudbuild.builds.editor roles/artifactregistry.writer roles/run.admin roles/iam.serviceAccountUser; do
  gcloud projects add-iam-policy-binding $PROJECT_ID \
      --member="serviceAccount:$SA_NAME@$PROJECT_ID.iam.gserviceaccount.com" \
      --role="$ROLE" > /dev/null
done

echo "Creating Workload Identity Pool..."
gcloud iam workload-identity-pools create "github-actions-pool" \
    --project="${PROJECT_ID}" \
    --location="global" \
    --display-name="GitHub Actions Pool" || true

echo "Creating Workload Identity Provider..."
gcloud iam workload-identity-pools providers create-oidc "github-actions-provider" \
    --project="${PROJECT_ID}" \
    --location="global" \
    --workload-identity-pool="github-actions-pool" \
    --display-name="GitHub Actions Provider" \
    --attribute-mapping="google.subject=assertion.sub,attribute.actor=assertion.actor,attribute.repository=assertion.repository" \
    --issuer-uri="https://token.actions.githubusercontent.com" || true

PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")

echo "Binding GitHub repo to Service Account..."
gcloud iam service-accounts add-iam-policy-binding "${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com" \
    --project="${PROJECT_ID}" \
    --role="roles/iam.workloadIdentityUser" \
    --member="principalSet://iam.googleapis.com/projects/${PROJECT_NUMBER}/locations/global/workloadIdentityPools/github-actions-pool/attribute.repository/${REPO}" > /dev/null

echo "PROJECT_NUMBER=$PROJECT_NUMBER"
