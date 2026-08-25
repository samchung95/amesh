# \ExecutionsAPI

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**ApplyExecutionControlApiV1ExecutionsExecutionIdInterventionsPost**](ExecutionsAPI.md#ApplyExecutionControlApiV1ExecutionsExecutionIdInterventionsPost) | **Post** /api/v1/executions/{execution_id}/interventions | Apply Execution Control
[**CreateExecutionApiV1ExecutionsPost**](ExecutionsAPI.md#CreateExecutionApiV1ExecutionsPost) | **Post** /api/v1/executions | Create Execution
[**CreateExecutionsBulkApiV1ExecutionsBulkPost**](ExecutionsAPI.md#CreateExecutionsBulkApiV1ExecutionsBulkPost) | **Post** /api/v1/executions/bulk | Create Executions Bulk
[**DownloadExecutionFileApiV1ExecutionsExecutionIdFilesArtifactIdGet**](ExecutionsAPI.md#DownloadExecutionFileApiV1ExecutionsExecutionIdFilesArtifactIdGet) | **Get** /api/v1/executions/{execution_id}/files/{artifact_id} | Download Execution File
[**GetExecutionAdmissionApiV1ExecutionsExecutionIdAdmissionGet**](ExecutionsAPI.md#GetExecutionAdmissionApiV1ExecutionsExecutionIdAdmissionGet) | **Get** /api/v1/executions/{execution_id}/admission | Get Execution Admission
[**GetExecutionApiV1ExecutionsExecutionIdGet**](ExecutionsAPI.md#GetExecutionApiV1ExecutionsExecutionIdGet) | **Get** /api/v1/executions/{execution_id} | Get Execution
[**GetExecutionEvidenceApiV1ExecutionsExecutionIdEvidenceGet**](ExecutionsAPI.md#GetExecutionEvidenceApiV1ExecutionsExecutionIdEvidenceGet) | **Get** /api/v1/executions/{execution_id}/evidence | Get Execution Evidence
[**GetExecutionGraphApiV1ExecutionsExecutionIdGraphGet**](ExecutionsAPI.md#GetExecutionGraphApiV1ExecutionsExecutionIdGraphGet) | **Get** /api/v1/executions/{execution_id}/graph | Get Execution Graph
[**GetExecutionLogsApiV1ExecutionsExecutionIdLogsGet**](ExecutionsAPI.md#GetExecutionLogsApiV1ExecutionsExecutionIdLogsGet) | **Get** /api/v1/executions/{execution_id}/logs | Get Execution Logs
[**GetExecutionParentSubflowApiV1ExecutionsExecutionIdParentSubflowGet**](ExecutionsAPI.md#GetExecutionParentSubflowApiV1ExecutionsExecutionIdParentSubflowGet) | **Get** /api/v1/executions/{execution_id}/parent-subflow | Get Execution Parent Subflow
[**GetTaskAdmissionApiV1TaskRunsTaskRunIdAdmissionGet**](ExecutionsAPI.md#GetTaskAdmissionApiV1TaskRunsTaskRunIdAdmissionGet) | **Get** /api/v1/task-runs/{task_run_id}/admission | Get Task Admission
[**ListExecutionAgentSessionsApiV1ExecutionsExecutionIdAgentSessionsGet**](ExecutionsAPI.md#ListExecutionAgentSessionsApiV1ExecutionsExecutionIdAgentSessionsGet) | **Get** /api/v1/executions/{execution_id}/agent-sessions | List Execution Agent Sessions
[**ListExecutionControlHistoryApiV1ExecutionsExecutionIdInterventionsGet**](ExecutionsAPI.md#ListExecutionControlHistoryApiV1ExecutionsExecutionIdInterventionsGet) | **Get** /api/v1/executions/{execution_id}/interventions | List Execution Control History
[**ListExecutionFilesApiV1ExecutionsExecutionIdFilesGet**](ExecutionsAPI.md#ListExecutionFilesApiV1ExecutionsExecutionIdFilesGet) | **Get** /api/v1/executions/{execution_id}/files | List Execution Files
[**ListExecutionSubflowsApiV1ExecutionsExecutionIdSubflowsGet**](ExecutionsAPI.md#ListExecutionSubflowsApiV1ExecutionsExecutionIdSubflowsGet) | **Get** /api/v1/executions/{execution_id}/subflows | List Execution Subflows
[**ListExecutionsApiV1ExecutionsGet**](ExecutionsAPI.md#ListExecutionsApiV1ExecutionsGet) | **Get** /api/v1/executions | List Executions
[**PreviewExecutionControlApiV1ExecutionsExecutionIdInterventionsPreviewPost**](ExecutionsAPI.md#PreviewExecutionControlApiV1ExecutionsExecutionIdInterventionsPreviewPost) | **Post** /api/v1/executions/{execution_id}/interventions/preview | Preview Execution Control
[**ReduceExecutionEventsApiV1ExecutionsReducePost**](ExecutionsAPI.md#ReduceExecutionEventsApiV1ExecutionsReducePost) | **Post** /api/v1/executions/reduce | Reduce Execution Events
[**ResumeTaskRunApiV1ExecutionsExecutionIdTaskRunsTaskRunIdResumePost**](ExecutionsAPI.md#ResumeTaskRunApiV1ExecutionsExecutionIdTaskRunsTaskRunIdResumePost) | **Post** /api/v1/executions/{execution_id}/task-runs/{task_run_id}/resume | Resume Task Run
[**StreamExecutionEvidenceApiV1ExecutionsExecutionIdEvidenceStreamGet**](ExecutionsAPI.md#StreamExecutionEvidenceApiV1ExecutionsExecutionIdEvidenceStreamGet) | **Get** /api/v1/executions/{execution_id}/evidence/stream | Stream Execution Evidence
[**StreamExecutionLogsApiV1ExecutionsExecutionIdLogsStreamGet**](ExecutionsAPI.md#StreamExecutionLogsApiV1ExecutionsExecutionIdLogsStreamGet) | **Get** /api/v1/executions/{execution_id}/logs/stream | Stream Execution Logs



## ApplyExecutionControlApiV1ExecutionsExecutionIdInterventionsPost

> ExecutionDetail ApplyExecutionControlApiV1ExecutionsExecutionIdInterventionsPost(ctx, executionId).ExecutionInterventionRequest(executionInterventionRequest).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Apply Execution Control

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
	executionId := "38400000-8cf0-11bd-b23e-10b96e4ef00d" // string |
	executionInterventionRequest := *openapiclient.NewExecutionInterventionRequest(openapiclient.ExecutionInterventionAction("PAUSE"), int32(123), int32(123), "Reason_example") // ExecutionInterventionRequest |
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.ExecutionsAPI.ApplyExecutionControlApiV1ExecutionsExecutionIdInterventionsPost(context.Background(), executionId).ExecutionInterventionRequest(executionInterventionRequest).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `ExecutionsAPI.ApplyExecutionControlApiV1ExecutionsExecutionIdInterventionsPost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `ApplyExecutionControlApiV1ExecutionsExecutionIdInterventionsPost`: ExecutionDetail
	fmt.Fprintf(os.Stdout, "Response from `ExecutionsAPI.ApplyExecutionControlApiV1ExecutionsExecutionIdInterventionsPost`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**executionId** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiApplyExecutionControlApiV1ExecutionsExecutionIdInterventionsPostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------

 **executionInterventionRequest** | [**ExecutionInterventionRequest**](ExecutionInterventionRequest.md) |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**ExecutionDetail**](ExecutionDetail.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## CreateExecutionApiV1ExecutionsPost

> ExecutionDetail CreateExecutionApiV1ExecutionsPost(ctx).CreateExecutionRequest(createExecutionRequest).Prefer(prefer).IdempotencyKey(idempotencyKey).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Create Execution

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
	createExecutionRequest := *openapiclient.NewCreateExecutionRequest("FlowId_example", "Namespace_example") // CreateExecutionRequest |
	prefer := "prefer_example" // string |  (optional)
	idempotencyKey := "idempotencyKey_example" // string |  (optional)
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.ExecutionsAPI.CreateExecutionApiV1ExecutionsPost(context.Background()).CreateExecutionRequest(createExecutionRequest).Prefer(prefer).IdempotencyKey(idempotencyKey).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `ExecutionsAPI.CreateExecutionApiV1ExecutionsPost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `CreateExecutionApiV1ExecutionsPost`: ExecutionDetail
	fmt.Fprintf(os.Stdout, "Response from `ExecutionsAPI.CreateExecutionApiV1ExecutionsPost`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiCreateExecutionApiV1ExecutionsPostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **createExecutionRequest** | [**CreateExecutionRequest**](CreateExecutionRequest.md) |  |
 **prefer** | **string** |  |
 **idempotencyKey** | **string** |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**ExecutionDetail**](ExecutionDetail.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## CreateExecutionsBulkApiV1ExecutionsBulkPost

> []BulkExecutionItemResult CreateExecutionsBulkApiV1ExecutionsBulkPost(ctx).BulkExecutionRequest(bulkExecutionRequest).Prefer(prefer).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Create Executions Bulk

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
	bulkExecutionRequest := *openapiclient.NewBulkExecutionRequest([]openapiclient.CreateExecutionRequest{*openapiclient.NewCreateExecutionRequest("FlowId_example", "Namespace_example")}) // BulkExecutionRequest |
	prefer := "prefer_example" // string |  (optional)
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.ExecutionsAPI.CreateExecutionsBulkApiV1ExecutionsBulkPost(context.Background()).BulkExecutionRequest(bulkExecutionRequest).Prefer(prefer).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `ExecutionsAPI.CreateExecutionsBulkApiV1ExecutionsBulkPost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `CreateExecutionsBulkApiV1ExecutionsBulkPost`: []BulkExecutionItemResult
	fmt.Fprintf(os.Stdout, "Response from `ExecutionsAPI.CreateExecutionsBulkApiV1ExecutionsBulkPost`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiCreateExecutionsBulkApiV1ExecutionsBulkPostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **bulkExecutionRequest** | [**BulkExecutionRequest**](BulkExecutionRequest.md) |  |
 **prefer** | **string** |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**[]BulkExecutionItemResult**](BulkExecutionItemResult.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## DownloadExecutionFileApiV1ExecutionsExecutionIdFilesArtifactIdGet

> DownloadExecutionFileApiV1ExecutionsExecutionIdFilesArtifactIdGet(ctx, executionId, artifactId).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Download Execution File

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
	executionId := "38400000-8cf0-11bd-b23e-10b96e4ef00d" // string |
	artifactId := "38400000-8cf0-11bd-b23e-10b96e4ef00d" // string |
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	r, err := apiClient.ExecutionsAPI.DownloadExecutionFileApiV1ExecutionsExecutionIdFilesArtifactIdGet(context.Background(), executionId, artifactId).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `ExecutionsAPI.DownloadExecutionFileApiV1ExecutionsExecutionIdFilesArtifactIdGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**executionId** | **string** |  |
**artifactId** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiDownloadExecutionFileApiV1ExecutionsExecutionIdFilesArtifactIdGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------


 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

 (empty response body)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## GetExecutionAdmissionApiV1ExecutionsExecutionIdAdmissionGet

> AdmissionDecision GetExecutionAdmissionApiV1ExecutionsExecutionIdAdmissionGet(ctx, executionId).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Get Execution Admission

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
	executionId := "38400000-8cf0-11bd-b23e-10b96e4ef00d" // string |
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.ExecutionsAPI.GetExecutionAdmissionApiV1ExecutionsExecutionIdAdmissionGet(context.Background(), executionId).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `ExecutionsAPI.GetExecutionAdmissionApiV1ExecutionsExecutionIdAdmissionGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `GetExecutionAdmissionApiV1ExecutionsExecutionIdAdmissionGet`: AdmissionDecision
	fmt.Fprintf(os.Stdout, "Response from `ExecutionsAPI.GetExecutionAdmissionApiV1ExecutionsExecutionIdAdmissionGet`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**executionId** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiGetExecutionAdmissionApiV1ExecutionsExecutionIdAdmissionGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------

 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**AdmissionDecision**](AdmissionDecision.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## GetExecutionApiV1ExecutionsExecutionIdGet

> ExecutionDetail GetExecutionApiV1ExecutionsExecutionIdGet(ctx, executionId).TaskOffset(taskOffset).TaskLimit(taskLimit).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Get Execution

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
	executionId := "38400000-8cf0-11bd-b23e-10b96e4ef00d" // string |
	taskOffset := int32(56) // int32 |  (optional) (default to 0)
	taskLimit := int32(56) // int32 |  (optional)
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.ExecutionsAPI.GetExecutionApiV1ExecutionsExecutionIdGet(context.Background(), executionId).TaskOffset(taskOffset).TaskLimit(taskLimit).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `ExecutionsAPI.GetExecutionApiV1ExecutionsExecutionIdGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `GetExecutionApiV1ExecutionsExecutionIdGet`: ExecutionDetail
	fmt.Fprintf(os.Stdout, "Response from `ExecutionsAPI.GetExecutionApiV1ExecutionsExecutionIdGet`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**executionId** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiGetExecutionApiV1ExecutionsExecutionIdGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------

 **taskOffset** | **int32** |  | [default to 0]
 **taskLimit** | **int32** |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**ExecutionDetail**](ExecutionDetail.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## GetExecutionEvidenceApiV1ExecutionsExecutionIdEvidenceGet

> ExecutionEvidencePage GetExecutionEvidenceApiV1ExecutionsExecutionIdEvidenceGet(ctx, executionId).Cursor(cursor).Limit(limit).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Get Execution Evidence

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
	executionId := "38400000-8cf0-11bd-b23e-10b96e4ef00d" // string |
	cursor := "cursor_example" // string | Opaque reconnect cursor (optional)
	limit := int32(56) // int32 |  (optional) (default to 500)
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.ExecutionsAPI.GetExecutionEvidenceApiV1ExecutionsExecutionIdEvidenceGet(context.Background(), executionId).Cursor(cursor).Limit(limit).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `ExecutionsAPI.GetExecutionEvidenceApiV1ExecutionsExecutionIdEvidenceGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `GetExecutionEvidenceApiV1ExecutionsExecutionIdEvidenceGet`: ExecutionEvidencePage
	fmt.Fprintf(os.Stdout, "Response from `ExecutionsAPI.GetExecutionEvidenceApiV1ExecutionsExecutionIdEvidenceGet`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**executionId** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiGetExecutionEvidenceApiV1ExecutionsExecutionIdEvidenceGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------

 **cursor** | **string** | Opaque reconnect cursor |
 **limit** | **int32** |  | [default to 500]
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**ExecutionEvidencePage**](ExecutionEvidencePage.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## GetExecutionGraphApiV1ExecutionsExecutionIdGraphGet

> FlowGraph GetExecutionGraphApiV1ExecutionsExecutionIdGraphGet(ctx, executionId).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Get Execution Graph

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
	executionId := "38400000-8cf0-11bd-b23e-10b96e4ef00d" // string |
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.ExecutionsAPI.GetExecutionGraphApiV1ExecutionsExecutionIdGraphGet(context.Background(), executionId).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `ExecutionsAPI.GetExecutionGraphApiV1ExecutionsExecutionIdGraphGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `GetExecutionGraphApiV1ExecutionsExecutionIdGraphGet`: FlowGraph
	fmt.Fprintf(os.Stdout, "Response from `ExecutionsAPI.GetExecutionGraphApiV1ExecutionsExecutionIdGraphGet`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**executionId** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiGetExecutionGraphApiV1ExecutionsExecutionIdGraphGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------

 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**FlowGraph**](FlowGraph.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## GetExecutionLogsApiV1ExecutionsExecutionIdLogsGet

> []TaskLog GetExecutionLogsApiV1ExecutionsExecutionIdLogsGet(ctx, executionId).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Get Execution Logs

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
	executionId := "38400000-8cf0-11bd-b23e-10b96e4ef00d" // string |
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.ExecutionsAPI.GetExecutionLogsApiV1ExecutionsExecutionIdLogsGet(context.Background(), executionId).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `ExecutionsAPI.GetExecutionLogsApiV1ExecutionsExecutionIdLogsGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `GetExecutionLogsApiV1ExecutionsExecutionIdLogsGet`: []TaskLog
	fmt.Fprintf(os.Stdout, "Response from `ExecutionsAPI.GetExecutionLogsApiV1ExecutionsExecutionIdLogsGet`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**executionId** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiGetExecutionLogsApiV1ExecutionsExecutionIdLogsGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------

 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**[]TaskLog**](TaskLog.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## GetExecutionParentSubflowApiV1ExecutionsExecutionIdParentSubflowGet

> PersistedSubflow GetExecutionParentSubflowApiV1ExecutionsExecutionIdParentSubflowGet(ctx, executionId).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Get Execution Parent Subflow

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
	executionId := "38400000-8cf0-11bd-b23e-10b96e4ef00d" // string |
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.ExecutionsAPI.GetExecutionParentSubflowApiV1ExecutionsExecutionIdParentSubflowGet(context.Background(), executionId).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `ExecutionsAPI.GetExecutionParentSubflowApiV1ExecutionsExecutionIdParentSubflowGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `GetExecutionParentSubflowApiV1ExecutionsExecutionIdParentSubflowGet`: PersistedSubflow
	fmt.Fprintf(os.Stdout, "Response from `ExecutionsAPI.GetExecutionParentSubflowApiV1ExecutionsExecutionIdParentSubflowGet`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**executionId** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiGetExecutionParentSubflowApiV1ExecutionsExecutionIdParentSubflowGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------

 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**PersistedSubflow**](PersistedSubflow.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## GetTaskAdmissionApiV1TaskRunsTaskRunIdAdmissionGet

> AdmissionDecision GetTaskAdmissionApiV1TaskRunsTaskRunIdAdmissionGet(ctx, taskRunId).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Get Task Admission

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
	taskRunId := "38400000-8cf0-11bd-b23e-10b96e4ef00d" // string |
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.ExecutionsAPI.GetTaskAdmissionApiV1TaskRunsTaskRunIdAdmissionGet(context.Background(), taskRunId).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `ExecutionsAPI.GetTaskAdmissionApiV1TaskRunsTaskRunIdAdmissionGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `GetTaskAdmissionApiV1TaskRunsTaskRunIdAdmissionGet`: AdmissionDecision
	fmt.Fprintf(os.Stdout, "Response from `ExecutionsAPI.GetTaskAdmissionApiV1TaskRunsTaskRunIdAdmissionGet`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**taskRunId** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiGetTaskAdmissionApiV1TaskRunsTaskRunIdAdmissionGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------

 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**AdmissionDecision**](AdmissionDecision.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## ListExecutionAgentSessionsApiV1ExecutionsExecutionIdAgentSessionsGet

> []AgentSessionRecord ListExecutionAgentSessionsApiV1ExecutionsExecutionIdAgentSessionsGet(ctx, executionId).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

List Execution Agent Sessions

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
	executionId := "38400000-8cf0-11bd-b23e-10b96e4ef00d" // string |
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.ExecutionsAPI.ListExecutionAgentSessionsApiV1ExecutionsExecutionIdAgentSessionsGet(context.Background(), executionId).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `ExecutionsAPI.ListExecutionAgentSessionsApiV1ExecutionsExecutionIdAgentSessionsGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `ListExecutionAgentSessionsApiV1ExecutionsExecutionIdAgentSessionsGet`: []AgentSessionRecord
	fmt.Fprintf(os.Stdout, "Response from `ExecutionsAPI.ListExecutionAgentSessionsApiV1ExecutionsExecutionIdAgentSessionsGet`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**executionId** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiListExecutionAgentSessionsApiV1ExecutionsExecutionIdAgentSessionsGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------

 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**[]AgentSessionRecord**](AgentSessionRecord.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## ListExecutionControlHistoryApiV1ExecutionsExecutionIdInterventionsGet

> []ExecutionInterventionRecord ListExecutionControlHistoryApiV1ExecutionsExecutionIdInterventionsGet(ctx, executionId).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

List Execution Control History

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
	executionId := "38400000-8cf0-11bd-b23e-10b96e4ef00d" // string |
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.ExecutionsAPI.ListExecutionControlHistoryApiV1ExecutionsExecutionIdInterventionsGet(context.Background(), executionId).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `ExecutionsAPI.ListExecutionControlHistoryApiV1ExecutionsExecutionIdInterventionsGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `ListExecutionControlHistoryApiV1ExecutionsExecutionIdInterventionsGet`: []ExecutionInterventionRecord
	fmt.Fprintf(os.Stdout, "Response from `ExecutionsAPI.ListExecutionControlHistoryApiV1ExecutionsExecutionIdInterventionsGet`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**executionId** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiListExecutionControlHistoryApiV1ExecutionsExecutionIdInterventionsGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------

 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**[]ExecutionInterventionRecord**](ExecutionInterventionRecord.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## ListExecutionFilesApiV1ExecutionsExecutionIdFilesGet

> []ExecutionArtifact ListExecutionFilesApiV1ExecutionsExecutionIdFilesGet(ctx, executionId).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

List Execution Files

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
	executionId := "38400000-8cf0-11bd-b23e-10b96e4ef00d" // string |
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.ExecutionsAPI.ListExecutionFilesApiV1ExecutionsExecutionIdFilesGet(context.Background(), executionId).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `ExecutionsAPI.ListExecutionFilesApiV1ExecutionsExecutionIdFilesGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `ListExecutionFilesApiV1ExecutionsExecutionIdFilesGet`: []ExecutionArtifact
	fmt.Fprintf(os.Stdout, "Response from `ExecutionsAPI.ListExecutionFilesApiV1ExecutionsExecutionIdFilesGet`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**executionId** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiListExecutionFilesApiV1ExecutionsExecutionIdFilesGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------

 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**[]ExecutionArtifact**](ExecutionArtifact.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## ListExecutionSubflowsApiV1ExecutionsExecutionIdSubflowsGet

> []PersistedSubflow ListExecutionSubflowsApiV1ExecutionsExecutionIdSubflowsGet(ctx, executionId).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

List Execution Subflows

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
	executionId := "38400000-8cf0-11bd-b23e-10b96e4ef00d" // string |
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.ExecutionsAPI.ListExecutionSubflowsApiV1ExecutionsExecutionIdSubflowsGet(context.Background(), executionId).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `ExecutionsAPI.ListExecutionSubflowsApiV1ExecutionsExecutionIdSubflowsGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `ListExecutionSubflowsApiV1ExecutionsExecutionIdSubflowsGet`: []PersistedSubflow
	fmt.Fprintf(os.Stdout, "Response from `ExecutionsAPI.ListExecutionSubflowsApiV1ExecutionsExecutionIdSubflowsGet`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**executionId** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiListExecutionSubflowsApiV1ExecutionsExecutionIdSubflowsGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------

 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**[]PersistedSubflow**](PersistedSubflow.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## ListExecutionsApiV1ExecutionsGet

> []PersistedExecution ListExecutionsApiV1ExecutionsGet(ctx).Cursor(cursor).Limit(limit).Filter(filter).Sort(sort).Fields(fields).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

List Executions

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
	cursor := "cursor_example" // string | Opaque cursor from the prior page (optional)
	limit := int32(56) // int32 |  (optional) (default to 100)
	filter := []string{"Inner_example"} // []string | Repeatable top-level equality filter in field=value form (optional)
	sort := "sort_example" // string | Comma-separated top-level fields; prefix descending fields with - (optional)
	fields := "fields_example" // string | Comma-separated top-level response fields (optional)
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.ExecutionsAPI.ListExecutionsApiV1ExecutionsGet(context.Background()).Cursor(cursor).Limit(limit).Filter(filter).Sort(sort).Fields(fields).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `ExecutionsAPI.ListExecutionsApiV1ExecutionsGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `ListExecutionsApiV1ExecutionsGet`: []PersistedExecution
	fmt.Fprintf(os.Stdout, "Response from `ExecutionsAPI.ListExecutionsApiV1ExecutionsGet`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiListExecutionsApiV1ExecutionsGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **cursor** | **string** | Opaque cursor from the prior page |
 **limit** | **int32** |  | [default to 100]
 **filter** | **[]string** | Repeatable top-level equality filter in field&#x3D;value form |
 **sort** | **string** | Comma-separated top-level fields; prefix descending fields with - |
 **fields** | **string** | Comma-separated top-level response fields |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**[]PersistedExecution**](PersistedExecution.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## PreviewExecutionControlApiV1ExecutionsExecutionIdInterventionsPreviewPost

> ExecutionInterventionPreview PreviewExecutionControlApiV1ExecutionsExecutionIdInterventionsPreviewPost(ctx, executionId).ExecutionInterventionPreviewRequest(executionInterventionPreviewRequest).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Preview Execution Control

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
	executionId := "38400000-8cf0-11bd-b23e-10b96e4ef00d" // string |
	executionInterventionPreviewRequest := *openapiclient.NewExecutionInterventionPreviewRequest(openapiclient.ExecutionInterventionAction("PAUSE")) // ExecutionInterventionPreviewRequest |
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.ExecutionsAPI.PreviewExecutionControlApiV1ExecutionsExecutionIdInterventionsPreviewPost(context.Background(), executionId).ExecutionInterventionPreviewRequest(executionInterventionPreviewRequest).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `ExecutionsAPI.PreviewExecutionControlApiV1ExecutionsExecutionIdInterventionsPreviewPost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `PreviewExecutionControlApiV1ExecutionsExecutionIdInterventionsPreviewPost`: ExecutionInterventionPreview
	fmt.Fprintf(os.Stdout, "Response from `ExecutionsAPI.PreviewExecutionControlApiV1ExecutionsExecutionIdInterventionsPreviewPost`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**executionId** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiPreviewExecutionControlApiV1ExecutionsExecutionIdInterventionsPreviewPostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------

 **executionInterventionPreviewRequest** | [**ExecutionInterventionPreviewRequest**](ExecutionInterventionPreviewRequest.md) |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**ExecutionInterventionPreview**](ExecutionInterventionPreview.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## ReduceExecutionEventsApiV1ExecutionsReducePost

> ReduceExecutionResponse ReduceExecutionEventsApiV1ExecutionsReducePost(ctx).ReduceExecutionRequest(reduceExecutionRequest).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Reduce Execution Events

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
	reduceExecutionRequest := *openapiclient.NewReduceExecutionRequest([]openapiclient.ExecutionEvent{*openapiclient.NewExecutionEvent(openapiclient.ExecutionEventType("ExecutionCreated"))}, *openapiclient.NewExecutionSnapshot("ExecutionId_example", "FlowId_example", int32(123), "Namespace_example", "TenantId_example")) // ReduceExecutionRequest |
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.ExecutionsAPI.ReduceExecutionEventsApiV1ExecutionsReducePost(context.Background()).ReduceExecutionRequest(reduceExecutionRequest).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `ExecutionsAPI.ReduceExecutionEventsApiV1ExecutionsReducePost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `ReduceExecutionEventsApiV1ExecutionsReducePost`: ReduceExecutionResponse
	fmt.Fprintf(os.Stdout, "Response from `ExecutionsAPI.ReduceExecutionEventsApiV1ExecutionsReducePost`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiReduceExecutionEventsApiV1ExecutionsReducePostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **reduceExecutionRequest** | [**ReduceExecutionRequest**](ReduceExecutionRequest.md) |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**ReduceExecutionResponse**](ReduceExecutionResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## ResumeTaskRunApiV1ExecutionsExecutionIdTaskRunsTaskRunIdResumePost

> PersistedTaskRun ResumeTaskRunApiV1ExecutionsExecutionIdTaskRunsTaskRunIdResumePost(ctx, executionId, taskRunId).ResumeTaskRequest(resumeTaskRequest).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Resume Task Run

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
	executionId := "38400000-8cf0-11bd-b23e-10b96e4ef00d" // string |
	taskRunId := "38400000-8cf0-11bd-b23e-10b96e4ef00d" // string |
	resumeTaskRequest := *openapiclient.NewResumeTaskRequest(*openapiclient.NewTaskCompletion(), "ResumeToken_example") // ResumeTaskRequest |
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.ExecutionsAPI.ResumeTaskRunApiV1ExecutionsExecutionIdTaskRunsTaskRunIdResumePost(context.Background(), executionId, taskRunId).ResumeTaskRequest(resumeTaskRequest).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `ExecutionsAPI.ResumeTaskRunApiV1ExecutionsExecutionIdTaskRunsTaskRunIdResumePost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `ResumeTaskRunApiV1ExecutionsExecutionIdTaskRunsTaskRunIdResumePost`: PersistedTaskRun
	fmt.Fprintf(os.Stdout, "Response from `ExecutionsAPI.ResumeTaskRunApiV1ExecutionsExecutionIdTaskRunsTaskRunIdResumePost`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**executionId** | **string** |  |
**taskRunId** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiResumeTaskRunApiV1ExecutionsExecutionIdTaskRunsTaskRunIdResumePostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------


 **resumeTaskRequest** | [**ResumeTaskRequest**](ResumeTaskRequest.md) |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**PersistedTaskRun**](PersistedTaskRun.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## StreamExecutionEvidenceApiV1ExecutionsExecutionIdEvidenceStreamGet

> StreamExecutionEvidenceApiV1ExecutionsExecutionIdEvidenceStreamGet(ctx, executionId).Cursor(cursor).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Stream Execution Evidence

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
	executionId := "38400000-8cf0-11bd-b23e-10b96e4ef00d" // string |
	cursor := "cursor_example" // string | Opaque reconnect cursor (optional)
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	r, err := apiClient.ExecutionsAPI.StreamExecutionEvidenceApiV1ExecutionsExecutionIdEvidenceStreamGet(context.Background(), executionId).Cursor(cursor).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `ExecutionsAPI.StreamExecutionEvidenceApiV1ExecutionsExecutionIdEvidenceStreamGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**executionId** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiStreamExecutionEvidenceApiV1ExecutionsExecutionIdEvidenceStreamGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------

 **cursor** | **string** | Opaque reconnect cursor |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

 (empty response body)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/x-ndjson, application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## StreamExecutionLogsApiV1ExecutionsExecutionIdLogsStreamGet

> StreamExecutionLogsApiV1ExecutionsExecutionIdLogsStreamGet(ctx, executionId).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Stream Execution Logs

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
	executionId := "38400000-8cf0-11bd-b23e-10b96e4ef00d" // string |
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	r, err := apiClient.ExecutionsAPI.StreamExecutionLogsApiV1ExecutionsExecutionIdLogsStreamGet(context.Background(), executionId).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `ExecutionsAPI.StreamExecutionLogsApiV1ExecutionsExecutionIdLogsStreamGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**executionId** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiStreamExecutionLogsApiV1ExecutionsExecutionIdLogsStreamGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------

 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

 (empty response body)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/x-ndjson, application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)
