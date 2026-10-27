# Workspace, personal configuration and credentials

<!-- README-I18N:START -->

**English** | [中文](storage-and-credentials_ZH.md)

<!-- README-I18N:END -->


Share code and rules; keep each member's data, actual paths and authentication separate. Concrete capability mappings belong in the relevant skills and classified guides, not general storage rules.

## 1. Storage roles

| Location | Contents | Boundary |
|---|---|---|
| Repository | Reusable code, documentation, schemas and public examples | No actual data, secrets or personal mappings |
| `AIRMOSAIC_LOCAL_WORKSPACE` | Cache, new results, local receipts and temporary files | No authentication or credentials |
| `AIRMOSAIC_CONFIG_DIR` | Non-secret mappings and preferences | Explicitly reviewed/loaded, no secrets |
| `AIRMOSAIC_AUTH_DIR` | Necessary member-owned browser state | Restricted access; no data or shared outputs |
| External resource root | Authorized releases and existing external resources | Separate configured read-only input; no implied edit permission |

All personal roots must exist separately outside Git. A shared input root may be read-only, but writable tasks remain member-specific. Repository `config/examples/` is different from personal configuration. Setting a variable does not launch a browser, authenticate, load configuration or authorize modification. `.env` is not automatically loaded.

Within the workspace use `data_cache/<source>/`, `output/<run_id>/<tool>/`, `runs/<run_id>/` and `temp/<run_id>/`. Browser profiles use `browser_profiles/<service>/` in the authentication root. Directory labels are logical examples, not personal paths.

## 2. Setup and routine use

1. Inspect the repository and existing directories without replacing data or settings.
2. Review/copy the [environment example](../config/examples/README.md) outside Git and explicitly load the approved session settings.
3. Ensure roots do not overlap or nest, and are outside every checkout. Do not make a data root the parent of authentication.
4. Allocate a unique task ID and map actual output parameters to its output directory. Configuration filenames grant no authority.
5. The user handles login when needed. Report sanitized states such as ready, needs_auth or permission_denied, not credentials. A common authentication adapter is not implemented.
6. Review diffs, logs and attachments before authorized sharing. Local complete records may contain needed paths, but never authentication secrets.

Use OS permissions to restrict authentication to the intended member. Do not grant all members access. Directory permissions and secret storage are different controls; agents under the same OS identity often share file access.

## 3. Credential handling

| Material | Storage/use | Maintenance |
|---|---|---|
| Repository access | Reviewed credential helper or individual private-key storage | User-managed login, device/purpose separation; share public keys only |
| Website passwords and multifactor factors | Personal secret manager and interactive login | Agents do not collect passwords/recovery codes or try accounts in bulk |
| Browser authentication | Member/service-specific profile under AUTH_DIR | Reauthenticate on expiry/account changes; do not copy sessions |
| API credentials | OS/team secret storage, injected only when needed | Restrict scope, purpose and lifetime; rotation requires authority |
| Automation secrets | Platform-supported protected secret storage and a suitable identity | Least privilege; no personal browser sessions |

Environment variables transmit values; they are not encrypted storage. Do not place secrets in commands, examples, agent instructions, snapshots or logs. Do not create plaintext secret templates or ordinary configuration files containing passwords.

A user-prepared protected secret file may be internally reused only by the specifically authorized trusted client/task. The agent must not open, parse, print, copy, migrate, modify or hash its contents, or publish its path/fingerprint. Keep it in the client's protected existing location; it is not ordinary CONFIG_DIR configuration. Do not infer permission for other clients or scan other credentials. Prefer a secret manager.

Dedicated profiles access only task-relevant sites, not unrelated personal accounts. Debug endpoints are local and authorized, never public. Process exit does not prove session destruction. Follow [agent boundaries](agent-boundaries.md).

## 4. Capability-independent mapping

Inputs come from authorized cache or read-only sources. Fresh downloads go into a new task's raw area; processed results and quality summaries are separate. Cache publication is a separate authorized operation. Parameters go in CONFIG_DIR and sessions in AUTH_DIR. Exact flags, resources and loaders belong in the skill; templates must be inspected/adapted before execution.

Do not assume a template is harmless to load: it may reset settings or write into its input tree. Explicit output mapping is required. Direct scripts do not automatically inherit runner checks, startup isolation or sanitized receipts.

## 5. Legacy data and handoff

- Do not automatically move/delete existing outputs, logs, temporary directories or sessions. Old tasks continue to reference their original paths.
- Retire mixed secret/profile locations for new tasks without copying sessions. The user may close an old browser and reauthenticate. Empty placeholders need not be deleted.
- Data backups include only authorized data/results. Authentication stays out of archives, issues, reviews, shared drives and cross-member synchronization. Secret backups need a separate encrypted scheme.
- Ignore rules reduce accidental commits; they do not encrypt files, restrict access or protect already tracked content. Report suspected leakage by location/category; revocation and history changes require specific authority.
- Read-only queries check declared path metadata, not secret contents. Supported runner adapters apply path preflight, minimal environments and sanitized receipts. Personal configuration/authentication roots are not passed wholesale to child processes. Existing-session tools need task-owned session verification. A credential broker and OS sandbox remain unimplemented.
