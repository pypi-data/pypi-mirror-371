# GraphBridge — Lightweight Microsoft Graph (SharePoint Lists) client

A small Python helper to work with **Microsoft Graph**—specifically **SharePoint Lists**—using **app-only authentication** (Azure AD / Entra ID via `ClientSecretCredential`).
It exposes high-level classes to authenticate (`GbAuth`), resolve a **SharePoint Site** (`GbSite`), and read/write **Lists** (`GbList`).

---

## Features

* 🔐 App-only auth via `azure-identity` (`ClientSecretCredential`)
* 🧭 SharePoint **site resolution** (`siteId`) through Graph
* 📋 List read with **automatic pagination**
* ✍️ CRUD helpers: `create`, `update`, `delete`
* 🔁 Smart **upsert/sync** via `upload(ids, rows, force, delete)`
* 🧩 Client-side filtering with `get_items_by_features`
* 🔤 Utilities to map column names with spaces/punctuation (`encode_row` / `decode_row`)

---

## Requirements

* **Python ≥ 3.10** (uses `|` unions and `list[dict]` style hints)
* An **Entra ID (Azure AD) app** with Client ID/Secret and Graph **application** permissions:

  * Read: `Sites.Read.All`
  * Write: `Sites.ReadWrite.All`
* Dependencies:

  ```bash
  pip install azure-identity requests
  ```

> **Admin consent is required** for application permissions before calls will succeed.

---

## Installation

If the file lives inside your project:

```python
# grapbridge.py in your project
from grapbridge import GbAuth, GbSite, GbList
```

(There’s no separate package—treat it as an internal module.)

---

## Quick start

```python
import os
from grapbridge import GbAuth, GbSite, GbList

# 1) Authentication (read from env is recommended)
TENANT_ID = os.environ["AZURE_TENANT_ID"]
CLIENT_ID = os.environ["AZURE_CLIENT_ID"]
CLIENT_SECRET = os.environ["AZURE_CLIENT_SECRET"]

auth = GbAuth(tenant_id=TENANT_ID, client_id=CLIENT_ID, client_secret=CLIENT_SECRET)

# 2) SharePoint Site
site = GbSite(
    gb_auth=auth,
    hostname="contoso.sharepoint.com",
    site_path="/sites/Finance"  # include the leading slash
)

print("Site ID:", site.site_id)

# 3) List
gl = GbList(
    gb_site=site,
    list_name="Project Tracker"
)

# Read everything (fields, IDs, columns)
rows = gl.list_rows          # -> [ {<field>: <value>, ...}, ... ]
ids  = gl.list_ids           # -> ["1","2",...]
cols = gl.list_fields        # -> list of field names

print("Items count:", len(rows))
print("First 3 rows:", rows[:3])
```

---

## Key concepts

* **Hostname**: your SharePoint tenant domain, e.g., `contoso.sharepoint.com`.
* **Site path**: path with a leading slash, e.g., `/sites/Finance`.
* **List name**: the display title of the list, e.g., `Project Tracker`.
* **Graph base**: all calls go to `https://graph.microsoft.com/v1.0/...` with `Authorization: Bearer <token>`.

---

## High-level API

### `GbAuth`

App-only auth via Azure AD.

```python
GbAuth(tenant_id: str, client_id: str, client_secret: str)

# Handy properties (lazy, cached)
auth.credential  # ClientSecretCredential
auth.token       # JWT access token string
auth.headers     # {"Authorization": "Bearer <token>"}
```

**May raise**

* `ValueError` / `TypeError` for invalid inputs
* `RuntimeError` if token acquisition fails

---

### `GbSite(GbAuth)`

Represents a SharePoint site.

```python
GbSite(hostname: str, site_path: str, gb_auth: GbAuth | None = None, ...)

site.site_url   # Graph site endpoint
site.site_data  # dict (lazy; GET /sites/{hostname}:{site_path})
site.site_id    # site id
```

> You can provide a `GbAuth` instance (recommended) or pass credentials directly.

---

### `GbList(GbSite)`

List operations.

```python
GbList(list_name: str, gb_site: GbSite | None = None, ...)

gl.list_url     # Graph list endpoint
gl.list_data    # list metadata (lazy)
gl.list_id      # list id
```

#### Reading

```python
gl.list_items       # First page only (expand=fields) – no pagination
gl.list_items_all   # Property with automatic pagination (@odata.nextLink)
gl.list_rows        # [item["fields"] for item in list_items_all]
gl.list_ids         # ["1","2",...]
gl.list_fields      # keys from the first row (or [])
```

> `list_items_all` uses `$top=200` internally and will fetch **all** pages.
> It’s a **property** (no parenthesis) and may perform multiple HTTP requests.

#### Writing (CRUD)

```python
# CREATE: accepts a dict or a list of dicts (fields)
gl.create(rows={"Title": "New", "Status": "Active"})
gl.create(rows=[{"Title": "A"}, {"Title": "B"}])

# UPDATE: id(s) + dict/list of dicts (1:1)
gl.update(ids="12",           rows={"Status": "Closed"})
gl.update(ids=["12","15"],    rows=[{"Status":"Closed"}, {"Status":"Open"}])

# DELETE: single id or a collection
gl.delete(ids="12")
gl.delete(ids={"12","13","14"})  # set/list/tuple are fine
```

**Return shape (general)**
All mutating methods return a **result object** with `successes` / `failures`.
Example for `update`:

```json
{
  "successes": [
    {"id": "12", "success": true, "updated_row": {"id": "12", "Title": "X", "...": "..."}}
  ],
  "failures": [
    {"id": "15", "success": false, "error": "Error updating: 404 ..."}
  ]
}
```

#### Advanced upsert/sync

```python
gl.upload(
  ids=["1","2","9"],    # logical keys to keep
  rows=[
    {"Title":"Row 1"},
    {"Title":"Row 2"},
    {"Title":"Row 9"}
  ],
  force=False,          # True = replace (delete+create) if ID exists
  delete=True           # True = delete items not in ids
)
```

**Behavior of `upload`**

* If `delete=True`: remove **existing** items whose IDs are **not** in `ids`.
* For each ID in `ids`:

  * If it **exists**:

    * `force=True` → **replace** (delete + create). The **new item** gets a **new Graph id**; the result includes `new_id`.
    * `force=False` → **update** (PATCH).
  * If it **doesn’t exist** → **create**.

**Return (shape):**

```json
{
  "delete_results": {"successes": [...], "failures": [...] | null},
  "force_results": {
    "replaced": {"successes": [...], "failures": [...]},
    "updated":  {"successes": [...], "failures": [...]},
    "created":  {"successes": [...], "failures": [...]}
  }
}
```

---

## Column names with spaces/punctuation

Microsoft Graph often encodes field keys like `Project_x0020_Name` for “Project Name”.
`GbList` provides utilities to convert automatically:

```python
# Encoding map (excerpt)
gl.encode_map   # {' ': '_x0020_', '/': '_x002f_', '(': '_x0028_', ')': '_x0029_', ...}

# Convert human keys -> Graph-encoded keys
row_api = gl.encode_row({"Project Name": "ABC", "Cost (USD)": 123.45})
# -> {"Project_x0020_Name": "ABC", "Cost_x0020__x0028_USD_x0029_": 123.45}

# Decode back (Graph payload -> human keys)
row_human = gl.decode_row(row_api)
```

> **Tip**: if your column names have spaces/symbols, always pass data to `create`/`update` through `encode_row(...)`.

---

## Client-side filtering

```python
# Returns the raw Graph “item” dicts (not just fields) that match
# AT LEAST one block (OR across dicts). Inside each block: AND.
matches = gl.get_items_by_features([
  {"fields": {"Status": "Active"}},  # nested: match inside "fields"
  {"id": "12"}                       # flat: match top-level keys of the item
])

only_fields = [i["fields"] for i in matches]
```

* Supports **one nesting level**, e.g., `{"fields": {"Column": "Value"}}`.
* Results are **de-duplicated**.

> *Note*: iterates `list_items_all` (with `expand=fields`).
> To filter by list fields, use the nested **`"fields": {...}`** shape.

---

## Practical snippets

### Create multiple items with “human” column names

```python
new_rows_human = [
  {"Project Name": "Mars", "Status": "Active"},
  {"Project Name": "Venus", "Status": "Pending"}
]
gl.create(rows=[gl.encode_row(r) for r in new_rows_human])
```

### Bulk update

```python
ids = ["101", "102", "103"]
patches = [{"Status": "Closed"} for _ in ids]
gl.update(ids=ids, rows=patches)
```

### Keep your source of truth in sync (remove anything else)

```python
source_ids = ["1","2","3"]
source_rows = [{"Title": "A"}, {"Title": "B"}, {"Title": "C"}]
gl.upload(ids=source_ids, rows=source_rows, force=False, delete=True)
```

---

## Error handling

Methods may raise:

* `ValueError` / `TypeError` for invalid inputs
* `RuntimeError` for non-2xx HTTP responses (includes Graph message)

Example:

```python
try:
    gl.update(ids="999", rows={"Status": "Closed"})
except (ValueError, TypeError, RuntimeError) as e:
    print("Operation failed:", e)
```

---

## Best practices

* **Don’t** hard-code secrets—use env vars:

  ```bash
  export AZURE_TENANT_ID=...
  export AZURE_CLIENT_ID=...
  export AZURE_CLIENT_SECRET=...
  ```
* Ensure `site_path` starts with `/` (e.g., `/sites/Finance`).
* For large datasets use `gl.list_rows` (auto-pagination).
* For columns with spaces/symbols use `encode_row` / `decode_row`.
* With `upload(force=True)`, remember the Graph **ID can change** (see `new_id`).

---

## Graph endpoints used (simplified)

* Site: `GET https://graph.microsoft.com/v1.0/sites/{hostname}:{site_path}`
* List (metadata): `GET https://graph.microsoft.com/v1.0/sites/{siteId}/lists/{listNameEncoded}`
* Items:

  * Read: `GET .../items?expand=fields`
  * Create: `POST .../items` body: `{"fields": {...}}`
  * Update fields: `PATCH .../items/{id}/fields` body: `{...}`
  * Delete: `DELETE .../items/{id}`

---

## FAQ

**Q: My “Project Name” column doesn’t update.**
A: It’s likely a key-encoding issue. Use `gl.encode_row({"Project Name": "..."})` before `create`/`update`.

**Q: `list_items` doesn’t return everything.**
A: Use `gl.list_items_all` or `gl.list_rows` (auto-pagination).

**Q: Which permissions do I need?**
A: App-only: `Sites.Read.All` to read, `Sites.ReadWrite.All` to write, and **admin consent**.
