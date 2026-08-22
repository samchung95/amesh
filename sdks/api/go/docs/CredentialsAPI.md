# \CredentialsAPI

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**ExchangeWorkloadCredentialApiV1CredentialsExchangePost**](CredentialsAPI.md#ExchangeWorkloadCredentialApiV1CredentialsExchangePost) | **Post** /api/v1/credentials/exchange | Exchange Workload Credential
[**IssueCredentialApiV1AdminPrincipalsPrincipalIdCredentialsPost**](CredentialsAPI.md#IssueCredentialApiV1AdminPrincipalsPrincipalIdCredentialsPost) | **Post** /api/v1/admin/principals/{principal_id}/credentials | Issue Credential
[**ListCredentialsApiV1AdminPrincipalsPrincipalIdCredentialsGet**](CredentialsAPI.md#ListCredentialsApiV1AdminPrincipalsPrincipalIdCredentialsGet) | **Get** /api/v1/admin/principals/{principal_id}/credentials | List Credentials
[**RevokeAllCredentialsApiV1AdminPrincipalsPrincipalIdCredentialsDelete**](CredentialsAPI.md#RevokeAllCredentialsApiV1AdminPrincipalsPrincipalIdCredentialsDelete) | **Delete** /api/v1/admin/principals/{principal_id}/credentials | Revoke All Credentials
[**RevokeCredentialApiV1AdminCredentialsCredentialIdDelete**](CredentialsAPI.md#RevokeCredentialApiV1AdminCredentialsCredentialIdDelete) | **Delete** /api/v1/admin/credentials/{credential_id} | Revoke Credential
[**RotateCredentialApiV1AdminCredentialsCredentialIdRotatePost**](CredentialsAPI.md#RotateCredentialApiV1AdminCredentialsCredentialIdRotatePost) | **Post** /api/v1/admin/credentials/{credential_id}/rotate | Rotate Credential



## ExchangeWorkloadCredentialApiV1CredentialsExchangePost

> IssuedCredentialResponse ExchangeWorkloadCredentialApiV1CredentialsExchangePost(ctx).ExchangeCredentialRequest(exchangeCredentialRequest).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).Execute()

Exchange Workload Credential

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
	exchangeCredentialRequest := *openapiclient.NewExchangeCredentialRequest("Audience_example", int32(123), []string{"Scopes_example"}) // ExchangeCredentialRequest |
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.CredentialsAPI.ExchangeWorkloadCredentialApiV1CredentialsExchangePost(context.Background()).ExchangeCredentialRequest(exchangeCredentialRequest).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `CredentialsAPI.ExchangeWorkloadCredentialApiV1CredentialsExchangePost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `ExchangeWorkloadCredentialApiV1CredentialsExchangePost`: IssuedCredentialResponse
	fmt.Fprintf(os.Stdout, "Response from `CredentialsAPI.ExchangeWorkloadCredentialApiV1CredentialsExchangePost`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiExchangeWorkloadCredentialApiV1CredentialsExchangePostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **exchangeCredentialRequest** | [**ExchangeCredentialRequest**](ExchangeCredentialRequest.md) |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |

### Return type

[**IssuedCredentialResponse**](IssuedCredentialResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## IssueCredentialApiV1AdminPrincipalsPrincipalIdCredentialsPost

> IssuedCredentialResponse IssueCredentialApiV1AdminPrincipalsPrincipalIdCredentialsPost(ctx, principalId).IssueCredentialRequest(issueCredentialRequest).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).Execute()

Issue Credential

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
	principalId := "38400000-8cf0-11bd-b23e-10b96e4ef00d" // string |
	issueCredentialRequest := *openapiclient.NewIssueCredentialRequest(time.Now(), "Name_example", []string{"Scopes_example"}) // IssueCredentialRequest |
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.CredentialsAPI.IssueCredentialApiV1AdminPrincipalsPrincipalIdCredentialsPost(context.Background(), principalId).IssueCredentialRequest(issueCredentialRequest).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `CredentialsAPI.IssueCredentialApiV1AdminPrincipalsPrincipalIdCredentialsPost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `IssueCredentialApiV1AdminPrincipalsPrincipalIdCredentialsPost`: IssuedCredentialResponse
	fmt.Fprintf(os.Stdout, "Response from `CredentialsAPI.IssueCredentialApiV1AdminPrincipalsPrincipalIdCredentialsPost`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**principalId** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiIssueCredentialApiV1AdminPrincipalsPrincipalIdCredentialsPostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------

 **issueCredentialRequest** | [**IssueCredentialRequest**](IssueCredentialRequest.md) |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |

### Return type

[**IssuedCredentialResponse**](IssuedCredentialResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## ListCredentialsApiV1AdminPrincipalsPrincipalIdCredentialsGet

> []CredentialMetadata ListCredentialsApiV1AdminPrincipalsPrincipalIdCredentialsGet(ctx, principalId).Cursor(cursor).Limit(limit).Filter(filter).Sort(sort).Fields(fields).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).Execute()

List Credentials

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
	principalId := "38400000-8cf0-11bd-b23e-10b96e4ef00d" // string |
	cursor := "cursor_example" // string | Opaque cursor from the prior page (optional)
	limit := int32(56) // int32 |  (optional)
	filter := []string{"Inner_example"} // []string | Repeatable top-level equality filter in field=value form (optional)
	sort := "sort_example" // string | Comma-separated top-level fields; prefix descending fields with - (optional)
	fields := "fields_example" // string | Comma-separated top-level response fields (optional)
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.CredentialsAPI.ListCredentialsApiV1AdminPrincipalsPrincipalIdCredentialsGet(context.Background(), principalId).Cursor(cursor).Limit(limit).Filter(filter).Sort(sort).Fields(fields).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `CredentialsAPI.ListCredentialsApiV1AdminPrincipalsPrincipalIdCredentialsGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `ListCredentialsApiV1AdminPrincipalsPrincipalIdCredentialsGet`: []CredentialMetadata
	fmt.Fprintf(os.Stdout, "Response from `CredentialsAPI.ListCredentialsApiV1AdminPrincipalsPrincipalIdCredentialsGet`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**principalId** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiListCredentialsApiV1AdminPrincipalsPrincipalIdCredentialsGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------

 **cursor** | **string** | Opaque cursor from the prior page |
 **limit** | **int32** |  |
 **filter** | **[]string** | Repeatable top-level equality filter in field&#x3D;value form |
 **sort** | **string** | Comma-separated top-level fields; prefix descending fields with - |
 **fields** | **string** | Comma-separated top-level response fields |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |

### Return type

[**[]CredentialMetadata**](CredentialMetadata.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## RevokeAllCredentialsApiV1AdminPrincipalsPrincipalIdCredentialsDelete

> RevokedCredentialsResponse RevokeAllCredentialsApiV1AdminPrincipalsPrincipalIdCredentialsDelete(ctx, principalId).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).Execute()

Revoke All Credentials

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
	principalId := "38400000-8cf0-11bd-b23e-10b96e4ef00d" // string |
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.CredentialsAPI.RevokeAllCredentialsApiV1AdminPrincipalsPrincipalIdCredentialsDelete(context.Background(), principalId).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `CredentialsAPI.RevokeAllCredentialsApiV1AdminPrincipalsPrincipalIdCredentialsDelete``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `RevokeAllCredentialsApiV1AdminPrincipalsPrincipalIdCredentialsDelete`: RevokedCredentialsResponse
	fmt.Fprintf(os.Stdout, "Response from `CredentialsAPI.RevokeAllCredentialsApiV1AdminPrincipalsPrincipalIdCredentialsDelete`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**principalId** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiRevokeAllCredentialsApiV1AdminPrincipalsPrincipalIdCredentialsDeleteRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------

 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |

### Return type

[**RevokedCredentialsResponse**](RevokedCredentialsResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## RevokeCredentialApiV1AdminCredentialsCredentialIdDelete

> RevokedCredentialsResponse RevokeCredentialApiV1AdminCredentialsCredentialIdDelete(ctx, credentialId).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).Execute()

Revoke Credential

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
	credentialId := "38400000-8cf0-11bd-b23e-10b96e4ef00d" // string |
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.CredentialsAPI.RevokeCredentialApiV1AdminCredentialsCredentialIdDelete(context.Background(), credentialId).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `CredentialsAPI.RevokeCredentialApiV1AdminCredentialsCredentialIdDelete``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `RevokeCredentialApiV1AdminCredentialsCredentialIdDelete`: RevokedCredentialsResponse
	fmt.Fprintf(os.Stdout, "Response from `CredentialsAPI.RevokeCredentialApiV1AdminCredentialsCredentialIdDelete`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**credentialId** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiRevokeCredentialApiV1AdminCredentialsCredentialIdDeleteRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------

 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |

### Return type

[**RevokedCredentialsResponse**](RevokedCredentialsResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## RotateCredentialApiV1AdminCredentialsCredentialIdRotatePost

> IssuedCredentialResponse RotateCredentialApiV1AdminCredentialsCredentialIdRotatePost(ctx, credentialId).RotateCredentialRequest(rotateCredentialRequest).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).Execute()

Rotate Credential

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
	credentialId := "38400000-8cf0-11bd-b23e-10b96e4ef00d" // string |
	rotateCredentialRequest := *openapiclient.NewRotateCredentialRequest() // RotateCredentialRequest |
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.CredentialsAPI.RotateCredentialApiV1AdminCredentialsCredentialIdRotatePost(context.Background(), credentialId).RotateCredentialRequest(rotateCredentialRequest).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `CredentialsAPI.RotateCredentialApiV1AdminCredentialsCredentialIdRotatePost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `RotateCredentialApiV1AdminCredentialsCredentialIdRotatePost`: IssuedCredentialResponse
	fmt.Fprintf(os.Stdout, "Response from `CredentialsAPI.RotateCredentialApiV1AdminCredentialsCredentialIdRotatePost`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**credentialId** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiRotateCredentialApiV1AdminCredentialsCredentialIdRotatePostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------

 **rotateCredentialRequest** | [**RotateCredentialRequest**](RotateCredentialRequest.md) |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |

### Return type

[**IssuedCredentialResponse**](IssuedCredentialResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)
