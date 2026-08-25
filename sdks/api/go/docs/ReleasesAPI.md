# \ReleasesAPI

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**ApplyPolicyApiV1ReleasesPoliciesPolicyIdApplyPost**](ReleasesAPI.md#ApplyPolicyApiV1ReleasesPoliciesPolicyIdApplyPost) | **Post** /api/v1/releases/policies/{policy_id}/apply | Apply Policy
[**CreatePolicyApiV1ReleasesPoliciesPost**](ReleasesAPI.md#CreatePolicyApiV1ReleasesPoliciesPost) | **Post** /api/v1/releases/policies | Create Policy
[**KillSwitchApiV1ReleasesTargetKindTargetKeyKillSwitchPost**](ReleasesAPI.md#KillSwitchApiV1ReleasesTargetKindTargetKeyKillSwitchPost) | **Post** /api/v1/releases/{target_kind}/{target_key}/kill-switch | Kill Switch
[**PreviewPolicyApiV1ReleasesPoliciesPolicyIdPreviewPost**](ReleasesAPI.md#PreviewPolicyApiV1ReleasesPoliciesPolicyIdPreviewPost) | **Post** /api/v1/releases/policies/{policy_id}/preview | Preview Policy
[**RecordEvidenceApiV1ReleasesEvidencePost**](ReleasesAPI.md#RecordEvidenceApiV1ReleasesEvidencePost) | **Post** /api/v1/releases/evidence | Record Evidence
[**RollbackApiV1ReleasesTargetKindTargetKeyRollbackPost**](ReleasesAPI.md#RollbackApiV1ReleasesTargetKindTargetKeyRollbackPost) | **Post** /api/v1/releases/{target_kind}/{target_key}/rollback | Rollback
[**TargetHistoryApiV1ReleasesTargetKindTargetKeyHistoryGet**](ReleasesAPI.md#TargetHistoryApiV1ReleasesTargetKindTargetKeyHistoryGet) | **Get** /api/v1/releases/{target_kind}/{target_key}/history | Target History
[**TargetStateApiV1ReleasesTargetKindTargetKeyGet**](ReleasesAPI.md#TargetStateApiV1ReleasesTargetKindTargetKeyGet) | **Get** /api/v1/releases/{target_kind}/{target_key} | Target State



## ApplyPolicyApiV1ReleasesPoliciesPolicyIdApplyPost

> interface{} ApplyPolicyApiV1ReleasesPoliciesPolicyIdApplyPost(ctx, policyId).PromotionApplyRequest(promotionApplyRequest).XAmeshTenant(xAmeshTenant).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).Execute()

Apply Policy

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
	policyId := "38400000-8cf0-11bd-b23e-10b96e4ef00d" // string |
	promotionApplyRequest := *openapiclient.NewPromotionApplyRequest(int32(123), "Reason_example") // PromotionApplyRequest |
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.ReleasesAPI.ApplyPolicyApiV1ReleasesPoliciesPolicyIdApplyPost(context.Background(), policyId).PromotionApplyRequest(promotionApplyRequest).XAmeshTenant(xAmeshTenant).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `ReleasesAPI.ApplyPolicyApiV1ReleasesPoliciesPolicyIdApplyPost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `ApplyPolicyApiV1ReleasesPoliciesPolicyIdApplyPost`: interface{}
	fmt.Fprintf(os.Stdout, "Response from `ReleasesAPI.ApplyPolicyApiV1ReleasesPoliciesPolicyIdApplyPost`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**policyId** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiApplyPolicyApiV1ReleasesPoliciesPolicyIdApplyPostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------

 **promotionApplyRequest** | [**PromotionApplyRequest**](PromotionApplyRequest.md) |  |
 **xAmeshTenant** | **string** |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |

### Return type

**interface{}**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## CreatePolicyApiV1ReleasesPoliciesPost

> PromotionPolicyOutput CreatePolicyApiV1ReleasesPoliciesPost(ctx).PromotionPolicyInput(promotionPolicyInput).XAmeshTenant(xAmeshTenant).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).Execute()

Create Policy

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
	promotionPolicyInput := *openapiclient.NewPromotionPolicyInput("ConfigurationDigest_example", "CreatedBy_example", "TargetKey_example", openapiclient.PromotionTargetKind("WORKFLOW"), int32(123), "TenantId_example") // PromotionPolicyInput |
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.ReleasesAPI.CreatePolicyApiV1ReleasesPoliciesPost(context.Background()).PromotionPolicyInput(promotionPolicyInput).XAmeshTenant(xAmeshTenant).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `ReleasesAPI.CreatePolicyApiV1ReleasesPoliciesPost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `CreatePolicyApiV1ReleasesPoliciesPost`: PromotionPolicyOutput
	fmt.Fprintf(os.Stdout, "Response from `ReleasesAPI.CreatePolicyApiV1ReleasesPoliciesPost`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiCreatePolicyApiV1ReleasesPoliciesPostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **promotionPolicyInput** | [**PromotionPolicyInput**](PromotionPolicyInput.md) |  |
 **xAmeshTenant** | **string** |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |

### Return type

[**PromotionPolicyOutput**](PromotionPolicyOutput.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## KillSwitchApiV1ReleasesTargetKindTargetKeyKillSwitchPost

> interface{} KillSwitchApiV1ReleasesTargetKindTargetKeyKillSwitchPost(ctx, targetKind, targetKey).PromotionKillSwitchRequest(promotionKillSwitchRequest).XAmeshTenant(xAmeshTenant).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).Execute()

Kill Switch

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
	targetKind := openapiclient.PromotionTargetKind("WORKFLOW") // PromotionTargetKind |
	targetKey := "targetKey_example" // string |
	promotionKillSwitchRequest := *openapiclient.NewPromotionKillSwitchRequest(int32(123), "Reason_example") // PromotionKillSwitchRequest |
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.ReleasesAPI.KillSwitchApiV1ReleasesTargetKindTargetKeyKillSwitchPost(context.Background(), targetKind, targetKey).PromotionKillSwitchRequest(promotionKillSwitchRequest).XAmeshTenant(xAmeshTenant).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `ReleasesAPI.KillSwitchApiV1ReleasesTargetKindTargetKeyKillSwitchPost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `KillSwitchApiV1ReleasesTargetKindTargetKeyKillSwitchPost`: interface{}
	fmt.Fprintf(os.Stdout, "Response from `ReleasesAPI.KillSwitchApiV1ReleasesTargetKindTargetKeyKillSwitchPost`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**targetKind** | [**PromotionTargetKind**](.md) |  |
**targetKey** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiKillSwitchApiV1ReleasesTargetKindTargetKeyKillSwitchPostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------


 **promotionKillSwitchRequest** | [**PromotionKillSwitchRequest**](PromotionKillSwitchRequest.md) |  |
 **xAmeshTenant** | **string** |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |

### Return type

**interface{}**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## PreviewPolicyApiV1ReleasesPoliciesPolicyIdPreviewPost

> interface{} PreviewPolicyApiV1ReleasesPoliciesPolicyIdPreviewPost(ctx, policyId).XAmeshTenant(xAmeshTenant).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).PromotionPreviewRequest(promotionPreviewRequest).Execute()

Preview Policy

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
	policyId := "38400000-8cf0-11bd-b23e-10b96e4ef00d" // string |
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	promotionPreviewRequest := *openapiclient.NewPromotionPreviewRequest() // PromotionPreviewRequest |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.ReleasesAPI.PreviewPolicyApiV1ReleasesPoliciesPolicyIdPreviewPost(context.Background(), policyId).XAmeshTenant(xAmeshTenant).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).PromotionPreviewRequest(promotionPreviewRequest).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `ReleasesAPI.PreviewPolicyApiV1ReleasesPoliciesPolicyIdPreviewPost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `PreviewPolicyApiV1ReleasesPoliciesPolicyIdPreviewPost`: interface{}
	fmt.Fprintf(os.Stdout, "Response from `ReleasesAPI.PreviewPolicyApiV1ReleasesPoliciesPolicyIdPreviewPost`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**policyId** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiPreviewPolicyApiV1ReleasesPoliciesPolicyIdPreviewPostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------

 **xAmeshTenant** | **string** |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **promotionPreviewRequest** | [**PromotionPreviewRequest**](PromotionPreviewRequest.md) |  |

### Return type

**interface{}**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## RecordEvidenceApiV1ReleasesEvidencePost

> EvidenceArtifact RecordEvidenceApiV1ReleasesEvidencePost(ctx).EvidenceArtifact(evidenceArtifact).XAmeshTenant(xAmeshTenant).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).Execute()

Record Evidence

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
	evidenceArtifact := *openapiclient.NewEvidenceArtifact(time.Now(), "ConfigurationDigest_example", "Digest_example", "Key_example", openapiclient.PromotionEvidenceKind("TEST"), false, "TenantId_example") // EvidenceArtifact |
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.ReleasesAPI.RecordEvidenceApiV1ReleasesEvidencePost(context.Background()).EvidenceArtifact(evidenceArtifact).XAmeshTenant(xAmeshTenant).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `ReleasesAPI.RecordEvidenceApiV1ReleasesEvidencePost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `RecordEvidenceApiV1ReleasesEvidencePost`: EvidenceArtifact
	fmt.Fprintf(os.Stdout, "Response from `ReleasesAPI.RecordEvidenceApiV1ReleasesEvidencePost`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiRecordEvidenceApiV1ReleasesEvidencePostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **evidenceArtifact** | [**EvidenceArtifact**](EvidenceArtifact.md) |  |
 **xAmeshTenant** | **string** |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |

### Return type

[**EvidenceArtifact**](EvidenceArtifact.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## RollbackApiV1ReleasesTargetKindTargetKeyRollbackPost

> interface{} RollbackApiV1ReleasesTargetKindTargetKeyRollbackPost(ctx, targetKind, targetKey).PromotionRollbackRequest(promotionRollbackRequest).XAmeshTenant(xAmeshTenant).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).Execute()

Rollback

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
	targetKind := openapiclient.PromotionTargetKind("WORKFLOW") // PromotionTargetKind |
	targetKey := "targetKey_example" // string |
	promotionRollbackRequest := *openapiclient.NewPromotionRollbackRequest(int32(123), "Reason_example", int32(123)) // PromotionRollbackRequest |
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.ReleasesAPI.RollbackApiV1ReleasesTargetKindTargetKeyRollbackPost(context.Background(), targetKind, targetKey).PromotionRollbackRequest(promotionRollbackRequest).XAmeshTenant(xAmeshTenant).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `ReleasesAPI.RollbackApiV1ReleasesTargetKindTargetKeyRollbackPost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `RollbackApiV1ReleasesTargetKindTargetKeyRollbackPost`: interface{}
	fmt.Fprintf(os.Stdout, "Response from `ReleasesAPI.RollbackApiV1ReleasesTargetKindTargetKeyRollbackPost`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**targetKind** | [**PromotionTargetKind**](.md) |  |
**targetKey** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiRollbackApiV1ReleasesTargetKindTargetKeyRollbackPostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------


 **promotionRollbackRequest** | [**PromotionRollbackRequest**](PromotionRollbackRequest.md) |  |
 **xAmeshTenant** | **string** |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |

### Return type

**interface{}**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## TargetHistoryApiV1ReleasesTargetKindTargetKeyHistoryGet

> interface{} TargetHistoryApiV1ReleasesTargetKindTargetKeyHistoryGet(ctx, targetKind, targetKey).XAmeshTenant(xAmeshTenant).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).Execute()

Target History

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
	targetKind := openapiclient.PromotionTargetKind("WORKFLOW") // PromotionTargetKind |
	targetKey := "targetKey_example" // string |
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.ReleasesAPI.TargetHistoryApiV1ReleasesTargetKindTargetKeyHistoryGet(context.Background(), targetKind, targetKey).XAmeshTenant(xAmeshTenant).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `ReleasesAPI.TargetHistoryApiV1ReleasesTargetKindTargetKeyHistoryGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `TargetHistoryApiV1ReleasesTargetKindTargetKeyHistoryGet`: interface{}
	fmt.Fprintf(os.Stdout, "Response from `ReleasesAPI.TargetHistoryApiV1ReleasesTargetKindTargetKeyHistoryGet`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**targetKind** | [**PromotionTargetKind**](.md) |  |
**targetKey** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiTargetHistoryApiV1ReleasesTargetKindTargetKeyHistoryGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------


 **xAmeshTenant** | **string** |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |

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


## TargetStateApiV1ReleasesTargetKindTargetKeyGet

> interface{} TargetStateApiV1ReleasesTargetKindTargetKeyGet(ctx, targetKind, targetKey).XAmeshTenant(xAmeshTenant).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).Execute()

Target State

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
	targetKind := openapiclient.PromotionTargetKind("WORKFLOW") // PromotionTargetKind |
	targetKey := "targetKey_example" // string |
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.ReleasesAPI.TargetStateApiV1ReleasesTargetKindTargetKeyGet(context.Background(), targetKind, targetKey).XAmeshTenant(xAmeshTenant).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `ReleasesAPI.TargetStateApiV1ReleasesTargetKindTargetKeyGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `TargetStateApiV1ReleasesTargetKindTargetKeyGet`: interface{}
	fmt.Fprintf(os.Stdout, "Response from `ReleasesAPI.TargetStateApiV1ReleasesTargetKindTargetKeyGet`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**targetKind** | [**PromotionTargetKind**](.md) |  |
**targetKey** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiTargetStateApiV1ReleasesTargetKindTargetKeyGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------


 **xAmeshTenant** | **string** |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |

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
