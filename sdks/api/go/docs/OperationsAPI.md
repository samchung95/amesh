# \OperationsAPI

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**DrainServiceInstanceApiV1OperationsServicesInstanceIdDrainPost**](OperationsAPI.md#DrainServiceInstanceApiV1OperationsServicesInstanceIdDrainPost) | **Post** /api/v1/operations/services/{instance_id}/drain | Drain Service Instance
[**GetAdmissionDiagnosticsApiV1AdmissionsDiagnosticsGet**](OperationsAPI.md#GetAdmissionDiagnosticsApiV1AdmissionsDiagnosticsGet) | **Get** /api/v1/admissions/diagnostics | Get Admission Diagnostics
[**GetReconciliationApiV1ReconciliationsRunIdGet**](OperationsAPI.md#GetReconciliationApiV1ReconciliationsRunIdGet) | **Get** /api/v1/reconciliations/{run_id} | Get Reconciliation
[**GetServiceTopologyApiV1OperationsTopologyGet**](OperationsAPI.md#GetServiceTopologyApiV1OperationsTopologyGet) | **Get** /api/v1/operations/topology | Get Service Topology
[**ListReconciliationsApiV1ReconciliationsGet**](OperationsAPI.md#ListReconciliationsApiV1ReconciliationsGet) | **Get** /api/v1/reconciliations | List Reconciliations
[**ReconcileAdmissionsApiV1AdmissionsReconcilePost**](OperationsAPI.md#ReconcileAdmissionsApiV1AdmissionsReconcilePost) | **Post** /api/v1/admissions/reconcile | Reconcile Admissions
[**RunReconciliationApiV1ReconciliationsPost**](OperationsAPI.md#RunReconciliationApiV1ReconciliationsPost) | **Post** /api/v1/reconciliations | Run Reconciliation



## DrainServiceInstanceApiV1OperationsServicesInstanceIdDrainPost

> ServiceInstance DrainServiceInstanceApiV1OperationsServicesInstanceIdDrainPost(ctx, instanceId).ServiceDrainRequest(serviceDrainRequest).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).Execute()

Drain Service Instance

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
	instanceId := "38400000-8cf0-11bd-b23e-10b96e4ef00d" // string |
	serviceDrainRequest := *openapiclient.NewServiceDrainRequest(int32(123), "Reason_example") // ServiceDrainRequest |
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.OperationsAPI.DrainServiceInstanceApiV1OperationsServicesInstanceIdDrainPost(context.Background(), instanceId).ServiceDrainRequest(serviceDrainRequest).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `OperationsAPI.DrainServiceInstanceApiV1OperationsServicesInstanceIdDrainPost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `DrainServiceInstanceApiV1OperationsServicesInstanceIdDrainPost`: ServiceInstance
	fmt.Fprintf(os.Stdout, "Response from `OperationsAPI.DrainServiceInstanceApiV1OperationsServicesInstanceIdDrainPost`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**instanceId** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiDrainServiceInstanceApiV1OperationsServicesInstanceIdDrainPostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------

 **serviceDrainRequest** | [**ServiceDrainRequest**](ServiceDrainRequest.md) |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |

### Return type

[**ServiceInstance**](ServiceInstance.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## GetAdmissionDiagnosticsApiV1AdmissionsDiagnosticsGet

> AdmissionDiagnostics GetAdmissionDiagnosticsApiV1AdmissionsDiagnosticsGet(ctx).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Get Admission Diagnostics

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
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.OperationsAPI.GetAdmissionDiagnosticsApiV1AdmissionsDiagnosticsGet(context.Background()).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `OperationsAPI.GetAdmissionDiagnosticsApiV1AdmissionsDiagnosticsGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `GetAdmissionDiagnosticsApiV1AdmissionsDiagnosticsGet`: AdmissionDiagnostics
	fmt.Fprintf(os.Stdout, "Response from `OperationsAPI.GetAdmissionDiagnosticsApiV1AdmissionsDiagnosticsGet`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiGetAdmissionDiagnosticsApiV1AdmissionsDiagnosticsGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**AdmissionDiagnostics**](AdmissionDiagnostics.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## GetReconciliationApiV1ReconciliationsRunIdGet

> ReconciliationRun GetReconciliationApiV1ReconciliationsRunIdGet(ctx, runId).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Get Reconciliation

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
	runId := "38400000-8cf0-11bd-b23e-10b96e4ef00d" // string |
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.OperationsAPI.GetReconciliationApiV1ReconciliationsRunIdGet(context.Background(), runId).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `OperationsAPI.GetReconciliationApiV1ReconciliationsRunIdGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `GetReconciliationApiV1ReconciliationsRunIdGet`: ReconciliationRun
	fmt.Fprintf(os.Stdout, "Response from `OperationsAPI.GetReconciliationApiV1ReconciliationsRunIdGet`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**runId** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiGetReconciliationApiV1ReconciliationsRunIdGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------

 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**ReconciliationRun**](ReconciliationRun.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## GetServiceTopologyApiV1OperationsTopologyGet

> ServiceTopology GetServiceTopologyApiV1OperationsTopologyGet(ctx).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).Execute()

Get Service Topology

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
	resp, r, err := apiClient.OperationsAPI.GetServiceTopologyApiV1OperationsTopologyGet(context.Background()).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `OperationsAPI.GetServiceTopologyApiV1OperationsTopologyGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `GetServiceTopologyApiV1OperationsTopologyGet`: ServiceTopology
	fmt.Fprintf(os.Stdout, "Response from `OperationsAPI.GetServiceTopologyApiV1OperationsTopologyGet`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiGetServiceTopologyApiV1OperationsTopologyGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |

### Return type

[**ServiceTopology**](ServiceTopology.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## ListReconciliationsApiV1ReconciliationsGet

> []ReconciliationRun ListReconciliationsApiV1ReconciliationsGet(ctx).Limit(limit).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

List Reconciliations

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
	limit := int32(56) // int32 |  (optional) (default to 50)
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.OperationsAPI.ListReconciliationsApiV1ReconciliationsGet(context.Background()).Limit(limit).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `OperationsAPI.ListReconciliationsApiV1ReconciliationsGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `ListReconciliationsApiV1ReconciliationsGet`: []ReconciliationRun
	fmt.Fprintf(os.Stdout, "Response from `OperationsAPI.ListReconciliationsApiV1ReconciliationsGet`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiListReconciliationsApiV1ReconciliationsGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **limit** | **int32** |  | [default to 50]
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**[]ReconciliationRun**](ReconciliationRun.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## ReconcileAdmissionsApiV1AdmissionsReconcilePost

> map[string]int32 ReconcileAdmissionsApiV1AdmissionsReconcilePost(ctx).Limit(limit).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Reconcile Admissions

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
	limit := int32(56) // int32 |  (optional) (default to 100)
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.OperationsAPI.ReconcileAdmissionsApiV1AdmissionsReconcilePost(context.Background()).Limit(limit).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `OperationsAPI.ReconcileAdmissionsApiV1AdmissionsReconcilePost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `ReconcileAdmissionsApiV1AdmissionsReconcilePost`: map[string]int32
	fmt.Fprintf(os.Stdout, "Response from `OperationsAPI.ReconcileAdmissionsApiV1AdmissionsReconcilePost`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiReconcileAdmissionsApiV1AdmissionsReconcilePostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **limit** | **int32** |  | [default to 100]
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

**map[string]int32**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## RunReconciliationApiV1ReconciliationsPost

> ReconciliationRun RunReconciliationApiV1ReconciliationsPost(ctx).ReconciliationRequest(reconciliationRequest).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Run Reconciliation

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
	reconciliationRequest := *openapiclient.NewReconciliationRequest("IdempotencyKey_example", "Reason_example") // ReconciliationRequest |
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.OperationsAPI.RunReconciliationApiV1ReconciliationsPost(context.Background()).ReconciliationRequest(reconciliationRequest).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `OperationsAPI.RunReconciliationApiV1ReconciliationsPost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `RunReconciliationApiV1ReconciliationsPost`: ReconciliationRun
	fmt.Fprintf(os.Stdout, "Response from `OperationsAPI.RunReconciliationApiV1ReconciliationsPost`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiRunReconciliationApiV1ReconciliationsPostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **reconciliationRequest** | [**ReconciliationRequest**](ReconciliationRequest.md) |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**ReconciliationRun**](ReconciliationRun.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)
