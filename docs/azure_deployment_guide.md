# Azure Deployment Guide — SkyCheck 107

This guide deploys SkyCheck 107 publicly on Microsoft Azure using Azure Container Apps.

Azure Container Apps is recommended for this portfolio project because it runs Dockerized apps without managing a VM, provides a public HTTPS endpoint, and keeps the deployment focused on cloud/container skills.

## 0. Prerequisites

Install these on your local computer:

- Git
- Docker Desktop
- Azure CLI
- A Microsoft Azure account

Confirm tools:

```bash
git --version
docker --version
az version
```

## 1. Unzip and enter the project

```bash
unzip uav-mission-planner-azure-final.zip
cd uav-mission-planner
```

## 2. Run locally before deploying

```bash
docker compose up --build
```

Open:

```txt
http://localhost:8000
```

Health check:

```bash
curl http://localhost:8000/health
```

Expected:

```json
{"service":"uav-mission-planner","status":"ok"}
```

Stop the app:

```bash
CTRL+C
```

## 3. Push to GitHub

Create an empty GitHub repository named `uav-mission-planner`, then run:

```bash
git init
git add .
git commit -m "Initial SkyCheck 107 UAV mission planner"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/uav-mission-planner.git
git push -u origin main
```

## 4. Log in to Azure

```bash
az login
```

Set your subscription if you have more than one:

```bash
az account list --output table
az account set --subscription "YOUR_SUBSCRIPTION_NAME_OR_ID"
```

## 5. Install/update the Container Apps extension

```bash
az extension add --name containerapp --upgrade
az provider register --namespace Microsoft.App
az provider register --namespace Microsoft.OperationalInsights
```

## 6. Create Azure resources and deploy

Choose a globally reasonable region such as `eastus`.

```bash
az group create --name rg-skycheck107 --location eastus
```

Deploy from the local Dockerfile:

```bash
az containerapp up   --name skycheck107   --resource-group rg-skycheck107   --location eastus   --source .   --ingress external   --target-port 8000
```

Azure will build the container image, create supporting resources, deploy the container app, and expose it publicly.

## 7. Get the public URL

```bash
APP_URL=$(az containerapp show   --name skycheck107   --resource-group rg-skycheck107   --query properties.configuration.ingress.fqdn   -o tsv)

echo "https://$APP_URL"
```

Open the printed HTTPS URL in your browser.

## 8. Confirm the deployment



UI startup check:
- Open the homepage.
- Confirm mission fields are blank.
- Confirm the risk score displays `0`.
- Click **Evaluate Mission** without filling required fields; the browser should require input before the API is called.

Browser test:

```txt
https://YOUR_APP_FQDN
```

Health endpoint:

```bash
curl https://YOUR_APP_FQDN/health
```

Expected:

```json
{"service":"uav-mission-planner","status":"ok"}
```

API test with a safe mission:

```bash
curl -X POST https://YOUR_APP_FQDN/api/evaluate   -H "Content-Type: application/json"   -d '{
    "mission_name": "Safe daylight mapping",
    "pilot_name": "Portfolio Demo Pilot",
    "location": "Pittsburgh, PA",
    "latitude": 40.4406,
    "longitude": -79.9959,
    "near_airport_nm": 6,
    "altitude_agl_ft": 250,
    "visibility_sm": 8,
    "wind_speed_mph": 10,
    "cloud_clearance_horizontal_ft": 3000,
    "cloud_clearance_vertical_ft": 900,
    "airspace_class": "G",
    "laanc_authorization": false,
    "daylight_condition": "day",
    "anti_collision_lights": false,
    "visual_observer": false,
    "operations_over_people": false,
    "operations_over_moving_vehicles": false,
    "near_emergency": false,
    "remote_id_ready": true,
    "notes": "VLOS daylight mapping with clear launch area."
  }'
```

Expected decision:

```txt
GO
```

API test with a blocked mission:

```bash
curl -X POST https://YOUR_APP_FQDN/api/evaluate   -H "Content-Type: application/json"   -d '{
    "mission_name": "Blocked controlled airspace night op",
    "pilot_name": "Portfolio Demo Pilot",
    "location": "Pittsburgh, PA",
    "latitude": 40.4406,
    "longitude": -79.9959,
    "near_airport_nm": 2,
    "altitude_agl_ft": 450,
    "visibility_sm": 2.5,
    "wind_speed_mph": 18,
    "cloud_clearance_horizontal_ft": 1000,
    "cloud_clearance_vertical_ft": 300,
    "airspace_class": "D",
    "laanc_authorization": false,
    "daylight_condition": "night",
    "anti_collision_lights": false,
    "visual_observer": false,
    "operations_over_people": true,
    "operations_over_moving_vehicles": true,
    "near_emergency": true,
    "remote_id_ready": false,
    "notes": "Intentionally unsafe test case."
  }'
```

Expected decision:

```txt
NO-GO
```

## 9. View logs

```bash
az containerapp logs show   --name skycheck107   --resource-group rg-skycheck107   --follow
```

Submit a mission in the UI. You should see request activity in the logs.

## 10. Update the live app after code changes

```bash
git add .
git commit -m "Update SkyCheck 107"
git push
```

Then redeploy from your local project folder:

```bash
az containerapp up   --name skycheck107   --resource-group rg-skycheck107   --location eastus   --source .   --ingress external   --target-port 8000
```

## 11. Resume links

Use:

```txt
Live Demo: https://YOUR_APP_FQDN
GitHub: https://github.com/YOUR_USERNAME/uav-mission-planner
```

## 12. Optional cleanup

To stop charges and remove the app:

```bash
az group delete --name rg-skycheck107 --yes --no-wait
```
