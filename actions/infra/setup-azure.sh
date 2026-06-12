#!/usr/bin/env bash
# --------------------------------------------------------------------------
# Provision Azure AD App Registration + Federated Identity Credential
# for GitHub Actions OIDC → SharePoint Document Sync
#
# Prerequisites:
#   - Azure CLI (az) installed and logged in
#   - Sufficient Entra ID permissions (Application Administrator or higher)
#
# Usage:
#   chmod +x infra/setup-azure.sh
#   ./infra/setup-azure.sh
# --------------------------------------------------------------------------

set -euo pipefail

# ---- Configuration -------------------------------------------------------
# SENSITIVE INFORMATION: Replace these values with your own before running.
# Do NOT commit real tenant IDs or org-specific values to public repositories.
GITHUB_ORG="AL-Copilot-Skills-Collection"       # SENSITIVE INFORMATION: GitHub organization name — environment-specific
GITHUB_REPO="BC-Tech-Days-26"                    # SENSITIVE INFORMATION: GitHub repository name — environment-specific
GITHUB_BRANCH="main"
APP_NAME="GitHub-SharePoint-Sync"
TENANT_ID="79f81379-3474-4428-951b-4fd994ced6a8" # SENSITIVE INFORMATION: Azure Entra ID Tenant ID — must be kept private

# Microsoft Graph API IDs (these are well-known public Microsoft constants — NOT sensitive)
GRAPH_API_ID="00000003-0000-0000-c000-000000000000"
# Sites.ReadWrite.All (Application permission) — well-known public permission GUID
SITES_READWRITE_ALL="ef54d2bf-783f-4e0f-bca1-3210c0444d99"

echo "=== SharePoint Sync — Azure AD Setup ==="
echo ""

# ---- Step 1: Create App Registration -------------------------------------
echo "[1/5] Creating App Registration: ${APP_NAME}..."
APP_ID=$(az ad app create \
  --display-name "${APP_NAME}" \
  --sign-in-audience "AzureADMyOrg" \
  --query appId \
  --output tsv)

echo "       App (client) ID: ${APP_ID}"

# ---- Step 2: Create Service Principal ------------------------------------
echo "[2/5] Creating Service Principal..."
az ad sp create --id "${APP_ID}" --output none 2>/dev/null || true
echo "       Service Principal created."

# ---- Step 3: Add Microsoft Graph permission -------------------------------
echo "[3/5] Adding Sites.ReadWrite.All permission..."
az ad app permission add \
  --id "${APP_ID}" \
  --api "${GRAPH_API_ID}" \
  --api-permissions "${SITES_READWRITE_ALL}=Role" \
  --output none

echo "       Permission added. Admin consent required (see step below)."

# ---- Step 4: Add Federated Identity Credential ---------------------------
echo "[4/5] Adding Federated Identity Credential for GitHub OIDC..."
az ad app federated-credential create \
  --id "${APP_ID}" \
  --parameters "{
    \"name\": \"github-oidc-${GITHUB_BRANCH}\",
    \"issuer\": \"https://token.actions.githubusercontent.com\",
    \"subject\": \"repo:${GITHUB_ORG}/${GITHUB_REPO}:ref:refs/heads/${GITHUB_BRANCH}\",
    \"audiences\": [\"api://AzureADTokenExchange\"],
    \"description\": \"GitHub Actions OIDC for ${GITHUB_ORG}/${GITHUB_REPO}:${GITHUB_BRANCH}\"
  }" \
  --output none

echo "       Federated credential created."

# ---- Step 5: Summary -----------------------------------------------------
echo ""
echo "[5/5] === Setup Complete ==="
echo ""
echo "  App (client) ID : ${APP_ID}"
echo "  Tenant ID       : ${TENANT_ID}"
echo ""
echo "  NEXT STEPS:"
echo "  1. Grant admin consent (requires Global Admin or Privileged Role Admin):"
echo "     az ad app permission admin-consent --id ${APP_ID}"
echo ""
echo "  2. Add these as GitHub repository secrets:"
echo "     AZURE_CLIENT_ID  = ${APP_ID}"
echo "     AZURE_TENANT_ID  = ${TENANT_ID}"
echo ""
echo "  3. Create .github/sharepoint-sync.yml in your repository."
echo ""
echo "  Done!"
