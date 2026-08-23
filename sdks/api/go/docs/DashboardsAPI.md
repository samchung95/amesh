# \DashboardsAPI

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**DeleteDashboardApiV1DashboardsDashboardIdDelete**](DashboardsAPI.md#DeleteDashboardApiV1DashboardsDashboardIdDelete) | **Delete** /api/v1/dashboards/{dashboard_id} | Delete Dashboard
[**ExecuteDashboardQueryApiV1DashboardQueriesPost**](DashboardsAPI.md#ExecuteDashboardQueryApiV1DashboardQueriesPost) | **Post** /api/v1/dashboard-queries | Execute Dashboard Query
[**ExportDashboardApiV1DashboardsDashboardIdExportGet**](DashboardsAPI.md#ExportDashboardApiV1DashboardsDashboardIdExportGet) | **Get** /api/v1/dashboards/{dashboard_id}/export | Export Dashboard
[**GetDashboardApiV1DashboardsDashboardIdGet**](DashboardsAPI.md#GetDashboardApiV1DashboardsDashboardIdGet) | **Get** /api/v1/dashboards/{dashboard_id} | Get Dashboard
[**ListDashboardsApiV1DashboardsGet**](DashboardsAPI.md#ListDashboardsApiV1DashboardsGet) | **Get** /api/v1/dashboards | List Dashboards
[**PutDashboardApiV1DashboardsDashboardIdPut**](DashboardsAPI.md#PutDashboardApiV1DashboardsDashboardIdPut) | **Put** /api/v1/dashboards/{dashboard_id} | Put Dashboard
[**RenderDashboardApiV1DashboardsDashboardIdRenderPost**](DashboardsAPI.md#RenderDashboardApiV1DashboardsDashboardIdRenderPost) | **Post** /api/v1/dashboards/{dashboard_id}/render | Render Dashboard



## DeleteDashboardApiV1DashboardsDashboardIdDelete

> DeleteDashboardApiV1DashboardsDashboardIdDelete(ctx, dashboardId).ExpectedVersion(expectedVersion).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Delete Dashboard

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
	dashboardId := "dashboardId_example" // string |
	expectedVersion := int32(56) // int32 |
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	r, err := apiClient.DashboardsAPI.DeleteDashboardApiV1DashboardsDashboardIdDelete(context.Background(), dashboardId).ExpectedVersion(expectedVersion).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `DashboardsAPI.DeleteDashboardApiV1DashboardsDashboardIdDelete``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**dashboardId** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiDeleteDashboardApiV1DashboardsDashboardIdDeleteRequest struct via the builder pattern


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


## ExecuteDashboardQueryApiV1DashboardQueriesPost

> DashboardQueryResult ExecuteDashboardQueryApiV1DashboardQueriesPost(ctx).DashboardQuery(dashboardQuery).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Execute Dashboard Query

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
	dashboardQuery := *openapiclient.NewDashboardQuery(openapiclient.DashboardDataSource("EXECUTIONS"), openapiclient.DashboardVisualization("TIME_SERIES")) // DashboardQuery |
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.DashboardsAPI.ExecuteDashboardQueryApiV1DashboardQueriesPost(context.Background()).DashboardQuery(dashboardQuery).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `DashboardsAPI.ExecuteDashboardQueryApiV1DashboardQueriesPost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `ExecuteDashboardQueryApiV1DashboardQueriesPost`: DashboardQueryResult
	fmt.Fprintf(os.Stdout, "Response from `DashboardsAPI.ExecuteDashboardQueryApiV1DashboardQueriesPost`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiExecuteDashboardQueryApiV1DashboardQueriesPostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **dashboardQuery** | [**DashboardQuery**](DashboardQuery.md) |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**DashboardQueryResult**](DashboardQueryResult.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## ExportDashboardApiV1DashboardsDashboardIdExportGet

> interface{} ExportDashboardApiV1DashboardsDashboardIdExportGet(ctx, dashboardId).Format(format).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Export Dashboard

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
	dashboardId := "dashboardId_example" // string |
	format := "format_example" // string |  (optional) (default to "yaml")
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.DashboardsAPI.ExportDashboardApiV1DashboardsDashboardIdExportGet(context.Background(), dashboardId).Format(format).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `DashboardsAPI.ExportDashboardApiV1DashboardsDashboardIdExportGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `ExportDashboardApiV1DashboardsDashboardIdExportGet`: interface{}
	fmt.Fprintf(os.Stdout, "Response from `DashboardsAPI.ExportDashboardApiV1DashboardsDashboardIdExportGet`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**dashboardId** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiExportDashboardApiV1DashboardsDashboardIdExportGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------

 **format** | **string** |  | [default to &quot;yaml&quot;]
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

**interface{}**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## GetDashboardApiV1DashboardsDashboardIdGet

> DashboardDefinition GetDashboardApiV1DashboardsDashboardIdGet(ctx, dashboardId).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Get Dashboard

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
	dashboardId := "dashboardId_example" // string |
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.DashboardsAPI.GetDashboardApiV1DashboardsDashboardIdGet(context.Background(), dashboardId).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `DashboardsAPI.GetDashboardApiV1DashboardsDashboardIdGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `GetDashboardApiV1DashboardsDashboardIdGet`: DashboardDefinition
	fmt.Fprintf(os.Stdout, "Response from `DashboardsAPI.GetDashboardApiV1DashboardsDashboardIdGet`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**dashboardId** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiGetDashboardApiV1DashboardsDashboardIdGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------

 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**DashboardDefinition**](DashboardDefinition.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## ListDashboardsApiV1DashboardsGet

> []DashboardDefinition ListDashboardsApiV1DashboardsGet(ctx).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

List Dashboards

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
	resp, r, err := apiClient.DashboardsAPI.ListDashboardsApiV1DashboardsGet(context.Background()).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `DashboardsAPI.ListDashboardsApiV1DashboardsGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `ListDashboardsApiV1DashboardsGet`: []DashboardDefinition
	fmt.Fprintf(os.Stdout, "Response from `DashboardsAPI.ListDashboardsApiV1DashboardsGet`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiListDashboardsApiV1DashboardsGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**[]DashboardDefinition**](DashboardDefinition.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## PutDashboardApiV1DashboardsDashboardIdPut

> DashboardDefinition PutDashboardApiV1DashboardsDashboardIdPut(ctx, dashboardId).DashboardSpec(dashboardSpec).ExpectedVersion(expectedVersion).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Put Dashboard

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
	dashboardId := "dashboardId_example" // string |
	dashboardSpec := *openapiclient.NewDashboardSpec("Title_example", []openapiclient.DashboardWidget{*openapiclient.NewDashboardWidget(*openapiclient.NewDashboardQuery(openapiclient.DashboardDataSource("EXECUTIONS"), openapiclient.DashboardVisualization("TIME_SERIES")), "Title_example", "WidgetId_example")}) // DashboardSpec |
	expectedVersion := int32(56) // int32 |  (optional)
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.DashboardsAPI.PutDashboardApiV1DashboardsDashboardIdPut(context.Background(), dashboardId).DashboardSpec(dashboardSpec).ExpectedVersion(expectedVersion).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `DashboardsAPI.PutDashboardApiV1DashboardsDashboardIdPut``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `PutDashboardApiV1DashboardsDashboardIdPut`: DashboardDefinition
	fmt.Fprintf(os.Stdout, "Response from `DashboardsAPI.PutDashboardApiV1DashboardsDashboardIdPut`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**dashboardId** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiPutDashboardApiV1DashboardsDashboardIdPutRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------

 **dashboardSpec** | [**DashboardSpec**](DashboardSpec.md) |  |
 **expectedVersion** | **int32** |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**DashboardDefinition**](DashboardDefinition.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## RenderDashboardApiV1DashboardsDashboardIdRenderPost

> DashboardRender RenderDashboardApiV1DashboardsDashboardIdRenderPost(ctx, dashboardId).DashboardFilters(dashboardFilters).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Render Dashboard

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
	dashboardId := "dashboardId_example" // string |
	dashboardFilters := *openapiclient.NewDashboardFilters() // DashboardFilters |
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.DashboardsAPI.RenderDashboardApiV1DashboardsDashboardIdRenderPost(context.Background(), dashboardId).DashboardFilters(dashboardFilters).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `DashboardsAPI.RenderDashboardApiV1DashboardsDashboardIdRenderPost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `RenderDashboardApiV1DashboardsDashboardIdRenderPost`: DashboardRender
	fmt.Fprintf(os.Stdout, "Response from `DashboardsAPI.RenderDashboardApiV1DashboardsDashboardIdRenderPost`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**dashboardId** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiRenderDashboardApiV1DashboardsDashboardIdRenderPostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------

 **dashboardFilters** | [**DashboardFilters**](DashboardFilters.md) |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**DashboardRender**](DashboardRender.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)
