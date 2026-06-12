// --------------------------------------------------------------------------
// Bicep template: Azure AD App Registration + Federated Identity Credential
// for GitHub Actions OIDC → SharePoint Document Sync
//
// Usage:
//   az deployment group create \
//     --resource-group <rg> \
//     --template-file infra/main.bicep \
//     --parameters githubOrg='<YOUR_ORG>' \
//                  githubRepo='<YOUR_REPO>'
//
// SENSITIVE INFORMATION: The githubOrg and githubRepo parameter values below
// are environment-specific. Pass them at deployment time; do NOT hardcode
// production values in the template.
// --------------------------------------------------------------------------

targetScope = 'subscription'

@description('GitHub organization or user that owns the repository.')
param githubOrg string

@description('GitHub repository name.')
param githubRepo string

@description('Branch allowed to request tokens (default: main).')
param githubBranch string = 'main'

@description('Display name for the App Registration.')
param appDisplayName string = 'GitHub-SharePoint-Sync'

@description('Resource group for the deployment metadata (not billed).')
param resourceGroupName string = 'rg-github-sharepoint-sync'

@description('Location for the resource group.')
param location string = 'westeurope'

// ---------------------------------------------------------------------------
// Resource Group
// ---------------------------------------------------------------------------
resource rg 'Microsoft.Resources/resourceGroups@2023-07-01' = {
  name: resourceGroupName
  location: location
}

// ---------------------------------------------------------------------------
// Module: App Registration + Federated Credential
// ---------------------------------------------------------------------------
module appRegistration 'modules/app-registration.bicep' = {
  scope: rg
  name: 'appRegistration'
  params: {
    appDisplayName: appDisplayName
    githubOrg: githubOrg
    githubRepo: githubRepo
    githubBranch: githubBranch
  }
}

// ---------------------------------------------------------------------------
// Outputs
// ---------------------------------------------------------------------------
// SENSITIVE INFORMATION: These outputs expose the App Client ID, Object ID, and Tenant ID.
// They will be visible in deployment logs. Treat deployment output as confidential.
output appClientId string = appRegistration.outputs.clientId
output appObjectId string = appRegistration.outputs.objectId
output tenantId string = tenant().tenantId
output instructions string = '''
Next steps:
1. Store these as GitHub repository secrets:
   - AZURE_CLIENT_ID  = ${appRegistration.outputs.clientId}
   - AZURE_TENANT_ID  = ${tenant().tenantId}

2. Grant Microsoft Graph API permission (requires Global/Application Admin):
   az ad app permission add \
     --id ${appRegistration.outputs.clientId} \
     --api 00000003-0000-0000-c000-000000000000 \
     --api-permissions ef54d2bf-783f-4e0f-bca1-3210c0444d99=Role

   az ad app permission admin-consent \
     --id ${appRegistration.outputs.clientId}

3. The App Registration is ready. The workflow will use OIDC — no secrets needed.
'''
