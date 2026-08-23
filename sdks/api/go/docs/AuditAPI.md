# \AuditAPI

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**CreateAuditLegalHoldApiV1AuditLegalHoldsPost**](AuditAPI.md#CreateAuditLegalHoldApiV1AuditLegalHoldsPost) | **Post** /api/v1/audit-legal-holds | Create Audit Legal Hold
[**CreateComplianceEvidenceApiV1ComplianceEvidencePost**](AuditAPI.md#CreateComplianceEvidenceApiV1ComplianceEvidencePost) | **Post** /api/v1/compliance-evidence | Create Compliance Evidence
[**CreateObjectAuditExportApiV1AuditExportsPost**](AuditAPI.md#CreateObjectAuditExportApiV1AuditExportsPost) | **Post** /api/v1/audit-exports | Create Object Audit Export
[**CreateObjectCompliancePackageApiV1CompliancePackagesPost**](AuditAPI.md#CreateObjectCompliancePackageApiV1CompliancePackagesPost) | **Post** /api/v1/compliance-packages | Create Object Compliance Package
[**DownloadAuditExportApiV1AuditEventsExportGet**](AuditAPI.md#DownloadAuditExportApiV1AuditEventsExportGet) | **Get** /api/v1/audit-events/export | Download Audit Export
[**DownloadCompliancePackageApiV1CompliancePackagesExportGet**](AuditAPI.md#DownloadCompliancePackageApiV1CompliancePackagesExportGet) | **Get** /api/v1/compliance-packages/export | Download Compliance Package
[**GetAuditPolicyApiV1AuditPolicyGet**](AuditAPI.md#GetAuditPolicyApiV1AuditPolicyGet) | **Get** /api/v1/audit-policy | Get Audit Policy
[**ListAuditEventsApiV1AuditEventsGet**](AuditAPI.md#ListAuditEventsApiV1AuditEventsGet) | **Get** /api/v1/audit-events | List Audit Events
[**ListAuditLegalHoldsApiV1AuditLegalHoldsGet**](AuditAPI.md#ListAuditLegalHoldsApiV1AuditLegalHoldsGet) | **Get** /api/v1/audit-legal-holds | List Audit Legal Holds
[**ListComplianceEvidenceApiV1ComplianceEvidenceGet**](AuditAPI.md#ListComplianceEvidenceApiV1ComplianceEvidenceGet) | **Get** /api/v1/compliance-evidence | List Compliance Evidence
[**PurgeAuditRetentionApiV1AuditRetentionPurgePost**](AuditAPI.md#PurgeAuditRetentionApiV1AuditRetentionPurgePost) | **Post** /api/v1/audit-retention/purge | Purge Audit Retention
[**ReleaseAuditLegalHoldApiV1AuditLegalHoldsHoldIdDelete**](AuditAPI.md#ReleaseAuditLegalHoldApiV1AuditLegalHoldsHoldIdDelete) | **Delete** /api/v1/audit-legal-holds/{hold_id} | Release Audit Legal Hold
[**UpdateAuditPolicyApiV1AuditPolicyPut**](AuditAPI.md#UpdateAuditPolicyApiV1AuditPolicyPut) | **Put** /api/v1/audit-policy | Update Audit Policy
[**VerifyAuditIntegrityApiV1AuditEventsIntegrityGet**](AuditAPI.md#VerifyAuditIntegrityApiV1AuditEventsIntegrityGet) | **Get** /api/v1/audit-events/integrity | Verify Audit Integrity



## CreateAuditLegalHoldApiV1AuditLegalHoldsPost

> AuditLegalHold CreateAuditLegalHoldApiV1AuditLegalHoldsPost(ctx).AuditLegalHoldCreate(auditLegalHoldCreate).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Create Audit Legal Hold

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
	auditLegalHoldCreate := *openapiclient.NewAuditLegalHoldCreate("Name_example", "Reason_example", time.Now()) // AuditLegalHoldCreate |
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.AuditAPI.CreateAuditLegalHoldApiV1AuditLegalHoldsPost(context.Background()).AuditLegalHoldCreate(auditLegalHoldCreate).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `AuditAPI.CreateAuditLegalHoldApiV1AuditLegalHoldsPost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `CreateAuditLegalHoldApiV1AuditLegalHoldsPost`: AuditLegalHold
	fmt.Fprintf(os.Stdout, "Response from `AuditAPI.CreateAuditLegalHoldApiV1AuditLegalHoldsPost`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiCreateAuditLegalHoldApiV1AuditLegalHoldsPostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **auditLegalHoldCreate** | [**AuditLegalHoldCreate**](AuditLegalHoldCreate.md) |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**AuditLegalHold**](AuditLegalHold.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## CreateComplianceEvidenceApiV1ComplianceEvidencePost

> ComplianceEvidenceRecord CreateComplianceEvidenceApiV1ComplianceEvidencePost(ctx).ComplianceEvidenceCreate(complianceEvidenceCreate).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Create Compliance Evidence

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
	complianceEvidenceCreate := *openapiclient.NewComplianceEvidenceCreate(openapiclient.ComplianceEvidenceCategory("ACCESS_REVIEW"), time.Now(), "Source_example", "Title_example") // ComplianceEvidenceCreate |
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.AuditAPI.CreateComplianceEvidenceApiV1ComplianceEvidencePost(context.Background()).ComplianceEvidenceCreate(complianceEvidenceCreate).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `AuditAPI.CreateComplianceEvidenceApiV1ComplianceEvidencePost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `CreateComplianceEvidenceApiV1ComplianceEvidencePost`: ComplianceEvidenceRecord
	fmt.Fprintf(os.Stdout, "Response from `AuditAPI.CreateComplianceEvidenceApiV1ComplianceEvidencePost`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiCreateComplianceEvidenceApiV1ComplianceEvidencePostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **complianceEvidenceCreate** | [**ComplianceEvidenceCreate**](ComplianceEvidenceCreate.md) |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**ComplianceEvidenceRecord**](ComplianceEvidenceRecord.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## CreateObjectAuditExportApiV1AuditExportsPost

> AuditExportReceipt CreateObjectAuditExportApiV1AuditExportsPost(ctx).AuditExportRequest(auditExportRequest).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Create Object Audit Export

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
	auditExportRequest := *openapiclient.NewAuditExportRequest() // AuditExportRequest |
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.AuditAPI.CreateObjectAuditExportApiV1AuditExportsPost(context.Background()).AuditExportRequest(auditExportRequest).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `AuditAPI.CreateObjectAuditExportApiV1AuditExportsPost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `CreateObjectAuditExportApiV1AuditExportsPost`: AuditExportReceipt
	fmt.Fprintf(os.Stdout, "Response from `AuditAPI.CreateObjectAuditExportApiV1AuditExportsPost`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiCreateObjectAuditExportApiV1AuditExportsPostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **auditExportRequest** | [**AuditExportRequest**](AuditExportRequest.md) |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**AuditExportReceipt**](AuditExportReceipt.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## CreateObjectCompliancePackageApiV1CompliancePackagesPost

> AuditExportReceipt CreateObjectCompliancePackageApiV1CompliancePackagesPost(ctx).CompliancePackageRequest(compliancePackageRequest).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Create Object Compliance Package

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
	compliancePackageRequest := *openapiclient.NewCompliancePackageRequest() // CompliancePackageRequest |
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.AuditAPI.CreateObjectCompliancePackageApiV1CompliancePackagesPost(context.Background()).CompliancePackageRequest(compliancePackageRequest).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `AuditAPI.CreateObjectCompliancePackageApiV1CompliancePackagesPost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `CreateObjectCompliancePackageApiV1CompliancePackagesPost`: AuditExportReceipt
	fmt.Fprintf(os.Stdout, "Response from `AuditAPI.CreateObjectCompliancePackageApiV1CompliancePackagesPost`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiCreateObjectCompliancePackageApiV1CompliancePackagesPostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **compliancePackageRequest** | [**CompliancePackageRequest**](CompliancePackageRequest.md) |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**AuditExportReceipt**](AuditExportReceipt.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## DownloadAuditExportApiV1AuditEventsExportGet

> interface{} DownloadAuditExportApiV1AuditEventsExportGet(ctx).Format(format).Limit(limit).Action(action).ResourceType(resourceType).Outcome(outcome).OccurredFrom(occurredFrom).OccurredTo(occurredTo).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Download Audit Export

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
	format := openapiclient.AuditExportFormat("JSON") // AuditExportFormat |  (optional) (default to "NDJSON")
	limit := int32(56) // int32 |  (optional) (default to 10000)
	action := "action_example" // string |  (optional)
	resourceType := "resourceType_example" // string |  (optional)
	outcome := "outcome_example" // string |  (optional)
	occurredFrom := time.Now() // time.Time |  (optional)
	occurredTo := time.Now() // time.Time |  (optional)
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.AuditAPI.DownloadAuditExportApiV1AuditEventsExportGet(context.Background()).Format(format).Limit(limit).Action(action).ResourceType(resourceType).Outcome(outcome).OccurredFrom(occurredFrom).OccurredTo(occurredTo).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `AuditAPI.DownloadAuditExportApiV1AuditEventsExportGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `DownloadAuditExportApiV1AuditEventsExportGet`: interface{}
	fmt.Fprintf(os.Stdout, "Response from `AuditAPI.DownloadAuditExportApiV1AuditEventsExportGet`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiDownloadAuditExportApiV1AuditEventsExportGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **format** | [**AuditExportFormat**](AuditExportFormat.md) |  | [default to &quot;NDJSON&quot;]
 **limit** | **int32** |  | [default to 10000]
 **action** | **string** |  |
 **resourceType** | **string** |  |
 **outcome** | **string** |  |
 **occurredFrom** | **time.Time** |  |
 **occurredTo** | **time.Time** |  |
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


## DownloadCompliancePackageApiV1CompliancePackagesExportGet

> interface{} DownloadCompliancePackageApiV1CompliancePackagesExportGet(ctx).OccurredFrom(occurredFrom).OccurredTo(occurredTo).MaxAuditEvents(maxAuditEvents).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Download Compliance Package

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
	occurredFrom := time.Now() // time.Time |  (optional)
	occurredTo := time.Now() // time.Time |  (optional)
	maxAuditEvents := int32(56) // int32 |  (optional) (default to 10000)
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.AuditAPI.DownloadCompliancePackageApiV1CompliancePackagesExportGet(context.Background()).OccurredFrom(occurredFrom).OccurredTo(occurredTo).MaxAuditEvents(maxAuditEvents).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `AuditAPI.DownloadCompliancePackageApiV1CompliancePackagesExportGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `DownloadCompliancePackageApiV1CompliancePackagesExportGet`: interface{}
	fmt.Fprintf(os.Stdout, "Response from `AuditAPI.DownloadCompliancePackageApiV1CompliancePackagesExportGet`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiDownloadCompliancePackageApiV1CompliancePackagesExportGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **occurredFrom** | **time.Time** |  |
 **occurredTo** | **time.Time** |  |
 **maxAuditEvents** | **int32** |  | [default to 10000]
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


## GetAuditPolicyApiV1AuditPolicyGet

> AuditRetentionPolicy GetAuditPolicyApiV1AuditPolicyGet(ctx).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Get Audit Policy

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
	resp, r, err := apiClient.AuditAPI.GetAuditPolicyApiV1AuditPolicyGet(context.Background()).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `AuditAPI.GetAuditPolicyApiV1AuditPolicyGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `GetAuditPolicyApiV1AuditPolicyGet`: AuditRetentionPolicy
	fmt.Fprintf(os.Stdout, "Response from `AuditAPI.GetAuditPolicyApiV1AuditPolicyGet`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiGetAuditPolicyApiV1AuditPolicyGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**AuditRetentionPolicy**](AuditRetentionPolicy.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## ListAuditEventsApiV1AuditEventsGet

> AuditEventPage ListAuditEventsApiV1AuditEventsGet(ctx).Cursor(cursor).Limit(limit).Action(action).ResourceType(resourceType).Outcome(outcome).OccurredFrom(occurredFrom).OccurredTo(occurredTo).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

List Audit Events

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
	cursor := int32(56) // int32 |  (optional)
	limit := int32(56) // int32 |  (optional) (default to 100)
	action := "action_example" // string |  (optional)
	resourceType := "resourceType_example" // string |  (optional)
	outcome := "outcome_example" // string |  (optional)
	occurredFrom := time.Now() // time.Time |  (optional)
	occurredTo := time.Now() // time.Time |  (optional)
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.AuditAPI.ListAuditEventsApiV1AuditEventsGet(context.Background()).Cursor(cursor).Limit(limit).Action(action).ResourceType(resourceType).Outcome(outcome).OccurredFrom(occurredFrom).OccurredTo(occurredTo).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `AuditAPI.ListAuditEventsApiV1AuditEventsGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `ListAuditEventsApiV1AuditEventsGet`: AuditEventPage
	fmt.Fprintf(os.Stdout, "Response from `AuditAPI.ListAuditEventsApiV1AuditEventsGet`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiListAuditEventsApiV1AuditEventsGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **cursor** | **int32** |  |
 **limit** | **int32** |  | [default to 100]
 **action** | **string** |  |
 **resourceType** | **string** |  |
 **outcome** | **string** |  |
 **occurredFrom** | **time.Time** |  |
 **occurredTo** | **time.Time** |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**AuditEventPage**](AuditEventPage.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## ListAuditLegalHoldsApiV1AuditLegalHoldsGet

> []AuditLegalHold ListAuditLegalHoldsApiV1AuditLegalHoldsGet(ctx).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

List Audit Legal Holds

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
	resp, r, err := apiClient.AuditAPI.ListAuditLegalHoldsApiV1AuditLegalHoldsGet(context.Background()).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `AuditAPI.ListAuditLegalHoldsApiV1AuditLegalHoldsGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `ListAuditLegalHoldsApiV1AuditLegalHoldsGet`: []AuditLegalHold
	fmt.Fprintf(os.Stdout, "Response from `AuditAPI.ListAuditLegalHoldsApiV1AuditLegalHoldsGet`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiListAuditLegalHoldsApiV1AuditLegalHoldsGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**[]AuditLegalHold**](AuditLegalHold.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## ListComplianceEvidenceApiV1ComplianceEvidenceGet

> []ComplianceEvidenceRecord ListComplianceEvidenceApiV1ComplianceEvidenceGet(ctx).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

List Compliance Evidence

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
	resp, r, err := apiClient.AuditAPI.ListComplianceEvidenceApiV1ComplianceEvidenceGet(context.Background()).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `AuditAPI.ListComplianceEvidenceApiV1ComplianceEvidenceGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `ListComplianceEvidenceApiV1ComplianceEvidenceGet`: []ComplianceEvidenceRecord
	fmt.Fprintf(os.Stdout, "Response from `AuditAPI.ListComplianceEvidenceApiV1ComplianceEvidenceGet`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiListComplianceEvidenceApiV1ComplianceEvidenceGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**[]ComplianceEvidenceRecord**](ComplianceEvidenceRecord.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## PurgeAuditRetentionApiV1AuditRetentionPurgePost

> AuditRetentionResult PurgeAuditRetentionApiV1AuditRetentionPurgePost(ctx).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Purge Audit Retention

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
	resp, r, err := apiClient.AuditAPI.PurgeAuditRetentionApiV1AuditRetentionPurgePost(context.Background()).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `AuditAPI.PurgeAuditRetentionApiV1AuditRetentionPurgePost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `PurgeAuditRetentionApiV1AuditRetentionPurgePost`: AuditRetentionResult
	fmt.Fprintf(os.Stdout, "Response from `AuditAPI.PurgeAuditRetentionApiV1AuditRetentionPurgePost`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiPurgeAuditRetentionApiV1AuditRetentionPurgePostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**AuditRetentionResult**](AuditRetentionResult.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## ReleaseAuditLegalHoldApiV1AuditLegalHoldsHoldIdDelete

> AuditLegalHold ReleaseAuditLegalHoldApiV1AuditLegalHoldsHoldIdDelete(ctx, holdId).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Release Audit Legal Hold

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
	holdId := "38400000-8cf0-11bd-b23e-10b96e4ef00d" // string |
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.AuditAPI.ReleaseAuditLegalHoldApiV1AuditLegalHoldsHoldIdDelete(context.Background(), holdId).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `AuditAPI.ReleaseAuditLegalHoldApiV1AuditLegalHoldsHoldIdDelete``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `ReleaseAuditLegalHoldApiV1AuditLegalHoldsHoldIdDelete`: AuditLegalHold
	fmt.Fprintf(os.Stdout, "Response from `AuditAPI.ReleaseAuditLegalHoldApiV1AuditLegalHoldsHoldIdDelete`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**holdId** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiReleaseAuditLegalHoldApiV1AuditLegalHoldsHoldIdDeleteRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------

 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**AuditLegalHold**](AuditLegalHold.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## UpdateAuditPolicyApiV1AuditPolicyPut

> AuditRetentionPolicy UpdateAuditPolicyApiV1AuditPolicyPut(ctx).AuditRetentionPolicyUpdate(auditRetentionPolicyUpdate).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Update Audit Policy

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
	auditRetentionPolicyUpdate := *openapiclient.NewAuditRetentionPolicyUpdate(int32(123)) // AuditRetentionPolicyUpdate |
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)
	xAmeshTenant := "xAmeshTenant_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.AuditAPI.UpdateAuditPolicyApiV1AuditPolicyPut(context.Background()).AuditRetentionPolicyUpdate(auditRetentionPolicyUpdate).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `AuditAPI.UpdateAuditPolicyApiV1AuditPolicyPut``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `UpdateAuditPolicyApiV1AuditPolicyPut`: AuditRetentionPolicy
	fmt.Fprintf(os.Stdout, "Response from `AuditAPI.UpdateAuditPolicyApiV1AuditPolicyPut`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiUpdateAuditPolicyApiV1AuditPolicyPutRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **auditRetentionPolicyUpdate** | [**AuditRetentionPolicyUpdate**](AuditRetentionPolicyUpdate.md) |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**AuditRetentionPolicy**](AuditRetentionPolicy.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## VerifyAuditIntegrityApiV1AuditEventsIntegrityGet

> AuditIntegrityReport VerifyAuditIntegrityApiV1AuditEventsIntegrityGet(ctx).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()

Verify Audit Integrity

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
	resp, r, err := apiClient.AuditAPI.VerifyAuditIntegrityApiV1AuditEventsIntegrityGet(context.Background()).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).XAmeshTenant(xAmeshTenant).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `AuditAPI.VerifyAuditIntegrityApiV1AuditEventsIntegrityGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `VerifyAuditIntegrityApiV1AuditEventsIntegrityGet`: AuditIntegrityReport
	fmt.Fprintf(os.Stdout, "Response from `AuditAPI.VerifyAuditIntegrityApiV1AuditEventsIntegrityGet`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiVerifyAuditIntegrityApiV1AuditEventsIntegrityGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |
 **xAmeshTenant** | **string** |  |

### Return type

[**AuditIntegrityReport**](AuditIntegrityReport.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)
