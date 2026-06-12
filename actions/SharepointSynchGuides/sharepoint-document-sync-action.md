# Technical Specification: SharePoint Document Sync GitHub Action

## 1. Overview

This specification defines a GitHub Action workflow that automatically synchronizes documents from a designated folder in a GitHub repository to a Microsoft SharePoint Online site when a pull request is merged into the `main` branch.

The solution is designed to be:

- **Secure** — No secrets stored in code; leverages Azure Managed Identity and OpenID Connect (OIDC) federated credentials.
- **Scalable** — Each repository independently configures its target SharePoint site and folder via repository-level configuration.
- **Auditable** — All sync operations are logged in GitHub Actions run history.

---

## 2. Functional Requirements

| ID | Requirement |
|----|-------------|
| FR-01 | The workflow triggers only when a PR is merged into `main`. |
| FR-02 | The workflow syncs files from a configurable source folder in the repository to a configurable SharePoint document library/folder. |
| FR-03 | The sync operation uploads new/modified files and optionally deletes files removed from the source folder. |
| FR-04 | The workflow supports different SharePoint target folders per repository without code changes. |
| FR-05 | The workflow reports success/failure status as a GitHub Actions check. |

---

## 3. Non-Functional Requirements

| ID | Requirement |
|----|-------------|
| NFR-01 | No passwords, client secrets, or tokens stored in repository code or environment variables visible in logs. |
| NFR-02 | Authentication uses Azure AD Workload Identity Federation (OIDC) — no long-lived secrets. |
| NFR-03 | Secrets (if any fallback is needed) are stored exclusively in GitHub Encrypted Secrets or Azure Key Vault. |
| NFR-04 | The solution must handle repositories with up to 10,000 files in the sync folder. |
| NFR-05 | Sync operations must complete within the GitHub Actions job timeout (6 hours max, target < 15 min for typical loads). |

---

## 4. Architecture

### 4.1 High-Level Flow

```
┌──────────────┐       ┌─────────────────┐       ┌──────────────────┐
│  GitHub Repo │──PR──▶│  GitHub Actions  │──API─▶│  SharePoint      │
│  (main)      │merged │  Workflow        │       │  Online Site     │
└──────────────┘       └────────┬────────┘       └──────────────────┘
                                │
                        OIDC Token Exchange
                                │
                       ┌────────▼────────┐
                       │  Azure AD /     │
                       │  Entra ID       │
                       └─────────────────┘
```

### 4.2 Authentication Flow (OIDC — No Secrets)

1. GitHub Actions requests an OIDC token from GitHub's token endpoint.
2. The OIDC token is presented to Azure AD via a Federated Identity Credential.
3. Azure AD validates the token (issuer, subject, audience) and issues an access token.
4. The access token is used to call Microsoft Graph API to upload files to SharePoint.

**No client secret or certificate is stored in the repository.**

### 4.3 Per-Repository Configuration

Each repository defines its sync settings in a configuration file at the repository root:

```yaml
# .github/sharepoint-sync.yml
source_folder: "docs/publish"        # Folder in repo to sync
sharepoint_site: "contoso.sharepoint.com:/sites/ProjectDocs"
sharepoint_folder: "/Shared Documents/AutoSync/ProjectAlpha"
delete_orphaned: true                 # Remove SP files not in source
file_patterns:                        # Optional glob filters
  - "**/*.md"
  - "**/*.pdf"
  - "**/*.docx"
```

This enables each repository to target a different SharePoint site/folder without modifying the workflow code.

---

## 5. Azure Resources Required

| Resource | Purpose | SKU/Tier |
|----------|---------|----------|
| **Azure AD App Registration** (Entra ID) | Represents the GitHub Action as a service principal for Graph API access. | Free (part of Entra ID) |
| **Federated Identity Credential** | Configured on the App Registration to trust GitHub OIDC tokens from specific repos/branches. | Free (part of Entra ID) |
| **Microsoft Graph API Permissions** | `Sites.ReadWrite.All` or scoped `Sites.Selected` permission for the app to write to SharePoint. | Included with Microsoft 365 |
| **Azure Key Vault** *(optional)* | Stores any additional configuration (e.g., site IDs) if needed; accessed via the same OIDC identity. | Standard tier |
| **SharePoint Online Site** | Target document library where files are synced. | Existing Microsoft 365 subscription |

### 5.1 Azure AD App Registration Configuration

```
App Registration:
  Name: "GitHub-SharePoint-Sync"
  Federated Credentials:
    - Issuer: https://token.actions.githubusercontent.com
      Subject: repo:<org>/<repo>:ref:refs/heads/main
      Audience: api://AzureADTokenExchange
  API Permissions:
    - Microsoft Graph → Sites.Selected (Application)
  Admin Consent: Required (granted by tenant admin)
```

### 5.2 Scaling to Multiple Repositories

**Option A — Single App Registration with multiple Federated Credentials:**
- Add one federated credential per repository (subject claim includes repo name).
- Simpler management, single permission set.
- All repos share the same SharePoint permission scope.

**Option B — One App Registration per repository/team:**
- Each team/repo has its own App Registration with scoped `Sites.Selected` permission.
- Better isolation; each app only accesses its designated SharePoint site.
- More administrative overhead.

**Recommendation:** Start with Option A for simplicity. Migrate to Option B if tenant isolation requirements increase.

---

## 6. Security Considerations

| Concern | Mitigation |
|---------|-----------|
| Secret leakage in logs | OIDC eliminates long-lived secrets. GitHub masks tokens in logs automatically. |
| Overly broad permissions | Use `Sites.Selected` Graph permission scoped to specific SharePoint sites only. |
| Unauthorized repo triggering sync | Federated credential subject claim restricts to specific repo + branch. |
| Tampering with config file | Config file changes require PR review and merge to `main`; branch protection rules enforce review. |
| Token replay | OIDC tokens are short-lived (valid ~5 minutes) and audience-restricted. |
| Data exfiltration via workflow modification | Require CODEOWNERS approval for `.github/workflows/` changes. |

---

## 7. GitHub Actions Workflow (Conceptual)

```yaml
name: SharePoint Document Sync

on:
  pull_request:
    types: [closed]
    branches: [main]

permissions:
  id-token: write   # Required for OIDC
  contents: read    # Required to read repo files

jobs:
  sync:
    if: github.event.pull_request.merged == true
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Read sync configuration
        id: config
        # Parse .github/sharepoint-sync.yml

      - name: Azure Login (OIDC)
        uses: azure/login@v2
        with:
          client-id: ${{ secrets.AZURE_CLIENT_ID }}
          tenant-id: ${{ secrets.AZURE_TENANT_ID }}
          subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}

      - name: Sync documents to SharePoint
        # Custom action or script that:
        # 1. Gets access token for Microsoft Graph
        # 2. Reads files from source_folder
        # 3. Uploads to SharePoint via Graph API
        # 4. Optionally deletes orphaned files

      - name: Report status
        # Post summary to workflow run
```

> **Note:** `AZURE_CLIENT_ID` and `AZURE_TENANT_ID` are not secrets in the traditional sense (they are UUIDs, not credentials), but storing them as GitHub Secrets keeps configuration clean and avoids hardcoding.

---

## 8. Error Handling & Retry Strategy

| Scenario | Handling |
|----------|----------|
| Graph API rate limiting (429) | Exponential backoff with jitter, max 5 retries. |
| File upload failure | Retry individual file up to 3 times; continue with remaining files. |
| Authentication failure | Fail fast with clear error message; do not retry (likely misconfiguration). |
| Config file missing/invalid | Fail workflow with descriptive error; do not attempt sync. |
| Large files (>250 MB) | Use Graph upload session (resumable upload) for files > 4 MB. |

---

## 9. Monitoring & Observability

- **GitHub Actions Logs** — Full execution trace per run.
- **Workflow Run Summary** — Post a summary annotation with file count, bytes transferred, and any errors.
- **Azure AD Sign-in Logs** — Audit trail of token issuance.
- **Optional: Azure Application Insights** — If the custom action is deployed as a reusable action, telemetry can be sent to App Insights.

---

## 10. Implementation Plan

### Phase 1: Azure Infrastructure Setup (Day 1–2)

- [ ] Create Azure AD App Registration (`GitHub-SharePoint-Sync`).
- [ ] Configure `Sites.Selected` Microsoft Graph API permission.
- [ ] Request and obtain admin consent from tenant administrator.
- [ ] Grant the App Registration access to the target SharePoint site(s) using the `Sites.Selected` permission via Graph API call.
- [ ] Add Federated Identity Credential for the target repository (`repo:<org>/<repo>:ref:refs/heads/main`).
- [ ] Document the `client-id` and `tenant-id` values.

### Phase 2: Repository Configuration (Day 2–3)

- [ ] Add `AZURE_CLIENT_ID` and `AZURE_TENANT_ID` as GitHub repository secrets (or organization secrets for multi-repo).
- [ ] Create `.github/sharepoint-sync.yml` configuration file in the target repository.
- [ ] Configure branch protection rules on `main` (require PR reviews, CODEOWNERS for workflow files).

### Phase 3: Action Development (Day 3–7)

- [ ] Develop the sync logic (TypeScript or Python composite action):
  - YAML config parser
  - Microsoft Graph SDK integration for file upload
  - Delta detection (compare local files vs. SharePoint folder contents)
  - Resumable upload for large files
  - Orphan deletion logic
- [ ] Write unit tests for config parsing and delta logic.
- [ ] Write integration tests against a test SharePoint site.

### Phase 4: Workflow Integration (Day 7–8)

- [ ] Create the workflow YAML file (`.github/workflows/sharepoint-sync.yml`).
- [ ] Test end-to-end with a test PR merged to `main`.
- [ ] Validate logs contain no sensitive data.
- [ ] Validate correct files appear in SharePoint.

### Phase 5: Documentation & Rollout (Day 8–10)

- [ ] Write setup guide for onboarding new repositories.
- [ ] Document how to add federated credentials for additional repos.
- [ ] Create runbook for common failure scenarios.
- [ ] Roll out to first production repository.
- [ ] Monitor for 1 week; address any issues.

### Phase 6: Scale & Harden (Post-Launch)

- [ ] Evaluate Option A vs Option B for multi-repo isolation.
- [ ] Add support for organization-level reusable workflow (if multiple repos adopt).
- [ ] Add optional Azure Application Insights telemetry.
- [ ] Implement scheduled reconciliation workflow (periodic full sync as safety net).

---

## 11. Open Questions for Review

1. **Deletion policy** — Should orphaned files in SharePoint be deleted automatically, or moved to a "trash" folder for manual review?
2. **Conflict handling** — If a file exists in SharePoint with the same name but different content (modified outside the repo), should the sync overwrite it?
3. **Multi-branch support** — Is there a future need to sync from branches other than `main` (e.g., `release/*`)?
4. **File size limits** — Are there expected files larger than 250 MB that would require special handling?
5. **Notification** — Should the workflow notify a Teams channel or email on sync completion/failure?

---

## 12. Appendix: Alternative Approaches Considered

| Approach | Pros | Cons | Decision |
|----------|------|------|----------|
| Client Secret in GitHub Secrets | Simple setup | Secret rotation burden; risk of leakage | ❌ Rejected |
| Managed Identity on self-hosted runner | No secret at all | Requires self-hosted runner infrastructure | ❌ Deferred |
| OIDC Federated Credential | No long-lived secrets; GitHub-native | Requires Azure AD configuration | ✅ Selected |
| Power Automate webhook | Low-code | Hard to version control; limited error handling | ❌ Rejected |
| Azure Logic Apps | Visual workflow | Additional Azure cost; harder to test locally | ❌ Rejected |
