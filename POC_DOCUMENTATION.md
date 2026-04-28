# Clinical Supply Chain Intelligence Agent (POC)

## Overview
This repository contains the code and documentation for a Proof of Concept (POC) demonstrating an Agentic AI architecture on Google Cloud Platform (GCP). It was specifically designed for an AI Engineer role interview.

The core objective is to build a **McKesson-style conversational agent** that assists hospital supply chain managers by:
1. Checking if a specific medication is in stock.
2. Confirming that it complies with current shipping and storage regulations.

## Architecture & Technology Stack
- **The Data Layer (RAG)**: Google Cloud Storage for raw PDF manuals -> Vertex AI Agent Builder Data Store (automates embedding and vector search without requiring a manual Cloud Function).
- **The Logic Layer (Tools)**: An "Inventory Database" simulated via a containerized **FastAPI** application hosted on **Google Cloud Run**.
- **The Brain**: **Gemini 1.5 Pro** accessed via **Vertex AI Agent Builder**, equipped with an OpenAPI Tool (for inventory checking) and a Data Store Search Tool (for regulation queries).

---

## 🟢 What Has Been Completed 

### Phase 0: Local Environment Setup
-  Cloned and initialized the repository inside the `mxasalam/ClinicalChain` directory.
-  Generated a suite of mock PDF shipping manuals (for Insulin, Amoxicillin, and mRNA vaccines).
-  Successfully installed and authenticated the `gcloud` CLI (using `gcloud init` and pulling Application-Default Credentials).

### Phase 1: Logic Layer (Inventory API)
-  Written a fast and responsive `FastAPI` application mimicking the inventory DB (`inventory-api/main.py`).
-  Written a `Dockerfile` for containerization.
-  Enabled the required GCP APIs for deployment (Cloud Run, Cloud Build, Artifact Registry, Discovery Engine).
-  **Deployed the container seamlessly to Google Cloud Run**.
-  Generated and modified the `openapi.json` file to point specifically to the live Cloud Run endpoint, preparing it for Agent Builder ingestion.

### Phase 2: Data Storage Implementation
-  Provisioned a Google Cloud Storage bucket (`gs://clinicalchain-manuals-mxasalam`) residing in `us-central1`.
-  Successfully uploaded all mock PDF storage regulations directly to the GCS bucket.

All initial code and assets have been committed and safely pushed to the `main` branch of this GitHub repository.

---

## 🟡 What Is Left To Do (Phase 3: The UI Configuration)

The foundational backend infrastructure is complete. The remaining steps need to be interactively completed by the user directly within the **Google Cloud Console**, as this allows you to best familiarize yourself with the platform for your interview.

### Step 1: Create the Data Store (RAG Pipeline)
1. Go to **Vertex AI Agent Builder** in the GCP Console.
2. Navigate to **Data Stores** -> **Create Data Store**.
3. Choose **Cloud Storage** as the source, locate your `clinicalchain-manuals-mxasalam` bucket, choose **Unstructured documents**, and click Continue.
4. Name it `"Shipping Regulations"` and hit Create. GCP handles all the PDF text-extraction and vector embedding automatically behind the scenes.

### Step 2: Create the Agent Frame
1. Still in Agent Builder's left menu, go to **Apps** -> **Create App**.
2. Select **Agent** (ensure it uses Gemini 1.5 Pro).
3. Title it `"McKesson Logistics Assistant"`.
4. In the Agent's details, set the **Instructions (System Prompt)** to:
   > *"You are a McKesson Logistics Assistant. You help hospital supply chain managers check if inventory is available and if they comply with shipping regulations. Always check the Search Tool for shipping rules, and the Inventory API Tool for stock."*

### Step 3: Wire the Agent's Tools
1. **The Search Tool**: Navigate to your Agent's **Tools** menu. Create a new tool, select **Data Store**, connect it to your `"Shipping Regulations"` data store, and name it `search_regulations`.
2. **The API Tool**: Add another tool, but choose **OpenAPI** (or "API"). Upload the `openapi.json` file located natively on your machine at `/Users/mxasalam/ClinicalChain/inventory-api/openapi.json`. Name this tool `check_inventory`.

### Step 4: Verification and Testing
Utilize the testing pane on the right side of the Agent Builder UI. Enter the following compound query:
> *"What are the rules for shipping insulin? Also, do we have any in the Richmond warehouse?"*

The agent should flawlessly utilize the Vector Search RAG pipeline to report back real shipping rules, and execute the OpenAPI tool directly against the live Cloud Run endpoint to check Richmond's inventory!
