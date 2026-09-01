# \AgentSessionTransfersAPI

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**ExportAgentProfileTransferApiV1AdminAgentSessionTransfersProfilesNamespaceAgentKeyExportGet**](AgentSessionTransfersAPI.md#ExportAgentProfileTransferApiV1AdminAgentSessionTransfersProfilesNamespaceAgentKeyExportGet) | **Get** /api/v1/admin/agent-session-transfers/profiles/{namespace}/{agent_key}/export | Export Agent Profile Transfer
[**ExportAgentProfileTransferApiV1AdminAgentSessionTransfersProfilesNamespaceAgentKeyExportPost**](AgentSessionTransfersAPI.md#ExportAgentProfileTransferApiV1AdminAgentSessionTransfersProfilesNamespaceAgentKeyExportPost) | **Post** /api/v1/admin/agent-session-transfers/profiles/{namespace}/{agent_key}/export | Export Agent Profile Transfer
[**ExportAgentSessionTransferApiV1AdminAgentSessionTransfersSessionsSessionIdExportPost**](AgentSessionTransfersAPI.md#ExportAgentSessionTransferApiV1AdminAgentSessionTransfersSessionsSessionIdExportPost) | **Post** /api/v1/admin/agent-session-transfers/sessions/{session_id}/export | Export Agent Session Transfer
[**ImportAgentProfileTransferApiV1AdminAgentSessionTransfersProfilesImportPost**](AgentSessionTransfersAPI.md#ImportAgentProfileTransferApiV1AdminAgentSessionTransfersProfilesImportPost) | **Post** /api/v1/admin/agent-session-transfers/profiles/import | Import Agent Profile Transfer
[**ImportAgentSessionTransferApiV1AdminAgentSessionTransfersSessionsImportPost**](AgentSessionTransfersAPI.md#ImportAgentSessionTransferApiV1AdminAgentSessionTransfersSessionsImportPost) | **Post** /api/v1/admin/agent-session-transfers/sessions/import | Import Agent Session Transfer
[**PlanAgentProfileTransferApiV1AdminAgentSessionTransfersProfilesPlanPost**](AgentSessionTransfersAPI.md#PlanAgentProfileTransferApiV1AdminAgentSessionTransfersProfilesPlanPost) | **Post** /api/v1/admin/agent-session-transfers/profiles/plan | Plan Agent Profile Transfer
[**PlanAgentSessionTransferApiV1AdminAgentSessionTransfersSessionsPlanPost**](AgentSessionTransfersAPI.md#PlanAgentSessionTransferApiV1AdminAgentSessionTransfersSessionsPlanPost) | **Post** /api/v1/admin/agent-session-transfers/sessions/plan | Plan Agent Session Transfer



## ExportAgentProfileTransferApiV1AdminAgentSessionTransfersProfilesNamespaceAgentKeyExportGet

> ProfileBundleOutput ExportAgentProfileTransferApiV1AdminAgentSessionTransfersProfilesNamespaceAgentKeyExportGet(ctx, namespace, agentKey).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Export Agent Profile Transfer

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
	agentKey := "agentKey_example" // string |
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.AgentSessionTransfersAPI.ExportAgentProfileTransferApiV1AdminAgentSessionTransfersProfilesNamespaceAgentKeyExportGet(context.Background(), namespace, agentKey).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `AgentSessionTransfersAPI.ExportAgentProfileTransferApiV1AdminAgentSessionTransfersProfilesNamespaceAgentKeyExportGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `ExportAgentProfileTransferApiV1AdminAgentSessionTransfersProfilesNamespaceAgentKeyExportGet`: ProfileBundleOutput
	fmt.Fprintf(os.Stdout, "Response from `AgentSessionTransfersAPI.ExportAgentProfileTransferApiV1AdminAgentSessionTransfersProfilesNamespaceAgentKeyExportGet`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**namespace** | **string** |  |
**agentKey** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiExportAgentProfileTransferApiV1AdminAgentSessionTransfersProfilesNamespaceAgentKeyExportGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------


 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

**ProfileBundleOutput**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## ExportAgentProfileTransferApiV1AdminAgentSessionTransfersProfilesNamespaceAgentKeyExportPost

> ProfileBundleOutput ExportAgentProfileTransferApiV1AdminAgentSessionTransfersProfilesNamespaceAgentKeyExportPost(ctx, namespace, agentKey).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Export Agent Profile Transfer

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
	agentKey := "agentKey_example" // string |
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.AgentSessionTransfersAPI.ExportAgentProfileTransferApiV1AdminAgentSessionTransfersProfilesNamespaceAgentKeyExportPost(context.Background(), namespace, agentKey).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `AgentSessionTransfersAPI.ExportAgentProfileTransferApiV1AdminAgentSessionTransfersProfilesNamespaceAgentKeyExportPost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `ExportAgentProfileTransferApiV1AdminAgentSessionTransfersProfilesNamespaceAgentKeyExportPost`: ProfileBundleOutput
	fmt.Fprintf(os.Stdout, "Response from `AgentSessionTransfersAPI.ExportAgentProfileTransferApiV1AdminAgentSessionTransfersProfilesNamespaceAgentKeyExportPost`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**namespace** | **string** |  |
**agentKey** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiExportAgentProfileTransferApiV1AdminAgentSessionTransfersProfilesNamespaceAgentKeyExportPostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------


 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

**ProfileBundleOutput**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## ExportAgentSessionTransferApiV1AdminAgentSessionTransfersSessionsSessionIdExportPost

> SessionTransferBundleOutput ExportAgentSessionTransferApiV1AdminAgentSessionTransfersSessionsSessionIdExportPost(ctx, sessionId).AgentSessionTransferSessionExportRequest(agentSessionTransferSessionExportRequest).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Export Agent Session Transfer

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
	sessionId := "38400000-8cf0-11bd-b23e-10b96e4ef00d" // string |
	agentSessionTransferSessionExportRequest := *openapiclient.NewAgentSessionTransferSessionExportRequest(openapiclient.SessionTransferMode("TERMINAL_HISTORY")) // AgentSessionTransferSessionExportRequest |
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.AgentSessionTransfersAPI.ExportAgentSessionTransferApiV1AdminAgentSessionTransfersSessionsSessionIdExportPost(context.Background(), sessionId).AgentSessionTransferSessionExportRequest(agentSessionTransferSessionExportRequest).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `AgentSessionTransfersAPI.ExportAgentSessionTransferApiV1AdminAgentSessionTransfersSessionsSessionIdExportPost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `ExportAgentSessionTransferApiV1AdminAgentSessionTransfersSessionsSessionIdExportPost`: SessionTransferBundleOutput
	fmt.Fprintf(os.Stdout, "Response from `AgentSessionTransfersAPI.ExportAgentSessionTransferApiV1AdminAgentSessionTransfersSessionsSessionIdExportPost`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**sessionId** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiExportAgentSessionTransferApiV1AdminAgentSessionTransfersSessionsSessionIdExportPostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------

 **agentSessionTransferSessionExportRequest** | **AgentSessionTransferSessionExportRequest** |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

**SessionTransferBundleOutput**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## ImportAgentProfileTransferApiV1AdminAgentSessionTransfersProfilesImportPost

> ProfileImportResult ImportAgentProfileTransferApiV1AdminAgentSessionTransfersProfilesImportPost(ctx).AgentSessionTransferProfileImportRequest(agentSessionTransferProfileImportRequest).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Import Agent Profile Transfer

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
	agentSessionTransferProfileImportRequest := *openapiclient.NewAgentSessionTransferProfileImportRequest(*openapiclient.NewProfileBundleInput("AgentKey_example", int32(123), "ChecksumSha256_example", "Namespace_example", "SourceTenantId_example")) // AgentSessionTransferProfileImportRequest |
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.AgentSessionTransfersAPI.ImportAgentProfileTransferApiV1AdminAgentSessionTransfersProfilesImportPost(context.Background()).AgentSessionTransferProfileImportRequest(agentSessionTransferProfileImportRequest).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `AgentSessionTransfersAPI.ImportAgentProfileTransferApiV1AdminAgentSessionTransfersProfilesImportPost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `ImportAgentProfileTransferApiV1AdminAgentSessionTransfersProfilesImportPost`: ProfileImportResult
	fmt.Fprintf(os.Stdout, "Response from `AgentSessionTransfersAPI.ImportAgentProfileTransferApiV1AdminAgentSessionTransfersProfilesImportPost`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiImportAgentProfileTransferApiV1AdminAgentSessionTransfersProfilesImportPostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **agentSessionTransferProfileImportRequest** | **AgentSessionTransferProfileImportRequest** |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

**ProfileImportResult**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## ImportAgentSessionTransferApiV1AdminAgentSessionTransfersSessionsImportPost

> SessionTransferImportResult ImportAgentSessionTransferApiV1AdminAgentSessionTransfersSessionsImportPost(ctx).AgentSessionTransferSessionImportRequest(agentSessionTransferSessionImportRequest).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Import Agent Session Transfer

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
	agentSessionTransferSessionImportRequest := *openapiclient.NewAgentSessionTransferSessionImportRequest(*openapiclient.NewSessionTransferBundleInput("ChecksumSha256_example", *openapiclient.NewPersistedExecution(time.Now(), int32(123), "ExecutionId_example", "FlowId_example", "Namespace_example", openapiclient.ExecutionState("CREATED"), "TenantId_example", time.Now(), int32(123)), openapiclient.SessionTransferMode("TERMINAL_HISTORY"), *openapiclient.NewAgentSessionRecordInput(int32(123), "CapabilityPinId_example", "EnvelopeDigest_example", "ExecutionId_example", "Namespace_example", "TaskRunId_example", "TenantId_example"), "SourceTenantId_example")) // AgentSessionTransferSessionImportRequest |
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.AgentSessionTransfersAPI.ImportAgentSessionTransferApiV1AdminAgentSessionTransfersSessionsImportPost(context.Background()).AgentSessionTransferSessionImportRequest(agentSessionTransferSessionImportRequest).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `AgentSessionTransfersAPI.ImportAgentSessionTransferApiV1AdminAgentSessionTransfersSessionsImportPost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `ImportAgentSessionTransferApiV1AdminAgentSessionTransfersSessionsImportPost`: SessionTransferImportResult
	fmt.Fprintf(os.Stdout, "Response from `AgentSessionTransfersAPI.ImportAgentSessionTransferApiV1AdminAgentSessionTransfersSessionsImportPost`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiImportAgentSessionTransferApiV1AdminAgentSessionTransfersSessionsImportPostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **agentSessionTransferSessionImportRequest** | **AgentSessionTransferSessionImportRequest** |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

**SessionTransferImportResult**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## PlanAgentProfileTransferApiV1AdminAgentSessionTransfersProfilesPlanPost

> ProfileCompatibilityReport PlanAgentProfileTransferApiV1AdminAgentSessionTransfersProfilesPlanPost(ctx).AgentSessionTransferProfilePlanRequest(agentSessionTransferProfilePlanRequest).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Plan Agent Profile Transfer

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
	agentSessionTransferProfilePlanRequest := *openapiclient.NewAgentSessionTransferProfilePlanRequest(*openapiclient.NewProfileBundleInput("AgentKey_example", int32(123), "ChecksumSha256_example", "Namespace_example", "SourceTenantId_example")) // AgentSessionTransferProfilePlanRequest |
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.AgentSessionTransfersAPI.PlanAgentProfileTransferApiV1AdminAgentSessionTransfersProfilesPlanPost(context.Background()).AgentSessionTransferProfilePlanRequest(agentSessionTransferProfilePlanRequest).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `AgentSessionTransfersAPI.PlanAgentProfileTransferApiV1AdminAgentSessionTransfersProfilesPlanPost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `PlanAgentProfileTransferApiV1AdminAgentSessionTransfersProfilesPlanPost`: ProfileCompatibilityReport
	fmt.Fprintf(os.Stdout, "Response from `AgentSessionTransfersAPI.PlanAgentProfileTransferApiV1AdminAgentSessionTransfersProfilesPlanPost`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiPlanAgentProfileTransferApiV1AdminAgentSessionTransfersProfilesPlanPostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **agentSessionTransferProfilePlanRequest** | **AgentSessionTransferProfilePlanRequest** |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

**ProfileCompatibilityReport**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## PlanAgentSessionTransferApiV1AdminAgentSessionTransfersSessionsPlanPost

> SessionTransferCompatibilityReport PlanAgentSessionTransferApiV1AdminAgentSessionTransfersSessionsPlanPost(ctx).AgentSessionTransferSessionPlanRequest(agentSessionTransferSessionPlanRequest).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Plan Agent Session Transfer

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
	agentSessionTransferSessionPlanRequest := *openapiclient.NewAgentSessionTransferSessionPlanRequest(*openapiclient.NewSessionTransferBundleInput("ChecksumSha256_example", *openapiclient.NewPersistedExecution(time.Now(), int32(123), "ExecutionId_example", "FlowId_example", "Namespace_example", openapiclient.ExecutionState("CREATED"), "TenantId_example", time.Now(), int32(123)), openapiclient.SessionTransferMode("TERMINAL_HISTORY"), *openapiclient.NewAgentSessionRecordInput(int32(123), "CapabilityPinId_example", "EnvelopeDigest_example", "ExecutionId_example", "Namespace_example", "TaskRunId_example", "TenantId_example"), "SourceTenantId_example")) // AgentSessionTransferSessionPlanRequest |
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.AgentSessionTransfersAPI.PlanAgentSessionTransferApiV1AdminAgentSessionTransfersSessionsPlanPost(context.Background()).AgentSessionTransferSessionPlanRequest(agentSessionTransferSessionPlanRequest).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `AgentSessionTransfersAPI.PlanAgentSessionTransferApiV1AdminAgentSessionTransfersSessionsPlanPost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `PlanAgentSessionTransferApiV1AdminAgentSessionTransfersSessionsPlanPost`: SessionTransferCompatibilityReport
	fmt.Fprintf(os.Stdout, "Response from `AgentSessionTransfersAPI.PlanAgentSessionTransferApiV1AdminAgentSessionTransfersSessionsPlanPost`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiPlanAgentSessionTransferApiV1AdminAgentSessionTransfersSessionsPlanPostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **agentSessionTransferSessionPlanRequest** | **AgentSessionTransferSessionPlanRequest** |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

**SessionTransferCompatibilityReport**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)
