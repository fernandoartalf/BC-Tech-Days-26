# SharePoint Document Sync — Technical Architecture

> Automatic file synchronization from the `docs/` repository folder to a SharePoint Online document library via GitHub Actions, OIDC authentication, and Microsoft Graph API.

---

## 1. High-Level Overview

```mermaid
flowchart LR
    subgraph GitHub["GitHub Repository"]
        A["docs/ folder"]
        W["GitHub Actions Workflow"]
    end
    subgraph Azure_AD["Azure AD"]
        OIDC["OIDC / Workload Identity\nFederation"]
    end
    subgraph SharePoint["SharePoint Online"]
        SP["Documents / BC-Tech-Days-26"]
    end

    A -->|"push to main\nor manual dispatch"| W
    W -->|"1 — Request OIDC token"| OIDC
    OIDC -->|"2 — Access token\n(Sites.ReadWrite.All)"| W
    W -->|"3 — Upload via\nMicrosoft Graph API"| SP
```

---

## 2. Authentication Flow

```mermaid
sequenceDiagram
    participant GH as GitHub Actions Runner
    participant OIDC as GitHub OIDC Provider
    participant AAD as Azure AD
    participant Graph as Microsoft Graph API

    GH->>OIDC: Request OIDC JWT
    OIDC-->>GH: id_token (sub = repo:org/repo:ref:refs/heads/main)
    GH->>AAD: Exchange id_token for access_token<br/>(Federated Credential on App Registration)
    AAD-->>GH: access_token (scope: Sites.ReadWrite.All)
    GH->>Graph: API calls with Bearer token
    Graph-->>GH: 200 OK
```

**Key details:**
- **App Registration**: `GitHub-SharePoint-Sync` (Client ID: `89200c80-...`)
- **Permission**: `Sites.ReadWrite.All` (Application — admin-consented)
- **Federated Credential Subject**: `repo:AL-Copilot-Skills-Collection/BC-Tech-Days-26:ref:refs/heads/main`
- **No secrets stored** — OIDC token exchange eliminates long-lived credentials

---

## 3. Component Architecture

```mermaid
flowchart TB
    subgraph Workflow[".github/workflows/sharepoint-sync.yml"]
        T1["Trigger: push main / workflow_dispatch"]
        T2["Checkout (fetch-depth: 0)"]
        T3["Determine merge base SHAs"]
        T4["Azure Login (OIDC)"]
        T5["Invoke Composite Action"]
        T1 --> T2 --> T3 --> T4 --> T5
    end

    subgraph Action["actions/sharepoint-sync/"]
        AY["action.yml\n(setup Python, install deps)"]
        SY["sync.py\n(orchestrator)"]
        CF["config.py\n(load YAML config)"]
        DL["delta.py\n(change detection)"]
        GC["graph_client.py\n(Graph API client)"]
        AY --> SY
        SY --> CF
        SY --> DL
        SY --> GC
    end

    subgraph Config[".github/sharepoint-sync.yml"]
        C1["source_folder: docs"]
        C2["sharepoint_site: ...:/sites/BCTechDays2026"]
        C3["sharepoint_folder: /BC-Tech-Days-26"]
        C4["sync_mode: auto"]
        C5["delete_orphaned: false"]
    end

    T5 --> AY
    CF --> Config
```

---

## 4. Sync Workflow — Step by Step

```mermaid
flowchart TD
    Start(["Workflow triggered"])
    Checkout["Checkout repo\n(full history)"]
    SHAs["Compute base/head SHAs\n(HEAD~1 → HEAD)"]
    Mode{"sync_mode?"}
    GitDiff["git diff --name-status\nbase..head -- docs/"]
    FullScan["rglob('*') on docs/\n(treat all as MODIFIED)"]
    Filter{"delete_orphaned?"}
    FilterDel["Remove DELETED entries"]
    KeepAll["Keep all changes"]
    Init["GraphSyncClient.initialize()\n• Resolve site ID via httpx\n• Resolve drive ID via SDK"]
    Upload{"File size?"}
    Simple["Simple upload\n(PUT content, < 4 MB)"]
    Resumable["Resumable upload\n(upload session, 10 MB chunks)"]
    Retry{"Success?"}
    BackOff["Exponential backoff\n+ jitter (max 5 retries)"]
    Summary["Write summary to\nGITHUB_STEP_SUMMARY"]
    Done(["Done"])

    Start --> Checkout --> SHAs --> Mode
    Mode -->|"auto + SHAs present\nor git-diff"| GitDiff
    Mode -->|"full or\nno SHAs available"| FullScan
    GitDiff --> Filter
    FullScan --> Filter
    Filter -->|"false (default)"| FilterDel
    Filter -->|"true"| KeepAll
    FilterDel --> Init
    KeepAll --> Init
    Init --> Upload
    Upload -->|"< 4 MB"| Simple
    Upload -->|"≥ 4 MB"| Resumable
    Simple --> Retry
    Resumable --> Retry
    Retry -->|"No"| BackOff --> Retry
    Retry -->|"Yes"| Summary --> Done
```

---

## 5. File Upload Detail

```mermaid
flowchart LR
    subgraph Small["Simple Upload (< 4 MB)"]
        S1["Read file bytes"]
        S2["PUT to Graph SDK\n.content.put(bytes)"]
        S1 --> S2
    end

    subgraph Large["Resumable Upload (≥ 4 MB)"]
        L1["Create upload session\n(conflictBehavior: replace)"]
        L2["Read 10 MB chunk"]
        L3["PUT chunk with\nContent-Range header"]
        L4{"More chunks?"}
        L1 --> L2 --> L3 --> L4
        L4 -->|"Yes"| L2
        L4 -->|"No"| L5["Upload complete"]
    end
```

**Remote path construction:**
```
Drive root (Documents library)
  └─ /BC-Tech-Days-26/           ← sharepoint_folder
      └─ subfolder/              ← preserves repo structure
          └─ file.md             ← uploaded file
```

Graph API auto-creates intermediate folders via the `root:/path/to/file:` notation.

---

## 6. Delta Detection Modes

```mermaid
flowchart TD
    Input{"sync_mode setting"}
    Auto{"SHAs available?"}
    GitDiff["git-diff mode\n• Runs: git diff --name-status base head -- docs/\n• Detects: ADDED, MODIFIED, DELETED\n• Fast: only changed files"]
    FullScan["full mode\n• Runs: rglob('*') on docs/\n• Treats all files as MODIFIED\n• No deletion detection\n• Reliable: ignores git history"]

    Input -->|"auto"| Auto
    Input -->|"git-diff"| GitDiff
    Input -->|"full"| FullScan
    Auto -->|"Yes"| GitDiff
    Auto -->|"No"| FullScan
```

| Mode | Speed | Detects Deletions | Use Case |
|---|---|---|---|
| `auto` | Adaptive | When SHAs present | Default — best of both |
| `git-diff` | Fast | Yes | CI push events |
| `full` | Slower | No | Manual re-sync, first run |

---

## 7. Infrastructure & Security

```mermaid
flowchart LR
    subgraph Secrets["GitHub Secrets"]
        CID["AZURE_CLIENT_ID"]
        TID["AZURE_TENANT_ID"]
    end

    subgraph AppReg["Azure AD App Registration"]
        FC["Federated Credential\n(GitHub OIDC → main branch)"]
        PERM["Sites.ReadWrite.All\n(Application permission)"]
        SP_OBJ["Service Principal"]
    end

    subgraph Target["SharePoint Online"]
        SITE["Site: BCTechDays2026"]
        LIB["Documents library (default drive)"]
        FOLDER["/BC-Tech-Days-26/"]
    end

    CID --> AppReg
    TID --> AppReg
    FC --> SP_OBJ
    PERM --> SP_OBJ
    SP_OBJ -->|"Graph API"| SITE
    SITE --> LIB --> FOLDER
```

**Security posture:**
- No client secrets — OIDC only
- Federated credential scoped to `main` branch only
- `Sites.ReadWrite.All` is the minimum permission for SharePoint file upload
- Additive-only sync (`delete_orphaned: false`) — never deletes from SharePoint

---

## 8. Dependencies

| Package | Purpose |
|---|---|
| `azure-identity >=1.17.0` | `DefaultAzureCredential` / OIDC token exchange |
| `msgraph-sdk >=1.5.0` | Microsoft Graph SDK (site/drive resolution, simple upload) |
| `httpx >=0.27.0` | Direct HTTP for site resolution + resumable upload chunks |
| `PyYAML >=6.0.1` | Parse `.github/sharepoint-sync.yml` config |

---

## 9. Configuration Reference

```yaml
# .github/sharepoint-sync.yml
source_folder: "docs"                    # Repo folder to sync
sharepoint_site: "host:/sites/SiteName"  # SharePoint site (hostname:/path)
sharepoint_folder: "/BC-Tech-Days-26"    # Path inside the Documents library
delete_orphaned: false                   # Never delete from SharePoint
sync_mode: "auto"                        # auto | git-diff | full
# file_patterns:                         # Optional glob filter
#   - "**/*.md"
```
