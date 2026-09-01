# AgentSessionAdministrationApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**bulkControlAgentSessionsApiV1AdminAgentSessionsActionsPost**](AgentSessionAdministrationApi.md#bulkcontrolagentsessionsapiv1adminagentsessionsactionspost) | **POST** /api/v1/admin/agent-sessions/actions | Bulk Control Agent Sessions |
| [**getAgentSessionInstanceAggregateApiV1AdminAgentSessionsAggregateGet**](AgentSessionAdministrationApi.md#getagentsessioninstanceaggregateapiv1adminagentsessionsaggregateget) | **GET** /api/v1/admin/agent-sessions/aggregate | Get Agent Session Instance Aggregate |
| [**getAgentSessionPolicyRevisionApiV1AdminAgentSessionPoliciesPolicyIdGet**](AgentSessionAdministrationApi.md#getagentsessionpolicyrevisionapiv1adminagentsessionpoliciespolicyidget) | **GET** /api/v1/admin/agent-session-policies/{policy_id} | Get Agent Session Policy Revision |
| [**getEffectiveAgentSessionPoliciesApiV1AdminAgentSessionPoliciesEffectiveGet**](AgentSessionAdministrationApi.md#geteffectiveagentsessionpoliciesapiv1adminagentsessionpolicieseffectiveget) | **GET** /api/v1/admin/agent-session-policies/effective | Get Effective Agent Session Policies |
| [**listAgentSessionFleetApiV1AdminAgentSessionsGet**](AgentSessionAdministrationApi.md#listagentsessionfleetapiv1adminagentsessionsget) | **GET** /api/v1/admin/agent-sessions | List Agent Session Fleet |
| [**listAgentSessionPoliciesApiV1AdminAgentSessionPoliciesGet**](AgentSessionAdministrationApi.md#listagentsessionpoliciesapiv1adminagentsessionpoliciesget) | **GET** /api/v1/admin/agent-session-policies | List Agent Session Policies |
| [**putAgentSessionPolicyApiV1AdminAgentSessionPoliciesPut**](AgentSessionAdministrationApi.md#putagentsessionpolicyapiv1adminagentsessionpoliciesput) | **PUT** /api/v1/admin/agent-session-policies | Put Agent Session Policy |



## bulkControlAgentSessionsApiV1AdminAgentSessionsActionsPost

> AgentSessionBulkActionResponse bulkControlAgentSessionsApiV1AdminAgentSessionsActionsPost(agentSessionBulkActionRequest, authorization, xAmeshCSRF, xAmeshTenant)

Bulk Control Agent Sessions

Apply bounded, independently fenced lifecycle controls to agent sessions.

### Example

```ts
import {
  Configuration,
  AgentSessionAdministrationApi,
} from '@amesh/client';
import type { BulkControlAgentSessionsApiV1AdminAgentSessionsActionsPostRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new AgentSessionAdministrationApi();

  const body = {
    // AgentSessionBulkActionRequest
    agentSessionBulkActionRequest: ...,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies BulkControlAgentSessionsApiV1AdminAgentSessionsActionsPostRequest;

  try {
    const data = await api.bulkControlAgentSessionsApiV1AdminAgentSessionsActionsPost(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **agentSessionBulkActionRequest** | AgentSessionBulkActionRequest |  | |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

**AgentSessionBulkActionResponse**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **207** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## getAgentSessionInstanceAggregateApiV1AdminAgentSessionsAggregateGet

> AgentSessionInstanceAggregate getAgentSessionInstanceAggregateApiV1AdminAgentSessionsAggregateGet(authorization, xAmeshCSRF)

Get Agent Session Instance Aggregate

Return instance-wide metadata-only totals without exposing tenant session rows.

### Example

```ts
import {
  Configuration,
  AgentSessionAdministrationApi,
} from '@amesh/client';
import type { GetAgentSessionInstanceAggregateApiV1AdminAgentSessionsAggregateGetRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new AgentSessionAdministrationApi();

  const body = {
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
  } satisfies GetAgentSessionInstanceAggregateApiV1AdminAgentSessionsAggregateGetRequest;

  try {
    const data = await api.getAgentSessionInstanceAggregateApiV1AdminAgentSessionsAggregateGet(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

**AgentSessionInstanceAggregate**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## getAgentSessionPolicyRevisionApiV1AdminAgentSessionPoliciesPolicyIdGet

> AgentSessionPolicyRevision getAgentSessionPolicyRevisionApiV1AdminAgentSessionPoliciesPolicyIdGet(policyId, revision, authorization, xAmeshCSRF, xAmeshTenant)

Get Agent Session Policy Revision

### Example

```ts
import {
  Configuration,
  AgentSessionAdministrationApi,
} from '@amesh/client';
import type { GetAgentSessionPolicyRevisionApiV1AdminAgentSessionPoliciesPolicyIdGetRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new AgentSessionAdministrationApi();

  const body = {
    // string
    policyId: 38400000-8cf0-11bd-b23e-10b96e4ef00d,
    // number (optional)
    revision: 56,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies GetAgentSessionPolicyRevisionApiV1AdminAgentSessionPoliciesPolicyIdGetRequest;

  try {
    const data = await api.getAgentSessionPolicyRevisionApiV1AdminAgentSessionPoliciesPolicyIdGet(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **policyId** | `string` |  | [Defaults to `undefined`] |
| **revision** | `number` |  | [Optional] [Defaults to `undefined`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

**AgentSessionPolicyRevision**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## getEffectiveAgentSessionPoliciesApiV1AdminAgentSessionPoliciesEffectiveGet

> Array&lt;AgentSessionPolicyRevision&gt; getEffectiveAgentSessionPoliciesApiV1AdminAgentSessionPoliciesEffectiveGet(namespace, applicationId, authorization, xAmeshCSRF, xAmeshTenant)

Get Effective Agent Session Policies

### Example

```ts
import {
  Configuration,
  AgentSessionAdministrationApi,
} from '@amesh/client';
import type { GetEffectiveAgentSessionPoliciesApiV1AdminAgentSessionPoliciesEffectiveGetRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new AgentSessionAdministrationApi();

  const body = {
    // string
    namespace: namespace_example,
    // string (optional)
    applicationId: applicationId_example,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies GetEffectiveAgentSessionPoliciesApiV1AdminAgentSessionPoliciesEffectiveGetRequest;

  try {
    const data = await api.getEffectiveAgentSessionPoliciesApiV1AdminAgentSessionPoliciesEffectiveGet(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **namespace** | `string` |  | [Defaults to `undefined`] |
| **applicationId** | `string` |  | [Optional] [Defaults to `undefined`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

**Array&lt;AgentSessionPolicyRevision&gt;**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## listAgentSessionFleetApiV1AdminAgentSessionsGet

> AgentSessionFleetPage listAgentSessionFleetApiV1AdminAgentSessionsGet(limit, cursor, state, namespace, agentRef, ownerId, harness, createdFrom, createdTo, authorization, xAmeshCSRF, xAmeshTenant)

List Agent Session Fleet

Return a bounded, tenant-isolated administrative session fleet projection.

### Example

```ts
import {
  Configuration,
  AgentSessionAdministrationApi,
} from '@amesh/client';
import type { ListAgentSessionFleetApiV1AdminAgentSessionsGetRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new AgentSessionAdministrationApi();

  const body = {
    // number (optional)
    limit: 56,
    // string (optional)
    cursor: cursor_example,
    // string (optional)
    state: state_example,
    // string (optional)
    namespace: namespace_example,
    // string (optional)
    agentRef: agentRef_example,
    // string (optional)
    ownerId: ownerId_example,
    // string (optional)
    harness: harness_example,
    // Date (optional)
    createdFrom: 2013-10-20T19:20:30+01:00,
    // Date (optional)
    createdTo: 2013-10-20T19:20:30+01:00,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies ListAgentSessionFleetApiV1AdminAgentSessionsGetRequest;

  try {
    const data = await api.listAgentSessionFleetApiV1AdminAgentSessionsGet(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **limit** | `number` |  | [Optional] [Defaults to `100`] |
| **cursor** | `string` |  | [Optional] [Defaults to `undefined`] |
| **state** | `string` |  | [Optional] [Defaults to `undefined`] |
| **namespace** | `string` |  | [Optional] [Defaults to `undefined`] |
| **agentRef** | `string` |  | [Optional] [Defaults to `undefined`] |
| **ownerId** | `string` |  | [Optional] [Defaults to `undefined`] |
| **harness** | `string` |  | [Optional] [Defaults to `undefined`] |
| **createdFrom** | `Date` |  | [Optional] [Defaults to `undefined`] |
| **createdTo** | `Date` |  | [Optional] [Defaults to `undefined`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

**AgentSessionFleetPage**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## listAgentSessionPoliciesApiV1AdminAgentSessionPoliciesGet

> Array&lt;AgentSessionPolicyRevision&gt; listAgentSessionPoliciesApiV1AdminAgentSessionPoliciesGet(namespace, applicationId, limit, authorization, xAmeshCSRF, xAmeshTenant)

List Agent Session Policies

### Example

```ts
import {
  Configuration,
  AgentSessionAdministrationApi,
} from '@amesh/client';
import type { ListAgentSessionPoliciesApiV1AdminAgentSessionPoliciesGetRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new AgentSessionAdministrationApi();

  const body = {
    // string (optional)
    namespace: namespace_example,
    // string (optional)
    applicationId: applicationId_example,
    // number (optional)
    limit: 56,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies ListAgentSessionPoliciesApiV1AdminAgentSessionPoliciesGetRequest;

  try {
    const data = await api.listAgentSessionPoliciesApiV1AdminAgentSessionPoliciesGet(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **namespace** | `string` |  | [Optional] [Defaults to `undefined`] |
| **applicationId** | `string` |  | [Optional] [Defaults to `undefined`] |
| **limit** | `number` |  | [Optional] [Defaults to `100`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

**Array&lt;AgentSessionPolicyRevision&gt;**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## putAgentSessionPolicyApiV1AdminAgentSessionPoliciesPut

> AgentSessionPolicyRevision putAgentSessionPolicyApiV1AdminAgentSessionPoliciesPut(agentSessionPolicyUpsertRequest, authorization, xAmeshCSRF, xAmeshTenant)

Put Agent Session Policy

### Example

```ts
import {
  Configuration,
  AgentSessionAdministrationApi,
} from '@amesh/client';
import type { PutAgentSessionPolicyApiV1AdminAgentSessionPoliciesPutRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new AgentSessionAdministrationApi();

  const body = {
    // AgentSessionPolicyUpsertRequest
    agentSessionPolicyUpsertRequest: ...,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies PutAgentSessionPolicyApiV1AdminAgentSessionPoliciesPutRequest;

  try {
    const data = await api.putAgentSessionPolicyApiV1AdminAgentSessionPoliciesPut(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **agentSessionPolicyUpsertRequest** | AgentSessionPolicyUpsertRequest |  | |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

**AgentSessionPolicyRevision**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)
