# \ExternalOrchestrationAPI

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**GetExternalOrchestrationProfileApiV1OrchestrationProfileGet**](ExternalOrchestrationAPI.md#GetExternalOrchestrationProfileApiV1OrchestrationProfileGet) | **Get** /api/v1/orchestration/profile | Get External Orchestration Profile



## GetExternalOrchestrationProfileApiV1OrchestrationProfileGet

> ExternalOrchestrationProfile GetExternalOrchestrationProfileApiV1OrchestrationProfileGet(ctx).Execute()

Get External Orchestration Profile



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

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.ExternalOrchestrationAPI.GetExternalOrchestrationProfileApiV1OrchestrationProfileGet(context.Background()).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `ExternalOrchestrationAPI.GetExternalOrchestrationProfileApiV1OrchestrationProfileGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `GetExternalOrchestrationProfileApiV1OrchestrationProfileGet`: ExternalOrchestrationProfile
	fmt.Fprintf(os.Stdout, "Response from `ExternalOrchestrationAPI.GetExternalOrchestrationProfileApiV1OrchestrationProfileGet`: %v\n", resp)
}
```

### Path Parameters

This endpoint does not need any parameter.

### Other Parameters

Other parameters are passed through a pointer to a apiGetExternalOrchestrationProfileApiV1OrchestrationProfileGetRequest struct via the builder pattern


### Return type

**ExternalOrchestrationProfile**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)
