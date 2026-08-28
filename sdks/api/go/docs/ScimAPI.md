# \ScimAPI

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**CreateScimGroupScimV2GroupsPost**](ScimAPI.md#CreateScimGroupScimV2GroupsPost) | **Post** /scim/v2/Groups | Create Scim Group
[**CreateScimUserScimV2UsersPost**](ScimAPI.md#CreateScimUserScimV2UsersPost) | **Post** /scim/v2/Users | Create Scim User
[**DeleteScimGroupScimV2GroupsGroupIdDelete**](ScimAPI.md#DeleteScimGroupScimV2GroupsGroupIdDelete) | **Delete** /scim/v2/Groups/{group_id} | Delete Scim Group
[**DeleteScimUserScimV2UsersUserIdDelete**](ScimAPI.md#DeleteScimUserScimV2UsersUserIdDelete) | **Delete** /scim/v2/Users/{user_id} | Delete Scim User
[**GetScimGroupScimV2GroupsGroupIdGet**](ScimAPI.md#GetScimGroupScimV2GroupsGroupIdGet) | **Get** /scim/v2/Groups/{group_id} | Get Scim Group
[**GetScimUserScimV2UsersUserIdGet**](ScimAPI.md#GetScimUserScimV2UsersUserIdGet) | **Get** /scim/v2/Users/{user_id} | Get Scim User
[**ListScimGroupsScimV2GroupsGet**](ScimAPI.md#ListScimGroupsScimV2GroupsGet) | **Get** /scim/v2/Groups | List Scim Groups
[**ListScimUsersScimV2UsersGet**](ScimAPI.md#ListScimUsersScimV2UsersGet) | **Get** /scim/v2/Users | List Scim Users
[**PatchScimGroupScimV2GroupsGroupIdPatch**](ScimAPI.md#PatchScimGroupScimV2GroupsGroupIdPatch) | **Patch** /scim/v2/Groups/{group_id} | Patch Scim Group
[**PatchScimUserScimV2UsersUserIdPatch**](ScimAPI.md#PatchScimUserScimV2UsersUserIdPatch) | **Patch** /scim/v2/Users/{user_id} | Patch Scim User
[**ScimServiceProviderConfigScimV2ServiceProviderConfigGet**](ScimAPI.md#ScimServiceProviderConfigScimV2ServiceProviderConfigGet) | **Get** /scim/v2/ServiceProviderConfig | Scim Service Provider Config



## CreateScimGroupScimV2GroupsPost

> ScimGroupResource CreateScimGroupScimV2GroupsPost(ctx).ScimGroupRequest(scimGroupRequest).Authorization(authorization).Execute()

Create Scim Group

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
	scimGroupRequest := *openapiclient.NewScimGroupRequest("DisplayName_example") // ScimGroupRequest |
	authorization := "authorization_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.ScimAPI.CreateScimGroupScimV2GroupsPost(context.Background()).ScimGroupRequest(scimGroupRequest).Authorization(authorization).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `ScimAPI.CreateScimGroupScimV2GroupsPost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `CreateScimGroupScimV2GroupsPost`: ScimGroupResource
	fmt.Fprintf(os.Stdout, "Response from `ScimAPI.CreateScimGroupScimV2GroupsPost`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiCreateScimGroupScimV2GroupsPostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **scimGroupRequest** | **ScimGroupRequest** |  |
 **authorization** | **string** |  |

### Return type

**ScimGroupResource**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## CreateScimUserScimV2UsersPost

> ScimUserResource CreateScimUserScimV2UsersPost(ctx).ScimUserRequest(scimUserRequest).Authorization(authorization).Execute()

Create Scim User

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
	scimUserRequest := *openapiclient.NewScimUserRequest("UserName_example") // ScimUserRequest |
	authorization := "authorization_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.ScimAPI.CreateScimUserScimV2UsersPost(context.Background()).ScimUserRequest(scimUserRequest).Authorization(authorization).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `ScimAPI.CreateScimUserScimV2UsersPost``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `CreateScimUserScimV2UsersPost`: ScimUserResource
	fmt.Fprintf(os.Stdout, "Response from `ScimAPI.CreateScimUserScimV2UsersPost`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiCreateScimUserScimV2UsersPostRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **scimUserRequest** | **ScimUserRequest** |  |
 **authorization** | **string** |  |

### Return type

**ScimUserResource**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## DeleteScimGroupScimV2GroupsGroupIdDelete

> DeleteScimGroupScimV2GroupsGroupIdDelete(ctx, groupId).Authorization(authorization).Execute()

Delete Scim Group

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
	groupId := "38400000-8cf0-11bd-b23e-10b96e4ef00d" // string |
	authorization := "authorization_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	r, err := apiClient.ScimAPI.DeleteScimGroupScimV2GroupsGroupIdDelete(context.Background(), groupId).Authorization(authorization).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `ScimAPI.DeleteScimGroupScimV2GroupsGroupIdDelete``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**groupId** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiDeleteScimGroupScimV2GroupsGroupIdDeleteRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------

 **authorization** | **string** |  |

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


## DeleteScimUserScimV2UsersUserIdDelete

> DeleteScimUserScimV2UsersUserIdDelete(ctx, userId).Authorization(authorization).Execute()

Delete Scim User

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
	userId := "38400000-8cf0-11bd-b23e-10b96e4ef00d" // string |
	authorization := "authorization_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	r, err := apiClient.ScimAPI.DeleteScimUserScimV2UsersUserIdDelete(context.Background(), userId).Authorization(authorization).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `ScimAPI.DeleteScimUserScimV2UsersUserIdDelete``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**userId** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiDeleteScimUserScimV2UsersUserIdDeleteRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------

 **authorization** | **string** |  |

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


## GetScimGroupScimV2GroupsGroupIdGet

> ScimGroupResource GetScimGroupScimV2GroupsGroupIdGet(ctx, groupId).Authorization(authorization).Execute()

Get Scim Group

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
	groupId := "38400000-8cf0-11bd-b23e-10b96e4ef00d" // string |
	authorization := "authorization_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.ScimAPI.GetScimGroupScimV2GroupsGroupIdGet(context.Background(), groupId).Authorization(authorization).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `ScimAPI.GetScimGroupScimV2GroupsGroupIdGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `GetScimGroupScimV2GroupsGroupIdGet`: ScimGroupResource
	fmt.Fprintf(os.Stdout, "Response from `ScimAPI.GetScimGroupScimV2GroupsGroupIdGet`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**groupId** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiGetScimGroupScimV2GroupsGroupIdGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------

 **authorization** | **string** |  |

### Return type

**ScimGroupResource**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## GetScimUserScimV2UsersUserIdGet

> ScimUserResource GetScimUserScimV2UsersUserIdGet(ctx, userId).Authorization(authorization).Execute()

Get Scim User

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
	userId := "38400000-8cf0-11bd-b23e-10b96e4ef00d" // string |
	authorization := "authorization_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.ScimAPI.GetScimUserScimV2UsersUserIdGet(context.Background(), userId).Authorization(authorization).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `ScimAPI.GetScimUserScimV2UsersUserIdGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `GetScimUserScimV2UsersUserIdGet`: ScimUserResource
	fmt.Fprintf(os.Stdout, "Response from `ScimAPI.GetScimUserScimV2UsersUserIdGet`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**userId** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiGetScimUserScimV2UsersUserIdGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------

 **authorization** | **string** |  |

### Return type

**ScimUserResource**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## ListScimGroupsScimV2GroupsGet

> ScimListResponse ListScimGroupsScimV2GroupsGet(ctx).Filter(filter).StartIndex(startIndex).Count(count).Authorization(authorization).Execute()

List Scim Groups

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
	filter := "filter_example" // string |  (optional)
	startIndex := int32(56) // int32 |  (optional) (default to 1)
	count := int32(56) // int32 |  (optional) (default to 100)
	authorization := "authorization_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.ScimAPI.ListScimGroupsScimV2GroupsGet(context.Background()).Filter(filter).StartIndex(startIndex).Count(count).Authorization(authorization).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `ScimAPI.ListScimGroupsScimV2GroupsGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `ListScimGroupsScimV2GroupsGet`: ScimListResponse
	fmt.Fprintf(os.Stdout, "Response from `ScimAPI.ListScimGroupsScimV2GroupsGet`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiListScimGroupsScimV2GroupsGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **filter** | **string** |  |
 **startIndex** | **int32** |  | [default to 1]
 **count** | **int32** |  | [default to 100]
 **authorization** | **string** |  |

### Return type

**ScimListResponse**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## ListScimUsersScimV2UsersGet

> ScimListResponse ListScimUsersScimV2UsersGet(ctx).Filter(filter).StartIndex(startIndex).Count(count).Authorization(authorization).Execute()

List Scim Users

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
	filter := "filter_example" // string |  (optional)
	startIndex := int32(56) // int32 |  (optional) (default to 1)
	count := int32(56) // int32 |  (optional) (default to 100)
	authorization := "authorization_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.ScimAPI.ListScimUsersScimV2UsersGet(context.Background()).Filter(filter).StartIndex(startIndex).Count(count).Authorization(authorization).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `ScimAPI.ListScimUsersScimV2UsersGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `ListScimUsersScimV2UsersGet`: ScimListResponse
	fmt.Fprintf(os.Stdout, "Response from `ScimAPI.ListScimUsersScimV2UsersGet`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiListScimUsersScimV2UsersGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **filter** | **string** |  |
 **startIndex** | **int32** |  | [default to 1]
 **count** | **int32** |  | [default to 100]
 **authorization** | **string** |  |

### Return type

**ScimListResponse**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## PatchScimGroupScimV2GroupsGroupIdPatch

> ScimGroupResource PatchScimGroupScimV2GroupsGroupIdPatch(ctx, groupId).ScimPatchRequest(scimPatchRequest).Authorization(authorization).Execute()

Patch Scim Group

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
	groupId := "38400000-8cf0-11bd-b23e-10b96e4ef00d" // string |
	scimPatchRequest := *openapiclient.NewScimPatchRequest([]openapiclient.ScimPatchOperation{*openapiclient.NewScimPatchOperation("Op_example")}) // ScimPatchRequest |
	authorization := "authorization_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.ScimAPI.PatchScimGroupScimV2GroupsGroupIdPatch(context.Background(), groupId).ScimPatchRequest(scimPatchRequest).Authorization(authorization).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `ScimAPI.PatchScimGroupScimV2GroupsGroupIdPatch``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `PatchScimGroupScimV2GroupsGroupIdPatch`: ScimGroupResource
	fmt.Fprintf(os.Stdout, "Response from `ScimAPI.PatchScimGroupScimV2GroupsGroupIdPatch`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**groupId** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiPatchScimGroupScimV2GroupsGroupIdPatchRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------

 **scimPatchRequest** | **ScimPatchRequest** |  |
 **authorization** | **string** |  |

### Return type

**ScimGroupResource**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## PatchScimUserScimV2UsersUserIdPatch

> ScimUserResource PatchScimUserScimV2UsersUserIdPatch(ctx, userId).ScimPatchRequest(scimPatchRequest).Authorization(authorization).Execute()

Patch Scim User

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
	userId := "38400000-8cf0-11bd-b23e-10b96e4ef00d" // string |
	scimPatchRequest := *openapiclient.NewScimPatchRequest([]openapiclient.ScimPatchOperation{*openapiclient.NewScimPatchOperation("Op_example")}) // ScimPatchRequest |
	authorization := "authorization_example" // string |  (optional)

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.ScimAPI.PatchScimUserScimV2UsersUserIdPatch(context.Background(), userId).ScimPatchRequest(scimPatchRequest).Authorization(authorization).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `ScimAPI.PatchScimUserScimV2UsersUserIdPatch``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `PatchScimUserScimV2UsersUserIdPatch`: ScimUserResource
	fmt.Fprintf(os.Stdout, "Response from `ScimAPI.PatchScimUserScimV2UsersUserIdPatch`: %v\n", resp)
}
```

### Path Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
**ctx** | **context.Context** | context for authentication, logging, cancellation, deadlines, tracing, etc.
**userId** | **string** |  |

### Other Parameters

Other parameters are passed through a pointer to a apiPatchScimUserScimV2UsersUserIdPatchRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------

 **scimPatchRequest** | **ScimPatchRequest** |  |
 **authorization** | **string** |  |

### Return type

**ScimUserResource**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)


## ScimServiceProviderConfigScimV2ServiceProviderConfigGet

> map[string]*interface{} ScimServiceProviderConfigScimV2ServiceProviderConfigGet(ctx).Authorization(authorization).Execute()

Scim Service Provider Config

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

	configuration := openapiclient.NewConfiguration()
	apiClient := openapiclient.NewAPIClient(configuration)
	resp, r, err := apiClient.ScimAPI.ScimServiceProviderConfigScimV2ServiceProviderConfigGet(context.Background()).Authorization(authorization).Execute()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error when calling `ScimAPI.ScimServiceProviderConfigScimV2ServiceProviderConfigGet``: %v\n", err)
		fmt.Fprintf(os.Stderr, "Full HTTP response: %v\n", r)
	}
	// response from `ScimServiceProviderConfigScimV2ServiceProviderConfigGet`: map[string]*interface{}
	fmt.Fprintf(os.Stdout, "Response from `ScimAPI.ScimServiceProviderConfigScimV2ServiceProviderConfigGet`: %v\n", resp)
}
```

### Path Parameters



### Other Parameters

Other parameters are passed through a pointer to a apiScimServiceProviderConfigScimV2ServiceProviderConfigGetRequest struct via the builder pattern


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **authorization** | **string** |  |

### Return type

**map[string]*interface{}**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints)
[[Back to Model list]](../README.md#documentation-for-models)
[[Back to README]](../README.md)
