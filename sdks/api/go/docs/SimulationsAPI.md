# \SimulationsAPI

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**CompareFlowSimulationsApiV1FlowsNamespaceFlowIdSimulationsComparePost**](SimulationsAPI.md#CompareFlowSimulationsApiV1FlowsNamespaceFlowIdSimulationsComparePost) | **Post** /api/v1/flows/{namespace}/{flow_id}/simulations/compare | Compare Flow Simulations
[**SimulateFlowRevisionApiV1FlowsNamespaceFlowIdRevisionsRevisionSimulatePost**](SimulationsAPI.md#SimulateFlowRevisionApiV1FlowsNamespaceFlowIdRevisionsRevisionSimulatePost) | **Post** /api/v1/flows/{namespace}/{flow_id}/revisions/{revision}/simulate | Simulate Flow Revision



## CompareFlowSimulationsApiV1FlowsNamespaceFlowIdSimulationsComparePost

> SimulationComparison CompareFlowSimulationsApiV1FlowsNamespaceFlowIdSimulationsComparePost(ctx, namespace, flowId).From(from).To(to).SimulationRequest(simulationRequest).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Compare Flow Simulations

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
	flowId := "flowId_example" // string |
	from := int32(56) // int32 |
	to := int32(56) // int32 |
	simulationRequest := *openapiclient.NewSimulationRequest() // SimulationRequest |
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.SimulationsAPI.CompareFlowSimulationsApiV1FlowsNamespaceFlowIdSimulationsComparePost(context.Background(), namespace, flowId).From(from).To(to).SimulationRequest(simulationRequest).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `SimulationsAPI.CompareFlowSimulationsApiV1FlowsNamespaceFlowIdSimulationsComparePost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `CompareFlowSimulationsApiV1FlowsNamespaceFlowIdSimulationsComparePost`: SimulationComparison
	fmt.Fprintf(os.Stdout, "Response from `SimulationsAPI.CompareFlowSimulationsApiV1FlowsNamespaceFlowIdSimulationsComparePost`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**namespace** | **string** |  |
**flowId** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiCompareFlowSimulationsApiV1FlowsNamespaceFlowIdSimulationsComparePostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------


 **from** | **int32** |  |
 **to** | **int32** |  |
 **simulationRequest** | **SimulationRequest** |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

**SimulationComparison**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## SimulateFlowRevisionApiV1FlowsNamespaceFlowIdRevisionsRevisionSimulatePost

> SimulationPlan SimulateFlowRevisionApiV1FlowsNamespaceFlowIdRevisionsRevisionSimulatePost(ctx, namespace, flowId, revision).SimulationRequest(simulationRequest).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Simulate Flow Revision

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
	flowId := "flowId_example" // string |
	revision := int32(56) // int32 |
	simulationRequest := *openapiclient.NewSimulationRequest() // SimulationRequest |
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.SimulationsAPI.SimulateFlowRevisionApiV1FlowsNamespaceFlowIdRevisionsRevisionSimulatePost(context.Background(), namespace, flowId, revision).SimulationRequest(simulationRequest).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `SimulationsAPI.SimulateFlowRevisionApiV1FlowsNamespaceFlowIdRevisionsRevisionSimulatePost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `SimulateFlowRevisionApiV1FlowsNamespaceFlowIdRevisionsRevisionSimulatePost`: SimulationPlan
	fmt.Fprintf(os.Stdout, "Response from `SimulationsAPI.SimulateFlowRevisionApiV1FlowsNamespaceFlowIdRevisionsRevisionSimulatePost`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**namespace** | **string** |  |
**flowId** | **string** |  |
**revision** | **int32** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiSimulateFlowRevisionApiV1FlowsNamespaceFlowIdRevisionsRevisionSimulatePostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------



 **simulationRequest** | **SimulationRequest** |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

**SimulationPlan**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)
