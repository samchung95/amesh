# \BlueprintsAPI

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**GetBlueprintVersionApiV1BlueprintsBlueprintIdVersionGet**](BlueprintsAPI.md#GetBlueprintVersionApiV1BlueprintsBlueprintIdVersionGet) | **Get** /api/v1/blueprints/{blueprint_id}/{version} | Get Blueprint Version
[**GetBlueprintsApiV1BlueprintsGet**](BlueprintsAPI.md#GetBlueprintsApiV1BlueprintsGet) | **Get** /api/v1/blueprints | Get Blueprints
[**InstantiateBlueprintDraftApiV1BlueprintsBlueprintIdVersionInstantiatePost**](BlueprintsAPI.md#InstantiateBlueprintDraftApiV1BlueprintsBlueprintIdVersionInstantiatePost) | **Post** /api/v1/blueprints/{blueprint_id}/{version}/instantiate | Instantiate Blueprint Draft
[**SimulatePlaygroundApiV1PlaygroundSimulatePost**](BlueprintsAPI.md#SimulatePlaygroundApiV1PlaygroundSimulatePost) | **Post** /api/v1/playground/simulate | Simulate Playground



## GetBlueprintVersionApiV1BlueprintsBlueprintIdVersionGet

> BlueprintDefinition GetBlueprintVersionApiV1BlueprintsBlueprintIdVersionGet(ctx, blueprintId, version).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Get Blueprint Version

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
	blueprintId := "blueprintId_example" // string |
	version := "version_example" // string |
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.BlueprintsAPI.GetBlueprintVersionApiV1BlueprintsBlueprintIdVersionGet(context.Background(), blueprintId, version).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `BlueprintsAPI.GetBlueprintVersionApiV1BlueprintsBlueprintIdVersionGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `GetBlueprintVersionApiV1BlueprintsBlueprintIdVersionGet`: BlueprintDefinition
	fmt.Fprintf(os.Stdout, "Response from `BlueprintsAPI.GetBlueprintVersionApiV1BlueprintsBlueprintIdVersionGet`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**blueprintId** | **string** |  |
**version** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiGetBlueprintVersionApiV1BlueprintsBlueprintIdVersionGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------


 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

**BlueprintDefinition**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## GetBlueprintsApiV1BlueprintsGet

> []BlueprintSummary GetBlueprintsApiV1BlueprintsGet(ctx).Q(q).Source(source).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Get Blueprints

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
	q := "q_example" // string |  (optional)
	source := openapiclient.BlueprintCatalogSource("BUILTIN") // BlueprintCatalogSource |  (optional)
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.BlueprintsAPI.GetBlueprintsApiV1BlueprintsGet(context.Background()).Q(q).Source(source).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `BlueprintsAPI.GetBlueprintsApiV1BlueprintsGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `GetBlueprintsApiV1BlueprintsGet`: []BlueprintSummary
	fmt.Fprintf(os.Stdout, "Response from `BlueprintsAPI.GetBlueprintsApiV1BlueprintsGet`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiGetBlueprintsApiV1BlueprintsGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **q** | **string** |  |
 **source** | **BlueprintCatalogSource** |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**[]BlueprintSummary**](BlueprintSummary.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## InstantiateBlueprintDraftApiV1BlueprintsBlueprintIdVersionInstantiatePost

> BlueprintDraftResponse InstantiateBlueprintDraftApiV1BlueprintsBlueprintIdVersionInstantiatePost(ctx, blueprintId, version).BlueprintInstantiationRequest(blueprintInstantiationRequest).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Instantiate Blueprint Draft

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
	blueprintId := "blueprintId_example" // string |
	version := "version_example" // string |
	blueprintInstantiationRequest := *openapiclient.NewBlueprintInstantiationRequest() // BlueprintInstantiationRequest |
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.BlueprintsAPI.InstantiateBlueprintDraftApiV1BlueprintsBlueprintIdVersionInstantiatePost(context.Background(), blueprintId, version).BlueprintInstantiationRequest(blueprintInstantiationRequest).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `BlueprintsAPI.InstantiateBlueprintDraftApiV1BlueprintsBlueprintIdVersionInstantiatePost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `InstantiateBlueprintDraftApiV1BlueprintsBlueprintIdVersionInstantiatePost`: BlueprintDraftResponse
	fmt.Fprintf(os.Stdout, "Response from `BlueprintsAPI.InstantiateBlueprintDraftApiV1BlueprintsBlueprintIdVersionInstantiatePost`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**blueprintId** | **string** |  |
**version** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiInstantiateBlueprintDraftApiV1BlueprintsBlueprintIdVersionInstantiatePostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------


 **blueprintInstantiationRequest** | **BlueprintInstantiationRequest** |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

**BlueprintDraftResponse**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## SimulatePlaygroundApiV1PlaygroundSimulatePost

> PlaygroundSimulationResponse SimulatePlaygroundApiV1PlaygroundSimulatePost(ctx).PlaygroundSimulationRequest(playgroundSimulationRequest).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Simulate Playground

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
	playgroundSimulationRequest := *openapiclient.NewPlaygroundSimulationRequest() // PlaygroundSimulationRequest |
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.BlueprintsAPI.SimulatePlaygroundApiV1PlaygroundSimulatePost(context.Background()).PlaygroundSimulationRequest(playgroundSimulationRequest).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `BlueprintsAPI.SimulatePlaygroundApiV1PlaygroundSimulatePost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `SimulatePlaygroundApiV1PlaygroundSimulatePost`: PlaygroundSimulationResponse
	fmt.Fprintf(os.Stdout, "Response from `BlueprintsAPI.SimulatePlaygroundApiV1PlaygroundSimulatePost`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiSimulatePlaygroundApiV1PlaygroundSimulatePostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **playgroundSimulationRequest** | **PlaygroundSimulationRequest** |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

**PlaygroundSimulationResponse**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)
