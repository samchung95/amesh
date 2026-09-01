# \AgentSessionAdministrationAPI

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**BulkControlAgentSessionsApiV1AdminAgentSessionsActionsPost**](AgentSessionAdministrationAPI.md#BulkControlAgentSessionsApiV1AdminAgentSessionsActionsPost) | **Post** /api/v1/admin/agent-sessions/actions | Bulk Control Agent Sessions
[**GetAgentSessionInstanceAggregateApiV1AdminAgentSessionsAggregateGet**](AgentSessionAdministrationAPI.md#GetAgentSessionInstanceAggregateApiV1AdminAgentSessionsAggregateGet) | **Get** /api/v1/admin/agent-sessions/aggregate | Get Agent Session Instance Aggregate
[**GetAgentSessionPolicyRevisionApiV1AdminAgentSessionPoliciesPolicyIdGet**](AgentSessionAdministrationAPI.md#GetAgentSessionPolicyRevisionApiV1AdminAgentSessionPoliciesPolicyIdGet) | **Get** /api/v1/admin/agent-session-policies/{policy_id} | Get Agent Session Policy Revision
[**GetEffectiveAgentSessionPoliciesApiV1AdminAgentSessionPoliciesEffectiveGet**](AgentSessionAdministrationAPI.md#GetEffectiveAgentSessionPoliciesApiV1AdminAgentSessionPoliciesEffectiveGet) | **Get** /api/v1/admin/agent-session-policies/effective | Get Effective Agent Session Policies
[**ListAgentSessionFleetApiV1AdminAgentSessionsGet**](AgentSessionAdministrationAPI.md#ListAgentSessionFleetApiV1AdminAgentSessionsGet) | **Get** /api/v1/admin/agent-sessions | List Agent Session Fleet
[**ListAgentSessionPoliciesApiV1AdminAgentSessionPoliciesGet**](AgentSessionAdministrationAPI.md#ListAgentSessionPoliciesApiV1AdminAgentSessionPoliciesGet) | **Get** /api/v1/admin/agent-session-policies | List Agent Session Policies
[**PutAgentSessionPolicyApiV1AdminAgentSessionPoliciesPut**](AgentSessionAdministrationAPI.md#PutAgentSessionPolicyApiV1AdminAgentSessionPoliciesPut) | **Put** /api/v1/admin/agent-session-policies | Put Agent Session Policy



## BulkControlAgentSessionsApiV1AdminAgentSessionsActionsPost

> AgentSessionBulkActionResponse BulkControlAgentSessionsApiV1AdminAgentSessionsActionsPost(ctx).AgentSessionBulkActionRequest(agentSessionBulkActionRequest).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Bulk Control Agent Sessions



### Example

```go
package main

import (
	"context"
	"fmt"
	"os"
	openapiclient "github.com/amesh/amesh-client-go"
)

func main() {
	agentSessionBulkActionRequest := *openapiclient.NewAgentSessionBulkActionRequest("Action_example", "Confirmation_example", []openapiclient.AgentSessionBulkActionItem{*openapiclient.NewAgentSessionBulkActionItem(int32(123), int32(123), "SessionId_example")}, "Reason_example") // AgentSessionBulkActionRequest |
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.AgentSessionAdministrationAPI.BulkControlAgentSessionsApiV1AdminAgentSessionsActionsPost(context.Background()).AgentSessionBulkActionRequest(agentSessionBulkActionRequest).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `AgentSessionAdministrationAPI.BulkControlAgentSessionsApiV1AdminAgentSessionsActionsPost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `BulkControlAgentSessionsApiV1AdminAgentSessionsActionsPost`: AgentSessionBulkActionResponse
	fmt.Fprintf(os.Stdout, "Response from `AgentSessionAdministrationAPI.BulkControlAgentSessionsApiV1AdminAgentSessionsActionsPost`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiBulkControlAgentSessionsApiV1AdminAgentSessionsActionsPostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **agentSessionBulkActionRequest** | **AgentSessionBulkActionRequest** |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

**AgentSessionBulkActionResponse**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## GetAgentSessionInstanceAggregateApiV1AdminAgentSessionsAggregateGet

> AgentSessionInstanceAggregate GetAgentSessionInstanceAggregateApiV1AdminAgentSessionsAggregateGet(ctx).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).Execute()

Get Agent Session Instance Aggregate



### Example

```go
package main

import (
	"context"
	"fmt"
	"os"
	openapiclient "github.com/amesh/amesh-client-go"
)

func main() {
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.AgentSessionAdministrationAPI.GetAgentSessionInstanceAggregateApiV1AdminAgentSessionsAggregateGet(context.Background()).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `AgentSessionAdministrationAPI.GetAgentSessionInstanceAggregateApiV1AdminAgentSessionsAggregateGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `GetAgentSessionInstanceAggregateApiV1AdminAgentSessionsAggregateGet`: AgentSessionInstanceAggregate
	fmt.Fprintf(os.Stdout, "Response from `AgentSessionAdministrationAPI.GetAgentSessionInstanceAggregateApiV1AdminAgentSessionsAggregateGet`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiGetAgentSessionInstanceAggregateApiV1AdminAgentSessionsAggregateGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |

### Return type

**AgentSessionInstanceAggregate**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## GetAgentSessionPolicyRevisionApiV1AdminAgentSessionPoliciesPolicyIdGet

> AgentSessionPolicyRevision GetAgentSessionPolicyRevisionApiV1AdminAgentSessionPoliciesPolicyIdGet(ctx, policyId).Revision(revision).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Get Agent Session Policy Revision

### Example

```go
package main

import (
	"context"
	"fmt"
	"os"
	openapiclient "github.com/amesh/amesh-client-go"
)

func main() {
	policyId := "38400000-8cf0-11bd-b23e-10b96e4ef00d" // string |
	revision := int32(56) // int32 |  (optional)
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.AgentSessionAdministrationAPI.GetAgentSessionPolicyRevisionApiV1AdminAgentSessionPoliciesPolicyIdGet(context.Background(), policyId).Revision(revision).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `AgentSessionAdministrationAPI.GetAgentSessionPolicyRevisionApiV1AdminAgentSessionPoliciesPolicyIdGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `GetAgentSessionPolicyRevisionApiV1AdminAgentSessionPoliciesPolicyIdGet`: AgentSessionPolicyRevision
	fmt.Fprintf(os.Stdout, "Response from `AgentSessionAdministrationAPI.GetAgentSessionPolicyRevisionApiV1AdminAgentSessionPoliciesPolicyIdGet`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**policyId** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiGetAgentSessionPolicyRevisionApiV1AdminAgentSessionPoliciesPolicyIdGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------

 **revision** | **int32** |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

**AgentSessionPolicyRevision**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## GetEffectiveAgentSessionPoliciesApiV1AdminAgentSessionPoliciesEffectiveGet

> []AgentSessionPolicyRevision GetEffectiveAgentSessionPoliciesApiV1AdminAgentSessionPoliciesEffectiveGet(ctx).Namespace(namespace).ApplicationId(applicationId).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Get Effective Agent Session Policies

### Example

```go
package main

import (
	"context"
	"fmt"
	"os"
	openapiclient "github.com/amesh/amesh-client-go"
)

func main() {
	namespace := "namespace_example" // string |
	applicationId := "applicationId_example" // string |  (optional)
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.AgentSessionAdministrationAPI.GetEffectiveAgentSessionPoliciesApiV1AdminAgentSessionPoliciesEffectiveGet(context.Background()).Namespace(namespace).ApplicationId(applicationId).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `AgentSessionAdministrationAPI.GetEffectiveAgentSessionPoliciesApiV1AdminAgentSessionPoliciesEffectiveGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `GetEffectiveAgentSessionPoliciesApiV1AdminAgentSessionPoliciesEffectiveGet`: []AgentSessionPolicyRevision
	fmt.Fprintf(os.Stdout, "Response from `AgentSessionAdministrationAPI.GetEffectiveAgentSessionPoliciesApiV1AdminAgentSessionPoliciesEffectiveGet`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiGetEffectiveAgentSessionPoliciesApiV1AdminAgentSessionPoliciesEffectiveGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **namespace** | **string** |  |
 **applicationId** | **string** |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**[]AgentSessionPolicyRevision**](AgentSessionPolicyRevision.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## ListAgentSessionFleetApiV1AdminAgentSessionsGet

> AgentSessionFleetPage ListAgentSessionFleetApiV1AdminAgentSessionsGet(ctx).Limit(limit).Cursor(cursor).State(state).Namespace(namespace).AgentRef(agentRef).OwnerId(ownerId).Harness(harness).CreatedFrom(createdFrom).CreatedTo(createdTo).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

List Agent Session Fleet



### Example

```go
package main

import (
	"context"
	"fmt"
	"os"
    "time"
	openapiclient "github.com/amesh/amesh-client-go"
)

func main() {
	limit := int32(56) // int32 |  (optional) (default to 100)
	cursor := "cursor_example" // string |  (optional)
	state := "state_example" // string |  (optional)
	namespace := "namespace_example" // string |  (optional)
	agentRef := "agentRef_example" // string |  (optional)
	ownerId := "ownerId_example" // string |  (optional)
	harness := "harness_example" // string |  (optional)
	createdFrom := time.Now() // time.Time |  (optional)
	createdTo := time.Now() // time.Time |  (optional)
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.AgentSessionAdministrationAPI.ListAgentSessionFleetApiV1AdminAgentSessionsGet(context.Background()).Limit(limit).Cursor(cursor).State(state).Namespace(namespace).AgentRef(agentRef).OwnerId(ownerId).Harness(harness).CreatedFrom(createdFrom).CreatedTo(createdTo).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `AgentSessionAdministrationAPI.ListAgentSessionFleetApiV1AdminAgentSessionsGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `ListAgentSessionFleetApiV1AdminAgentSessionsGet`: AgentSessionFleetPage
	fmt.Fprintf(os.Stdout, "Response from `AgentSessionAdministrationAPI.ListAgentSessionFleetApiV1AdminAgentSessionsGet`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiListAgentSessionFleetApiV1AdminAgentSessionsGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **limit** | **int32** |  | [default to 100]
 **cursor** | **string** |  |
 **state** | **string** |  |
 **namespace** | **string** |  |
 **agentRef** | **string** |  |
 **ownerId** | **string** |  |
 **harness** | **string** |  |
 **createdFrom** | **time.Time** |  |
 **createdTo** | **time.Time** |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

**AgentSessionFleetPage**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## ListAgentSessionPoliciesApiV1AdminAgentSessionPoliciesGet

> []AgentSessionPolicyRevision ListAgentSessionPoliciesApiV1AdminAgentSessionPoliciesGet(ctx).Namespace(namespace).ApplicationId(applicationId).Limit(limit).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

List Agent Session Policies

### Example

```go
package main

import (
	"context"
	"fmt"
	"os"
	openapiclient "github.com/amesh/amesh-client-go"
)

func main() {
	namespace := "namespace_example" // string |  (optional)
	applicationId := "applicationId_example" // string |  (optional)
	limit := int32(56) // int32 |  (optional) (default to 100)
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.AgentSessionAdministrationAPI.ListAgentSessionPoliciesApiV1AdminAgentSessionPoliciesGet(context.Background()).Namespace(namespace).ApplicationId(applicationId).Limit(limit).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `AgentSessionAdministrationAPI.ListAgentSessionPoliciesApiV1AdminAgentSessionPoliciesGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `ListAgentSessionPoliciesApiV1AdminAgentSessionPoliciesGet`: []AgentSessionPolicyRevision
	fmt.Fprintf(os.Stdout, "Response from `AgentSessionAdministrationAPI.ListAgentSessionPoliciesApiV1AdminAgentSessionPoliciesGet`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiListAgentSessionPoliciesApiV1AdminAgentSessionPoliciesGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **namespace** | **string** |  |
 **applicationId** | **string** |  |
 **limit** | **int32** |  | [default to 100]
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**[]AgentSessionPolicyRevision**](AgentSessionPolicyRevision.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## PutAgentSessionPolicyApiV1AdminAgentSessionPoliciesPut

> AgentSessionPolicyRevision PutAgentSessionPolicyApiV1AdminAgentSessionPoliciesPut(ctx).AgentSessionPolicyUpsertRequest(agentSessionPolicyUpsertRequest).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Put Agent Session Policy

### Example

```go
package main

import (
	"context"
	"fmt"
	"os"
	openapiclient "github.com/amesh/amesh-client-go"
)

func main() {
	agentSessionPolicyUpsertRequest := *openapiclient.NewAgentSessionPolicyUpsertRequest(int32(123), *openapiclient.NewMaxcostusd(), int32(123), int32(123), int32(123)) // AgentSessionPolicyUpsertRequest |
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.AgentSessionAdministrationAPI.PutAgentSessionPolicyApiV1AdminAgentSessionPoliciesPut(context.Background()).AgentSessionPolicyUpsertRequest(agentSessionPolicyUpsertRequest).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `AgentSessionAdministrationAPI.PutAgentSessionPolicyApiV1AdminAgentSessionPoliciesPut``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `PutAgentSessionPolicyApiV1AdminAgentSessionPoliciesPut`: AgentSessionPolicyRevision
	fmt.Fprintf(os.Stdout, "Response from `AgentSessionAdministrationAPI.PutAgentSessionPolicyApiV1AdminAgentSessionPoliciesPut`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiPutAgentSessionPolicyApiV1AdminAgentSessionPoliciesPutRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **agentSessionPolicyUpsertRequest** | **AgentSessionPolicyUpsertRequest** |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

**AgentSessionPolicyRevision**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)
