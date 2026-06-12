// --------------------------------------------------------------------------
// Module: App Registration with Federated Identity Credential
// --------------------------------------------------------------------------

@description('Display name for the App Registration.')
param appDisplayName string

@description('GitHub organization.')
param githubOrg string

@description('GitHub repository name.')
param githubRepo string

@description('GitHub branch name.')
param githubBranch string

// ---------------------------------------------------------------------------
// App Registration
// ---------------------------------------------------------------------------
resource app 'Microsoft.Graph/applications@v1.0' = {
  displayName: appDisplayName
  uniqueName: appDisplayName
  signInAudience: 'AzureADMyOrg'

  // NOTE: The GUIDs below are well-known Microsoft public constants — NOT sensitive.
  requiredResourceAccess: [
    {
      // Microsoft Graph (well-known public resource app ID)
      resourceAppId: '00000003-0000-0000-c000-000000000000'
      resourceAccess: [
        {
          // Sites.ReadWrite.All (Application) — well-known permission GUID
          id: 'ef54d2bf-783f-4e0f-bca1-3210c0444d99'
          type: 'Role'
        }
      ]
    }
  ]
}

// ---------------------------------------------------------------------------
// Service Principal (Enterprise Application)
// ---------------------------------------------------------------------------
resource sp 'Microsoft.Graph/servicePrincipals@v1.0' = {
  appId: app.appId
}

// ---------------------------------------------------------------------------
// Federated Identity Credential — trusts GitHub OIDC from repo:branch
// ---------------------------------------------------------------------------
resource fedCred 'Microsoft.Graph/applications/${Microsoft.Graph/applications}/federatedIdentityCredentials@v1.0' = {
  name: '${app.uniqueName}/github-oidc-main'
  description: 'GitHub Actions OIDC for ${githubOrg}/${githubRepo}:${githubBranch}'
  audiences: [
    'api://AzureADTokenExchange'
  ]
  issuer: 'https://token.actions.githubusercontent.com'
  subject: 'repo:${githubOrg}/${githubRepo}:ref:refs/heads/${githubBranch}'
}

// ---------------------------------------------------------------------------
// Outputs
// SENSITIVE INFORMATION: clientId and objectId identify the App Registration.
// Treat these as confidential — store in GitHub Secrets, not in code.
// ---------------------------------------------------------------------------
output clientId string = app.appId
output objectId string = app.id
