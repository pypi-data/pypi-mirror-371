# SpearheadClient

**SpearheadClient** is a type-safe Python SDK for interacting with your organization's SpearheadOps data
using prepared calls via a GraphQL API. You can also write your own strongly-typed GraphQL queries using Pydantic models.

## 📦 Installation

Install the latest version using pip:

```bash
pip install spearheadclient
```

## Client

The Client class provides methods for interacting with the Spearhead API. It requires an authenticated HTTP client to be initialized.

### Initialization

The Client requires an authenticated HTTP client to be passed during initialization. The recommended way is to use the AuthInfinityHttpClient:

```python
from SpearheadClient import Client
from SpearheadClient.AuthInfinity.AuthInfinityHttpClient import AuthInfinityHttpClient

# Initialize the HTTP client with your credentials
http_client = AuthInfinityHttpClient(
    access_key="your_access_key",
    secret_key="your_secret_key"
)

# Initialize the main client with the HTTP client
client = Client(http_client=http_client)
```

### Authentication

The AuthInfinityHttpClient handles authentication automatically. It will:

1. Authenticate using the provided access_key and secret_key
2. Automatically refresh tokens when they expire
3. Handle 401 unauthorized responses by re-authenticating
4. Manage JWT tokens and their expiration

The client will automatically handle token refresh and re-authentication when needed, so you don't need to manage the authentication state manually.

### Available Methods

The Client class provides the following methods:

#### work_site_search

Search for work sites with filtering and pagination.

```python
results = await client.work_site_search(
    where={"deleted_at": {"_is_null": True}},
    query="search term",  # optional
    order_by=[{"created_at": "desc"}],  # optional
    limit=10,  # optional
    offset=0  # optional
)

for ws in results.work_sites:
  print(ws.title)
```

#### work_site_detail

Get detailed information about a specific work site.

```python
work_site = await client.work_site_detail(
    work_site_id="uuid-of-work-site"
)

print(work_site.work_site.title)
```

#### work_site_ownership

Get ownership information for a work site.

```python
results = await client.work_site_ownership(
    work_site_id="uuid-of-work-site"
)

for wso in results.work_site_owners:
    print(f"{wso.customer.title}: {wso.started_at} - {wso.ended_at}")
```

#### work_site_ticket_activity

Get ticket activity details for a work site.

```python
results = await client.work_site_ticket_activity(
    work_site_id="c8ef0e2d-507d-489f-a83f-69460b68e77f"
)

for ta in results.work_site_tickets:
    print(f"{ta.ticket_id}: {ta.started_at} - {ta.ended_at}")
```

### Sending a Custom Query

You can also define your own queries and mutations.

```python
from SpearheadClient import execute_sync

def get_worksites_in_state(state: str):
    query = """
query WorkSitesInState($state: String!) {
  work_sites(state: {_eq_: $state}}) {
    title
    state
  }
}
"""
    variables = {"state": state}
    response = execute_sync(client, query, variables)
    return response["WorkSitesInState"]
```

## 🛡 License

MIT License. See `LICENSE` file for details.
