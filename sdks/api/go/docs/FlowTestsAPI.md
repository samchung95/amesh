# \FlowTestsAPI

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**DeleteFlowTestApiV1FlowsNamespaceFlowIdTestsTestIdDelete**](FlowTestsAPI.md#DeleteFlowTestApiV1FlowsNamespaceFlowIdTestsTestIdDelete) | **Delete** /api/v1/flows/{namespace}/{flow_id}/tests/{test_id} | Delete Flow Test
[**GetFlowTestGateApiV1NamespacesNamespaceFlowTestGateGet**](FlowTestsAPI.md#GetFlowTestGateApiV1NamespacesNamespaceFlowTestGateGet) | **Get** /api/v1/namespaces/{namespace}/flow-test-gate | Get Flow Test Gate
[**ListFlowTestRunsApiV1FlowsNamespaceFlowIdTestsRunsGet**](FlowTestsAPI.md#ListFlowTestRunsApiV1FlowsNamespaceFlowIdTestsRunsGet) | **Get** /api/v1/flows/{namespace}/{flow_id}/tests/runs | List Flow Test Runs
[**ListFlowTestsApiV1FlowsNamespaceFlowIdTestsGet**](FlowTestsAPI.md#ListFlowTestsApiV1FlowsNamespaceFlowIdTestsGet) | **Get** /api/v1/flows/{namespace}/{flow_id}/tests | List Flow Tests
[**RunFlowTestsApiV1FlowsNamespaceFlowIdTestsRunsPost**](FlowTestsAPI.md#RunFlowTestsApiV1FlowsNamespaceFlowIdTestsRunsPost) | **Post** /api/v1/flows/{namespace}/{flow_id}/tests/runs | Run Flow Tests
[**SaveFlowTestApiV1FlowsNamespaceFlowIdTestsPut**](FlowTestsAPI.md#SaveFlowTestApiV1FlowsNamespaceFlowIdTestsPut) | **Put** /api/v1/flows/{namespace}/{flow_id}/tests | Save Flow Test
[**UpdateFlowTestGateApiV1NamespacesNamespaceFlowTestGatePut**](FlowTestsAPI.md#UpdateFlowTestGateApiV1NamespacesNamespaceFlowTestGatePut) | **Put** /api/v1/namespaces/{namespace}/flow-test-gate | Update Flow Test Gate



## DeleteFlowTestApiV1FlowsNamespaceFlowIdTestsTestIdDelete

> DeleteFlowTestApiV1FlowsNamespaceFlowIdTestsTestIdDelete(ctx, namespace, flowId, testId).ExpectedVersion(expectedVersion).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Delete Flow Test

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
	testId := "testId_example" // string |
	expectedVersion := int32(56) // int32 |
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	r, err := apiClient.FlowTestsAPI.DeleteFlowTestApiV1FlowsNamespaceFlowIdTestsTestIdDelete(context.Background(), namespace, flowId, testId).ExpectedVersion(expectedVersion).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `FlowTestsAPI.DeleteFlowTestApiV1FlowsNamespaceFlowIdTestsTestIdDelete``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**namespace** | **string** |  |
**flowId** | **string** |  |
**testId** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiDeleteFlowTestApiV1FlowsNamespaceFlowIdTestsTestIdDeleteRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------



 **expectedVersion** | **int32** |  |
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


## GetFlowTestGateApiV1NamespacesNamespaceFlowTestGateGet

> FlowTestQualityGate GetFlowTestGateApiV1NamespacesNamespaceFlowTestGateGet(ctx, namespace).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Get Flow Test Gate

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
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.FlowTestsAPI.GetFlowTestGateApiV1NamespacesNamespaceFlowTestGateGet(context.Background(), namespace).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `FlowTestsAPI.GetFlowTestGateApiV1NamespacesNamespaceFlowTestGateGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `GetFlowTestGateApiV1NamespacesNamespaceFlowTestGateGet`: FlowTestQualityGate
	fmt.Fprintf(os.Stdout, "Response from `FlowTestsAPI.GetFlowTestGateApiV1NamespacesNamespaceFlowTestGateGet`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**namespace** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiGetFlowTestGateApiV1NamespacesNamespaceFlowTestGateGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------

 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**FlowTestQualityGate**](FlowTestQualityGate.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## ListFlowTestRunsApiV1FlowsNamespaceFlowIdTestsRunsGet

> []FlowTestRunResult ListFlowTestRunsApiV1FlowsNamespaceFlowIdTestsRunsGet(ctx, namespace, flowId).Revision(revision).Limit(limit).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

List Flow Test Runs

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
	revision := int32(56) // int32 |  (optional)
	limit := int32(56) // int32 |  (optional) (default to 50)
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.FlowTestsAPI.ListFlowTestRunsApiV1FlowsNamespaceFlowIdTestsRunsGet(context.Background(), namespace, flowId).Revision(revision).Limit(limit).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `FlowTestsAPI.ListFlowTestRunsApiV1FlowsNamespaceFlowIdTestsRunsGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `ListFlowTestRunsApiV1FlowsNamespaceFlowIdTestsRunsGet`: []FlowTestRunResult
	fmt.Fprintf(os.Stdout, "Response from `FlowTestsAPI.ListFlowTestRunsApiV1FlowsNamespaceFlowIdTestsRunsGet`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**namespace** | **string** |  |
**flowId** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiListFlowTestRunsApiV1FlowsNamespaceFlowIdTestsRunsGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------


 **revision** | **int32** |  |
 **limit** | **int32** |  | [default to 50]
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**[]FlowTestRunResult**](FlowTestRunResult.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## ListFlowTestsApiV1FlowsNamespaceFlowIdTestsGet

> []FlowTestDefinition ListFlowTestsApiV1FlowsNamespaceFlowIdTestsGet(ctx, namespace, flowId).Revision(revision).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

List Flow Tests

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
	revision := int32(56) // int32 |  (optional)
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.FlowTestsAPI.ListFlowTestsApiV1FlowsNamespaceFlowIdTestsGet(context.Background(), namespace, flowId).Revision(revision).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `FlowTestsAPI.ListFlowTestsApiV1FlowsNamespaceFlowIdTestsGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `ListFlowTestsApiV1FlowsNamespaceFlowIdTestsGet`: []FlowTestDefinition
	fmt.Fprintf(os.Stdout, "Response from `FlowTestsAPI.ListFlowTestsApiV1FlowsNamespaceFlowIdTestsGet`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**namespace** | **string** |  |
**flowId** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiListFlowTestsApiV1FlowsNamespaceFlowIdTestsGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------


 **revision** | **int32** |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**[]FlowTestDefinition**](FlowTestDefinition.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## RunFlowTestsApiV1FlowsNamespaceFlowIdTestsRunsPost

> FlowTestRunResult RunFlowTestsApiV1FlowsNamespaceFlowIdTestsRunsPost(ctx, namespace, flowId).Revision(revision).FlowTestRunRequest(flowTestRunRequest).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Run Flow Tests

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
	flowTestRunRequest := *openapiclient.NewFlowTestRunRequest() // FlowTestRunRequest |
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.FlowTestsAPI.RunFlowTestsApiV1FlowsNamespaceFlowIdTestsRunsPost(context.Background(), namespace, flowId).Revision(revision).FlowTestRunRequest(flowTestRunRequest).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `FlowTestsAPI.RunFlowTestsApiV1FlowsNamespaceFlowIdTestsRunsPost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `RunFlowTestsApiV1FlowsNamespaceFlowIdTestsRunsPost`: FlowTestRunResult
	fmt.Fprintf(os.Stdout, "Response from `FlowTestsAPI.RunFlowTestsApiV1FlowsNamespaceFlowIdTestsRunsPost`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**namespace** | **string** |  |
**flowId** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiRunFlowTestsApiV1FlowsNamespaceFlowIdTestsRunsPostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------


 **revision** | **int32** |  |
 **flowTestRunRequest** | [**FlowTestRunRequest**](FlowTestRunRequest.md) |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**FlowTestRunResult**](FlowTestRunResult.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## SaveFlowTestApiV1FlowsNamespaceFlowIdTestsPut

> FlowTestDefinition SaveFlowTestApiV1FlowsNamespaceFlowIdTestsPut(ctx, namespace, flowId).FlowTestDefinitionCreateRequest(flowTestDefinitionCreateRequest).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Save Flow Test

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
	flowTestDefinitionCreateRequest := *openapiclient.NewFlowTestDefinitionCreateRequest("Name_example", int32(123), "TestId_example") // FlowTestDefinitionCreateRequest |
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.FlowTestsAPI.SaveFlowTestApiV1FlowsNamespaceFlowIdTestsPut(context.Background(), namespace, flowId).FlowTestDefinitionCreateRequest(flowTestDefinitionCreateRequest).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `FlowTestsAPI.SaveFlowTestApiV1FlowsNamespaceFlowIdTestsPut``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `SaveFlowTestApiV1FlowsNamespaceFlowIdTestsPut`: FlowTestDefinition
	fmt.Fprintf(os.Stdout, "Response from `FlowTestsAPI.SaveFlowTestApiV1FlowsNamespaceFlowIdTestsPut`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**namespace** | **string** |  |
**flowId** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiSaveFlowTestApiV1FlowsNamespaceFlowIdTestsPutRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------


 **flowTestDefinitionCreateRequest** | [**FlowTestDefinitionCreateRequest**](FlowTestDefinitionCreateRequest.md) |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**FlowTestDefinition**](FlowTestDefinition.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## UpdateFlowTestGateApiV1NamespacesNamespaceFlowTestGatePut

> FlowTestQualityGate UpdateFlowTestGateApiV1NamespacesNamespaceFlowTestGatePut(ctx, namespace).FlowTestQualityGateUpdate(flowTestQualityGateUpdate).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Update Flow Test Gate

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
	flowTestQualityGateUpdate := *openapiclient.NewFlowTestQualityGateUpdate() // FlowTestQualityGateUpdate |
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.FlowTestsAPI.UpdateFlowTestGateApiV1NamespacesNamespaceFlowTestGatePut(context.Background(), namespace).FlowTestQualityGateUpdate(flowTestQualityGateUpdate).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `FlowTestsAPI.UpdateFlowTestGateApiV1NamespacesNamespaceFlowTestGatePut``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `UpdateFlowTestGateApiV1NamespacesNamespaceFlowTestGatePut`: FlowTestQualityGate
	fmt.Fprintf(os.Stdout, "Response from `FlowTestsAPI.UpdateFlowTestGateApiV1NamespacesNamespaceFlowTestGatePut`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**namespace** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiUpdateFlowTestGateApiV1NamespacesNamespaceFlowTestGatePutRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------

 **flowTestQualityGateUpdate** | [**FlowTestQualityGateUpdate**](FlowTestQualityGateUpdate.md) |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**FlowTestQualityGate**](FlowTestQualityGate.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)
