# \ChecksAPI

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**GetCheckComplianceApiV1CheckComplianceGet**](ChecksAPI.md#GetCheckComplianceApiV1CheckComplianceGet) | **Get** /api/v1/check-compliance | Get Check Compliance
[**ListCheckEvaluationsApiV1CheckEvaluationsGet**](ChecksAPI.md#ListCheckEvaluationsApiV1CheckEvaluationsGet) | **Get** /api/v1/check-evaluations | List Check Evaluations
[**ListCheckPoliciesApiV1CheckPoliciesGet**](ChecksAPI.md#ListCheckPoliciesApiV1CheckPoliciesGet) | **Get** /api/v1/check-policies | List Check Policies
[**UpsertCheckPolicyApiV1CheckPoliciesNamespacePolicyKeyPut**](ChecksAPI.md#UpsertCheckPolicyApiV1CheckPoliciesNamespacePolicyKeyPut) | **Put** /api/v1/check-policies/{namespace}/{policy_key} | Upsert Check Policy



## GetCheckComplianceApiV1CheckComplianceGet

> []CheckComplianceSummary GetCheckComplianceApiV1CheckComplianceGet(ctx).GroupBy(groupBy).FromTime(fromTime).ToTime(toTime).Namespace(namespace).FlowId(flowId).Limit(limit).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Get Check Compliance

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
	groupBy := "groupBy_example" // string |  (optional) (default to "flow")
	fromTime := time.Now() // time.Time |  (optional)
	toTime := time.Now() // time.Time |  (optional)
	namespace := "namespace_example" // string |  (optional)
	flowId := "flowId_example" // string |  (optional)
	limit := int32(56) // int32 |  (optional) (default to 100)
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.ChecksAPI.GetCheckComplianceApiV1CheckComplianceGet(context.Background()).GroupBy(groupBy).FromTime(fromTime).ToTime(toTime).Namespace(namespace).FlowId(flowId).Limit(limit).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `ChecksAPI.GetCheckComplianceApiV1CheckComplianceGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `GetCheckComplianceApiV1CheckComplianceGet`: []CheckComplianceSummary
	fmt.Fprintf(os.Stdout, "Response from `ChecksAPI.GetCheckComplianceApiV1CheckComplianceGet`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiGetCheckComplianceApiV1CheckComplianceGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **groupBy** | **string** |  | [default to &quot;flow&quot;]
 **fromTime** | **time.Time** |  |
 **toTime** | **time.Time** |  |
 **namespace** | **string** |  |
 **flowId** | **string** |  |
 **limit** | **int32** |  | [default to 100]
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**[]CheckComplianceSummary**](CheckComplianceSummary.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## ListCheckEvaluationsApiV1CheckEvaluationsGet

> []CheckEvaluation ListCheckEvaluationsApiV1CheckEvaluationsGet(ctx).Namespace(namespace).FlowId(flowId).ExecutionId(executionId).Outcome(outcome).Limit(limit).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

List Check Evaluations

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
	flowId := "flowId_example" // string |  (optional)
	executionId := "38400000-8cf0-11bd-b23e-10b96e4ef00d" // string |  (optional)
	outcome := openapiclient.CheckOutcome("PASS") // CheckOutcome |  (optional)
	limit := int32(56) // int32 |  (optional) (default to 100)
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.ChecksAPI.ListCheckEvaluationsApiV1CheckEvaluationsGet(context.Background()).Namespace(namespace).FlowId(flowId).ExecutionId(executionId).Outcome(outcome).Limit(limit).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `ChecksAPI.ListCheckEvaluationsApiV1CheckEvaluationsGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `ListCheckEvaluationsApiV1CheckEvaluationsGet`: []CheckEvaluation
	fmt.Fprintf(os.Stdout, "Response from `ChecksAPI.ListCheckEvaluationsApiV1CheckEvaluationsGet`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiListCheckEvaluationsApiV1CheckEvaluationsGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **namespace** | **string** |  |
 **flowId** | **string** |  |
 **executionId** | **string** |  |
 **outcome** | **CheckOutcome** |  |
 **limit** | **int32** |  | [default to 100]
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**[]CheckEvaluation**](CheckEvaluation.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## ListCheckPoliciesApiV1CheckPoliciesGet

> []NamespaceCheckPolicy ListCheckPoliciesApiV1CheckPoliciesGet(ctx).Namespace(namespace).Limit(limit).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

List Check Policies

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
	limit := int32(56) // int32 |  (optional) (default to 100)
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.ChecksAPI.ListCheckPoliciesApiV1CheckPoliciesGet(context.Background()).Namespace(namespace).Limit(limit).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `ChecksAPI.ListCheckPoliciesApiV1CheckPoliciesGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `ListCheckPoliciesApiV1CheckPoliciesGet`: []NamespaceCheckPolicy
	fmt.Fprintf(os.Stdout, "Response from `ChecksAPI.ListCheckPoliciesApiV1CheckPoliciesGet`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiListCheckPoliciesApiV1CheckPoliciesGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **namespace** | **string** |  |
 **limit** | **int32** |  | [default to 100]
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**[]NamespaceCheckPolicy**](NamespaceCheckPolicy.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## UpsertCheckPolicyApiV1CheckPoliciesNamespacePolicyKeyPut

> NamespaceCheckPolicy UpsertCheckPolicyApiV1CheckPoliciesNamespacePolicyKeyPut(ctx, namespace, policyKey).CheckPolicyUpsertRequest(checkPolicyUpsertRequest).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Upsert Check Policy

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
	policyKey := "policyKey_example" // string |
	checkPolicyUpsertRequest := *openapiclient.NewCheckPolicyUpsertRequest(*openapiclient.NewCheckDefinition("Id_example", "Type_example")) // CheckPolicyUpsertRequest |
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.ChecksAPI.UpsertCheckPolicyApiV1CheckPoliciesNamespacePolicyKeyPut(context.Background(), namespace, policyKey).CheckPolicyUpsertRequest(checkPolicyUpsertRequest).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `ChecksAPI.UpsertCheckPolicyApiV1CheckPoliciesNamespacePolicyKeyPut``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `UpsertCheckPolicyApiV1CheckPoliciesNamespacePolicyKeyPut`: NamespaceCheckPolicy
	fmt.Fprintf(os.Stdout, "Response from `ChecksAPI.UpsertCheckPolicyApiV1CheckPoliciesNamespacePolicyKeyPut`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**namespace** | **string** |  |
**policyKey** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiUpsertCheckPolicyApiV1CheckPoliciesNamespacePolicyKeyPutRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------


 **checkPolicyUpsertRequest** | **CheckPolicyUpsertRequest** |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

**NamespaceCheckPolicy**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)
