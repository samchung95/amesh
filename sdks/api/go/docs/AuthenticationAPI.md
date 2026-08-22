# \AuthenticationAPI

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**ChangeLocalPasswordApiV1AuthPasswordPost**](AuthenticationAPI.md#ChangeLocalPasswordApiV1AuthPasswordPost) | **Post** /api/v1/auth/password | Change Local Password
[**ListAuthenticationProvidersApiV1AuthProvidersGet**](AuthenticationAPI.md#ListAuthenticationProvidersApiV1AuthProvidersGet) | **Get** /api/v1/auth/providers | List Authentication Providers
[**LoginApiV1AuthLoginPost**](AuthenticationAPI.md#LoginApiV1AuthLoginPost) | **Post** /api/v1/auth/login | Login
[**LogoutAllApiV1AuthLogoutAllPost**](AuthenticationAPI.md#LogoutAllApiV1AuthLogoutAllPost) | **Post** /api/v1/auth/logout-all | Logout All
[**LogoutApiV1AuthLogoutPost**](AuthenticationAPI.md#LogoutApiV1AuthLogoutPost) | **Post** /api/v1/auth/logout | Logout
[**RevokePrincipalSessionsApiV1AdminPrincipalsPrincipalIdSessionsDelete**](AuthenticationAPI.md#RevokePrincipalSessionsApiV1AdminPrincipalsPrincipalIdSessionsDelete) | **Delete** /api/v1/admin/principals/{principal_id}/sessions | Revoke Principal Sessions
[**SetLocalPasswordApiV1AdminPrincipalsPrincipalIdLocalPasswordPut**](AuthenticationAPI.md#SetLocalPasswordApiV1AdminPrincipalsPrincipalIdLocalPasswordPut) | **Put** /api/v1/admin/principals/{principal_id}/local-password | Set Local Password



## ChangeLocalPasswordApiV1AuthPasswordPost

> RevokedSessionsResponse ChangeLocalPasswordApiV1AuthPasswordPost(ctx).ChangeLocalPasswordRequest(changeLocalPasswordRequest).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).Execute()

Change Local Password

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
	changeLocalPasswordRequest := *openapiclient.NewChangeLocalPasswordRequest("CurrentPassword_example", "Identifier_example", "NewPassword_example") // ChangeLocalPasswordRequest |
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.AuthenticationAPI.ChangeLocalPasswordApiV1AuthPasswordPost(context.Background()).ChangeLocalPasswordRequest(changeLocalPasswordRequest).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `AuthenticationAPI.ChangeLocalPasswordApiV1AuthPasswordPost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `ChangeLocalPasswordApiV1AuthPasswordPost`: RevokedSessionsResponse
	fmt.Fprintf(os.Stdout, "Response from `AuthenticationAPI.ChangeLocalPasswordApiV1AuthPasswordPost`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiChangeLocalPasswordApiV1AuthPasswordPostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **changeLocalPasswordRequest** | [**ChangeLocalPasswordRequest**](ChangeLocalPasswordRequest.md) |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |

### Return type

[**RevokedSessionsResponse**](RevokedSessionsResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## ListAuthenticationProvidersApiV1AuthProvidersGet

> []AuthenticationProviderDescriptor ListAuthenticationProvidersApiV1AuthProvidersGet(ctx).Execute()

List Authentication Providers

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
	resp, r, err := apiClient.AuthenticationAPI.ListAuthenticationProvidersApiV1AuthProvidersGet(context.Background()).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `AuthenticationAPI.ListAuthenticationProvidersApiV1AuthProvidersGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `ListAuthenticationProvidersApiV1AuthProvidersGet`: []AuthenticationProviderDescriptor
	fmt.Fprintf(os.Stdout, "Response from `AuthenticationAPI.ListAuthenticationProvidersApiV1AuthProvidersGet`: %v\n", resp)
}
```

### Path Parameters

This endpoint does not need any parameter.

### Other Parameters

Other parameters are passed through a pointer to a apiListAuthenticationProvidersApiV1AuthProvidersGetRequest struct via the builder pattern


### Return type

[**[]AuthenticationProviderDescriptor**](AuthenticationProviderDescriptor.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## LoginApiV1AuthLoginPost

> LoginResponse LoginApiV1AuthLoginPost(ctx).LoginRequest(loginRequest).Execute()

Login

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
	loginRequest := *openapiclient.NewLoginRequest("Identifier_example", "Password_example") // LoginRequest |

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.AuthenticationAPI.LoginApiV1AuthLoginPost(context.Background()).LoginRequest(loginRequest).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `AuthenticationAPI.LoginApiV1AuthLoginPost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `LoginApiV1AuthLoginPost`: LoginResponse
	fmt.Fprintf(os.Stdout, "Response from `AuthenticationAPI.LoginApiV1AuthLoginPost`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiLoginApiV1AuthLoginPostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **loginRequest** | [**LoginRequest**](LoginRequest.md) |  |

### Return type

[**LoginResponse**](LoginResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## LogoutAllApiV1AuthLogoutAllPost

> RevokedSessionsResponse LogoutAllApiV1AuthLogoutAllPost(ctx).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).Execute()

Logout All

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
	resp, r, err := apiClient.AuthenticationAPI.LogoutAllApiV1AuthLogoutAllPost(context.Background()).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `AuthenticationAPI.LogoutAllApiV1AuthLogoutAllPost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `LogoutAllApiV1AuthLogoutAllPost`: RevokedSessionsResponse
	fmt.Fprintf(os.Stdout, "Response from `AuthenticationAPI.LogoutAllApiV1AuthLogoutAllPost`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiLogoutAllApiV1AuthLogoutAllPostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |

### Return type

[**RevokedSessionsResponse**](RevokedSessionsResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## LogoutApiV1AuthLogoutPost

> LogoutApiV1AuthLogoutPost(ctx).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).Execute()

Logout

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
	r, err := apiClient.AuthenticationAPI.LogoutApiV1AuthLogoutPost(context.Background()).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `AuthenticationAPI.LogoutApiV1AuthLogoutPost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiLogoutApiV1AuthLogoutPostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |

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


## RevokePrincipalSessionsApiV1AdminPrincipalsPrincipalIdSessionsDelete

> RevokedSessionsResponse RevokePrincipalSessionsApiV1AdminPrincipalsPrincipalIdSessionsDelete(ctx, principalId).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).Execute()

Revoke Principal Sessions

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
	resp, r, err := apiClient.AuthenticationAPI.RevokePrincipalSessionsApiV1AdminPrincipalsPrincipalIdSessionsDelete(context.Background(), principalId).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `AuthenticationAPI.RevokePrincipalSessionsApiV1AdminPrincipalsPrincipalIdSessionsDelete``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `RevokePrincipalSessionsApiV1AdminPrincipalsPrincipalIdSessionsDelete`: RevokedSessionsResponse
	fmt.Fprintf(os.Stdout, "Response from `AuthenticationAPI.RevokePrincipalSessionsApiV1AdminPrincipalsPrincipalIdSessionsDelete`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**principalId** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiRevokePrincipalSessionsApiV1AdminPrincipalsPrincipalIdSessionsDeleteRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------

 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |

### Return type

[**RevokedSessionsResponse**](RevokedSessionsResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## SetLocalPasswordApiV1AdminPrincipalsPrincipalIdLocalPasswordPut

> RevokedSessionsResponse SetLocalPasswordApiV1AdminPrincipalsPrincipalIdLocalPasswordPut(ctx, principalId).SetLocalPasswordRequest(setLocalPasswordRequest).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).Execute()

Set Local Password

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
	setLocalPasswordRequest := *openapiclient.NewSetLocalPasswordRequest("NewPassword_example") // SetLocalPasswordRequest |
	authorization := "authorization_example" // string |  (optional)
	xAmeshCSRF := "xAmeshCSRF_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.AuthenticationAPI.SetLocalPasswordApiV1AdminPrincipalsPrincipalIdLocalPasswordPut(context.Background(), principalId).SetLocalPasswordRequest(setLocalPasswordRequest).Authorization(authorization).XAmeshCSRF(xAmeshCSRF).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `AuthenticationAPI.SetLocalPasswordApiV1AdminPrincipalsPrincipalIdLocalPasswordPut``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `SetLocalPasswordApiV1AdminPrincipalsPrincipalIdLocalPasswordPut`: RevokedSessionsResponse
	fmt.Fprintf(os.Stdout, "Response from `AuthenticationAPI.SetLocalPasswordApiV1AdminPrincipalsPrincipalIdLocalPasswordPut`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**principalId** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiSetLocalPasswordApiV1AdminPrincipalsPrincipalIdLocalPasswordPutRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------

 **setLocalPasswordRequest** | [**SetLocalPasswordRequest**](SetLocalPasswordRequest.md) |  |
 **authorization** | **string** |  |
 **xAmeshCSRF** | **string** |  |

### Return type

[**RevokedSessionsResponse**](RevokedSessionsResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)
