# \PoliciesAPI

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**CreateAdmissionPolicyApiV1PoliciesPost**](PoliciesAPI.md#CreateAdmissionPolicyApiV1PoliciesPost) | **Post** /api/v1/policies | Create Admission Policy
[**EvaluateAdmissionPoliciesApiV1PoliciesEvaluatePost**](PoliciesAPI.md#EvaluateAdmissionPoliciesApiV1PoliciesEvaluatePost) | **Post** /api/v1/policies/evaluate | Evaluate Admission Policies
[**GetAdmissionPolicyApiV1PoliciesPolicyKeyGet**](PoliciesAPI.md#GetAdmissionPolicyApiV1PoliciesPolicyKeyGet) | **Get** /api/v1/policies/{policy_key} | Get Admission Policy
[**ListAdmissionPoliciesApiV1PoliciesGet**](PoliciesAPI.md#ListAdmissionPoliciesApiV1PoliciesGet) | **Get** /api/v1/policies | List Admission Policies
[**ListAdmissionPolicyDecisionsApiV1PoliciesDecisionsGet**](PoliciesAPI.md#ListAdmissionPolicyDecisionsApiV1PoliciesDecisionsGet) | **Get** /api/v1/policies/decisions | List Admission Policy Decisions
[**TestAdmissionPolicyApiV1PoliciesPolicyKeyTestPost**](PoliciesAPI.md#TestAdmissionPolicyApiV1PoliciesPolicyKeyTestPost) | **Post** /api/v1/policies/{policy_key}/test | Test Admission Policy
[**UpdateAdmissionPolicyApiV1PoliciesPolicyKeyPut**](PoliciesAPI.md#UpdateAdmissionPolicyApiV1PoliciesPolicyKeyPut) | **Put** /api/v1/policies/{policy_key} | Update Admission Policy
[**ValidateFlowAdmissionPolicyApiV1PoliciesFlowsValidatePost**](PoliciesAPI.md#ValidateFlowAdmissionPolicyApiV1PoliciesFlowsValidatePost) | **Post** /api/v1/policies/flows/validate | Validate Flow Admission Policy



## CreateAdmissionPolicyApiV1PoliciesPost

> PolicyRevision CreateAdmissionPolicyApiV1PoliciesPost(ctx).PolicyDocument(policyDocument).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Create Admission Policy

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
	policyDocument := *openapiclient.NewPolicyDocument("Name_example", "PolicyKey_example") // PolicyDocument |
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.PoliciesAPI.CreateAdmissionPolicyApiV1PoliciesPost(context.Background()).PolicyDocument(policyDocument).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `PoliciesAPI.CreateAdmissionPolicyApiV1PoliciesPost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `CreateAdmissionPolicyApiV1PoliciesPost`: PolicyRevision
	fmt.Fprintf(os.Stdout, "Response from `PoliciesAPI.CreateAdmissionPolicyApiV1PoliciesPost`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiCreateAdmissionPolicyApiV1PoliciesPostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **policyDocument** | [**PolicyDocument**](PolicyDocument.md) |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**PolicyRevision**](PolicyRevision.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## EvaluateAdmissionPoliciesApiV1PoliciesEvaluatePost

> PolicyDecision EvaluateAdmissionPoliciesApiV1PoliciesEvaluatePost(ctx).PolicyEvaluationRequest(policyEvaluationRequest).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Evaluate Admission Policies

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
	policyEvaluationRequest := *openapiclient.NewPolicyEvaluationRequest(*openapiclient.NewPolicyInput(*openapiclient.NewPolicyActorContext("Display_example", "PrincipalId_example", "PrincipalType_example"), *openapiclient.NewPolicyFlowContext("Id_example", int32(123)), *openapiclient.NewPolicyNamespaceContext("Id_example"), *openapiclient.NewPolicyTenantContext("Id_example")), openapiclient.PolicyStage("VALIDATE")) // PolicyEvaluationRequest |
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.PoliciesAPI.EvaluateAdmissionPoliciesApiV1PoliciesEvaluatePost(context.Background()).PolicyEvaluationRequest(policyEvaluationRequest).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `PoliciesAPI.EvaluateAdmissionPoliciesApiV1PoliciesEvaluatePost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `EvaluateAdmissionPoliciesApiV1PoliciesEvaluatePost`: PolicyDecision
	fmt.Fprintf(os.Stdout, "Response from `PoliciesAPI.EvaluateAdmissionPoliciesApiV1PoliciesEvaluatePost`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiEvaluateAdmissionPoliciesApiV1PoliciesEvaluatePostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **policyEvaluationRequest** | [**PolicyEvaluationRequest**](PolicyEvaluationRequest.md) |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**PolicyDecision**](PolicyDecision.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## GetAdmissionPolicyApiV1PoliciesPolicyKeyGet

> PolicyRevision GetAdmissionPolicyApiV1PoliciesPolicyKeyGet(ctx, policyKey).Revision(revision).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Get Admission Policy

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
	policyKey := "policyKey_example" // string |
	revision := int32(56) // int32 |  (optional)
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.PoliciesAPI.GetAdmissionPolicyApiV1PoliciesPolicyKeyGet(context.Background(), policyKey).Revision(revision).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `PoliciesAPI.GetAdmissionPolicyApiV1PoliciesPolicyKeyGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `GetAdmissionPolicyApiV1PoliciesPolicyKeyGet`: PolicyRevision
	fmt.Fprintf(os.Stdout, "Response from `PoliciesAPI.GetAdmissionPolicyApiV1PoliciesPolicyKeyGet`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**policyKey** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiGetAdmissionPolicyApiV1PoliciesPolicyKeyGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------

 **revision** | **int32** |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**PolicyRevision**](PolicyRevision.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## ListAdmissionPoliciesApiV1PoliciesGet

> []PolicyRevision ListAdmissionPoliciesApiV1PoliciesGet(ctx).Namespace(namespace).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

List Admission Policies

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
	namespace := "namespace_example" // string |  (optional) (default to "default")
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.PoliciesAPI.ListAdmissionPoliciesApiV1PoliciesGet(context.Background()).Namespace(namespace).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `PoliciesAPI.ListAdmissionPoliciesApiV1PoliciesGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `ListAdmissionPoliciesApiV1PoliciesGet`: []PolicyRevision
	fmt.Fprintf(os.Stdout, "Response from `PoliciesAPI.ListAdmissionPoliciesApiV1PoliciesGet`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiListAdmissionPoliciesApiV1PoliciesGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **namespace** | **string** |  | [default to &quot;default&quot;]
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**[]PolicyRevision**](PolicyRevision.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## ListAdmissionPolicyDecisionsApiV1PoliciesDecisionsGet

> []PolicyDecision ListAdmissionPolicyDecisionsApiV1PoliciesDecisionsGet(ctx).Limit(limit).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

List Admission Policy Decisions

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
	resp, r, err := apiClient.PoliciesAPI.ListAdmissionPolicyDecisionsApiV1PoliciesDecisionsGet(context.Background()).Limit(limit).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `PoliciesAPI.ListAdmissionPolicyDecisionsApiV1PoliciesDecisionsGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `ListAdmissionPolicyDecisionsApiV1PoliciesDecisionsGet`: []PolicyDecision
	fmt.Fprintf(os.Stdout, "Response from `PoliciesAPI.ListAdmissionPolicyDecisionsApiV1PoliciesDecisionsGet`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiListAdmissionPolicyDecisionsApiV1PoliciesDecisionsGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **limit** | **int32** |  | [default to 100]
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**[]PolicyDecision**](PolicyDecision.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## TestAdmissionPolicyApiV1PoliciesPolicyKeyTestPost

> PolicyFixtureResult TestAdmissionPolicyApiV1PoliciesPolicyKeyTestPost(ctx, policyKey).PolicyFixture(policyFixture).Revision(revision).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Test Admission Policy

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
	policyKey := "policyKey_example" // string |
	policyFixture := *openapiclient.NewPolicyFixture(false, openapiclient.PolicyOutcome("ALLOW"), "Name_example", *openapiclient.NewPolicyEvaluationRequest(*openapiclient.NewPolicyInput(*openapiclient.NewPolicyActorContext("Display_example", "PrincipalId_example", "PrincipalType_example"), *openapiclient.NewPolicyFlowContext("Id_example", int32(123)), *openapiclient.NewPolicyNamespaceContext("Id_example"), *openapiclient.NewPolicyTenantContext("Id_example")), openapiclient.PolicyStage("VALIDATE"))) // PolicyFixture |
	revision := int32(56) // int32 |  (optional)
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.PoliciesAPI.TestAdmissionPolicyApiV1PoliciesPolicyKeyTestPost(context.Background(), policyKey).PolicyFixture(policyFixture).Revision(revision).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `PoliciesAPI.TestAdmissionPolicyApiV1PoliciesPolicyKeyTestPost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `TestAdmissionPolicyApiV1PoliciesPolicyKeyTestPost`: PolicyFixtureResult
	fmt.Fprintf(os.Stdout, "Response from `PoliciesAPI.TestAdmissionPolicyApiV1PoliciesPolicyKeyTestPost`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**policyKey** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiTestAdmissionPolicyApiV1PoliciesPolicyKeyTestPostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------

 **policyFixture** | [**PolicyFixture**](PolicyFixture.md) |  |
 **revision** | **int32** |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**PolicyFixtureResult**](PolicyFixtureResult.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## UpdateAdmissionPolicyApiV1PoliciesPolicyKeyPut

> PolicyRevision UpdateAdmissionPolicyApiV1PoliciesPolicyKeyPut(ctx, policyKey).PolicyDocument(policyDocument).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Update Admission Policy

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
	policyKey := "policyKey_example" // string |
	policyDocument := *openapiclient.NewPolicyDocument("Name_example", "PolicyKey_example") // PolicyDocument |
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.PoliciesAPI.UpdateAdmissionPolicyApiV1PoliciesPolicyKeyPut(context.Background(), policyKey).PolicyDocument(policyDocument).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `PoliciesAPI.UpdateAdmissionPolicyApiV1PoliciesPolicyKeyPut``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `UpdateAdmissionPolicyApiV1PoliciesPolicyKeyPut`: PolicyRevision
	fmt.Fprintf(os.Stdout, "Response from `PoliciesAPI.UpdateAdmissionPolicyApiV1PoliciesPolicyKeyPut`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**policyKey** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiUpdateAdmissionPolicyApiV1PoliciesPolicyKeyPutRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------

 **policyDocument** | [**PolicyDocument**](PolicyDocument.md) |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**PolicyRevision**](PolicyRevision.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## ValidateFlowAdmissionPolicyApiV1PoliciesFlowsValidatePost

> PolicyDecision ValidateFlowAdmissionPolicyApiV1PoliciesFlowsValidatePost(ctx).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Validate Flow Admission Policy

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
	resp, r, err := apiClient.PoliciesAPI.ValidateFlowAdmissionPolicyApiV1PoliciesFlowsValidatePost(context.Background()).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `PoliciesAPI.ValidateFlowAdmissionPolicyApiV1PoliciesFlowsValidatePost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `ValidateFlowAdmissionPolicyApiV1PoliciesFlowsValidatePost`: PolicyDecision
	fmt.Fprintf(os.Stdout, "Response from `PoliciesAPI.ValidateFlowAdmissionPolicyApiV1PoliciesFlowsValidatePost`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiValidateFlowAdmissionPolicyApiV1PoliciesFlowsValidatePostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**PolicyDecision**](PolicyDecision.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)
