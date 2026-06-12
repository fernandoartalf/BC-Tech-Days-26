# SharePoint Document Sync — Setup Guide

Step-by-step guide to configure the automatic synchronization of documents from this GitHub repository to a SharePoint Online document library.

---

## Prerequisites

Before starting, ensure you have:

- [ ] **Azure CLI** (`az`) installed and authenticated — [Install guide](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli)
- [ ] **Entra ID permissions** — Application Administrator role or higher in your Azure tenant
- [ ] **Microsoft 365 subscription** with SharePoint Online enabled
- [ ] **GitHub repository admin access** — to configure secrets and branch protection
- [ ] Your **Azure Tenant ID** (a GUID, found in Azure Portal → Entra ID → Overview)

---

## Step 1: Create the Azure AD App Registration

The App Registration acts as the identity GitHub Actions uses to authenticate with SharePoint via OIDC (no secrets needed).

### Option A: Run the provisioning script (recommended)

1. Open `infra/setup-azure.sh` and update the configuration section with your values:

   ```bash
   GITHUB_ORG="your-github-org"          # Your GitHub organization or username
   GITHUB_REPO="your-repo-name"          # Your repository name
   TENANT_ID="your-azure-tenant-id"      # Your Entra ID tenant GUID
   ```

   > **Warning:** These are sensitive values. Do not commit production values to public repositories.

2. Run the script:

   ```bash
   chmod +x infra/setup-azure.sh
   ./infra/setup-azure.sh
   ```

3. Note the output values:
   - **App (client) ID** — you will need this in Step 3
   - **Tenant ID** — you will need this in Step 3

### Option B: Manual setup via Azure Portal

1. Go to **Azure Portal** → **Entra ID** → **App registrations** → **New registration**
2. Name: `GitHub-SharePoint-Sync`
3. Supported account types: **Accounts in this organizational directory only**
4. Click **Register**
5. Note the **Application (client) ID** and **Directory (tenant) ID**

---

## Step 2: Configure Federated Identity Credential

This tells Azure to trust OIDC tokens from your specific GitHub repository and branch.

### If you used the script

The script already created the federated credential. Skip to Step 3.

### Manual setup

1. In your App Registration → **Certificates & secrets** → **Federated credentials** → **Add credential**
2. Select **GitHub Actions deploying Azure resources**
3. Fill in:
   - **Organization:** `your-github-org`
   - **Repository:** `your-repo-name`
   - **Entity type:** Branch
   - **Branch name:** `main`
   - **Name:** `github-oidc-main`
4. Click **Add**

The federated credential subject will be:
```
repo:your-github-org/your-repo-name:ref:refs/heads/main
```

---

## Step 3: Grant Microsoft Graph API Permissions

The App Registration needs permission to write files to SharePoint.

### Via Azure CLI

```bash
# Add Sites.ReadWrite.All (Application) permission
az ad app permission add \
  --id <YOUR_APP_CLIENT_ID> \
  --api 00000003-0000-0000-c000-000000000000 \
  --api-permissions 9492366f-7969-46a4-8d15-ed1a20078fff=Role

# Grant admin consent (requires Global Admin or Privileged Role Admin)
az ad app permission admin-consent \
  --id <YOUR_APP_CLIENT_ID>
```

### Via Azure Portal

1. App Registration → **API permissions** → **Add a permission**
2. Select **Microsoft Graph** → **Application permissions**
3. Search for `Sites.ReadWrite.All` → check it → **Add permissions**
4. Click **Grant admin consent for [your tenant]** (requires admin role)

> **Note:** If your organization requires stricter scoping, use `Sites.Selected` instead and grant per-site access via Graph API. See [Microsoft documentation](https://learn.microsoft.com/en-us/graph/api/site-get?view=graph-rest-1.0).

---

## Step 4: Add GitHub Repository Secrets

Store the App Registration identifiers as encrypted secrets so the workflow can authenticate.

1. Go to your GitHub repository → **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret** and add:

   | Secret Name | Value | Description |
   |---|---|---|
   | `AZURE_CLIENT_ID` | `<App (client) ID from Step 1>` | Identifies the App Registration |
   | `AZURE_TENANT_ID` | `<Directory (tenant) ID>` | Identifies your Azure AD tenant |

> **Tip:** For multi-repo setups, use **Organization secrets** instead to avoid repeating this per repo.

---

## Step 5: Configure the Sync Settings

Edit `.github/sharepoint-sync.yml` in your repository with your target SharePoint site and folder.

```yaml
# Folder in the repository to sync
source_folder: "docs"

# SharePoint Online site (hostname:/sites/SiteName format)
sharepoint_site: "yourtenant.sharepoint.com:/sites/YourSite"

# Target folder inside the Documents library (drive root).
# Do NOT include "Shared Documents" — the default drive already
# points to that library.
sharepoint_folder: "/YourProject"

# Deletion policy: false = never delete from SharePoint (additive only)
delete_orphaned: false

# Delta detection: "auto" | "git-diff" | "full"
sync_mode: "auto"

# Optional: only sync files matching these patterns
# file_patterns:
#   - "**/*.md"
#   - "**/*.pdf"
#   - "**/*.docx"
```

### Configuration reference

| Key | Required | Default | Description |
|---|---|---|---|
| `source_folder` | Yes | — | Relative path to the repo folder to sync |
| `sharepoint_site` | Yes | — | SharePoint site in `hostname:/sites/Name` format |
| `sharepoint_folder` | Yes | — | Target path relative to the drive root (do NOT include "Shared Documents") |
| `delete_orphaned` | No | `false` | Delete SP files not in source (currently always `false`) |
| `sync_mode` | No | `auto` | `auto` = git-diff if SHAs available, else full scan |
| `file_patterns` | No | all files | Glob patterns to filter which files to sync |

---

## Step 6: Configure Branch Protection (recommended)

Protect the workflow and config files from unauthorized changes.

1. Go to **Settings** → **Branches** → **Add branch protection rule**
2. Branch name pattern: `main`
3. Enable:
   - [x] Require a pull request before merging
   - [x] Require approvals (at least 1)
   - [x] Require status checks to pass
4. Create a `CODEOWNERS` file to require approval for workflow changes:

   ```
   # .github/CODEOWNERS
   .github/workflows/   @your-org/platform-team
   .github/sharepoint-sync.yml  @your-org/platform-team
   ```

---

## Step 7: Verify the Setup

1. **Create a test file** in your `source_folder` (e.g., `docs/test-sync.txt`)
2. **Open a Pull Request** to `main` with the test file
3. **Merge the PR**
4. **Check GitHub Actions** — go to the **Actions** tab and verify the "SharePoint Document Sync" workflow ran successfully
5. **Check SharePoint** — navigate to your target folder and confirm the file appeared

### Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| Workflow does not trigger | PR was closed without merging, or workflow file not on `main` | Ensure the PR is merged (not just closed) |
| `AADSTS700016` error | Wrong `AZURE_CLIENT_ID` | Verify the secret matches the App Registration's Application (client) ID |
| `AADSTS70021` error | Federated credential mismatch | Verify the subject claim matches `repo:<org>/<repo>:ref:refs/heads/main` exactly |
| `403 Forbidden` from Graph API | Missing admin consent or insufficient permissions | Run `az ad app permission admin-consent --id <CLIENT_ID>` |
| `404 Not Found` for SharePoint site | Wrong `sharepoint_site` format | Must be `hostname:/sites/SiteName` (no `https://`, no trailing `/`) |
| No files uploaded | `source_folder` does not exist or `file_patterns` exclude everything | Check the folder path and patterns in `sharepoint-sync.yml` |

---

## Architecture Overview

```
PR merged to main
       │
       ▼
┌─────────────────────┐
│  GitHub Actions      │
│  Workflow triggers   │
│                      │
│  1. Checkout repo    │
│  2. Compute delta    │
│  3. OIDC login       │───── token exchange ────▶ Azure Entra ID
│  4. Run sync action  │◀──── access token ──────┘
│  5. Upload via Graph │
└──────────┬──────────┘
           │
     Microsoft Graph API
           │
           ▼
┌─────────────────────┐
│  SharePoint Online   │
│  Document Library    │
└─────────────────────┘
```

---

## Adding More Repositories

To onboard a new repository to the same App Registration:

1. Add a new **Federated Identity Credential** for the repo:

   ```bash
   az ad app federated-credential create \
     --id <APP_CLIENT_ID> \
     --parameters '{
       "name": "github-oidc-new-repo",
       "issuer": "https://token.actions.githubusercontent.com",
       "subject": "repo:<org>/<new-repo>:ref:refs/heads/main",
       "audiences": ["api://AzureADTokenExchange"]
     }'
   ```

2. Add `AZURE_CLIENT_ID` and `AZURE_TENANT_ID` secrets to the new repository

3. Copy `.github/sharepoint-sync.yml` and `.github/workflows/sharepoint-sync.yml` to the new repository, updating the `sharepoint_site` and `sharepoint_folder` values

---

## Security Checklist

- [ ] No passwords, client secrets, or certificates are stored anywhere in the repository
- [ ] `AZURE_CLIENT_ID` and `AZURE_TENANT_ID` are stored as GitHub Encrypted Secrets
- [ ] Federated credential is scoped to the specific repo + `main` branch only
- [ ] Microsoft Graph permissions have admin consent
- [ ] Branch protection is enabled on `main`
- [ ] `CODEOWNERS` protects workflow and config files
- [ ] `sharepoint-sync.yml` does not contain production URLs in public repositories
