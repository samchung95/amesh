# ScimApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**createScimGroupScimV2GroupsPost**](ScimApi.md#createScimGroupScimV2GroupsPost) | **POST** /scim/v2/Groups | Create Scim Group |
| [**createScimGroupScimV2GroupsPostWithHttpInfo**](ScimApi.md#createScimGroupScimV2GroupsPostWithHttpInfo) | **POST** /scim/v2/Groups | Create Scim Group |
| [**createScimUserScimV2UsersPost**](ScimApi.md#createScimUserScimV2UsersPost) | **POST** /scim/v2/Users | Create Scim User |
| [**createScimUserScimV2UsersPostWithHttpInfo**](ScimApi.md#createScimUserScimV2UsersPostWithHttpInfo) | **POST** /scim/v2/Users | Create Scim User |
| [**deleteScimGroupScimV2GroupsGroupIdDelete**](ScimApi.md#deleteScimGroupScimV2GroupsGroupIdDelete) | **DELETE** /scim/v2/Groups/{group_id} | Delete Scim Group |
| [**deleteScimGroupScimV2GroupsGroupIdDeleteWithHttpInfo**](ScimApi.md#deleteScimGroupScimV2GroupsGroupIdDeleteWithHttpInfo) | **DELETE** /scim/v2/Groups/{group_id} | Delete Scim Group |
| [**deleteScimUserScimV2UsersUserIdDelete**](ScimApi.md#deleteScimUserScimV2UsersUserIdDelete) | **DELETE** /scim/v2/Users/{user_id} | Delete Scim User |
| [**deleteScimUserScimV2UsersUserIdDeleteWithHttpInfo**](ScimApi.md#deleteScimUserScimV2UsersUserIdDeleteWithHttpInfo) | **DELETE** /scim/v2/Users/{user_id} | Delete Scim User |
| [**getScimGroupScimV2GroupsGroupIdGet**](ScimApi.md#getScimGroupScimV2GroupsGroupIdGet) | **GET** /scim/v2/Groups/{group_id} | Get Scim Group |
| [**getScimGroupScimV2GroupsGroupIdGetWithHttpInfo**](ScimApi.md#getScimGroupScimV2GroupsGroupIdGetWithHttpInfo) | **GET** /scim/v2/Groups/{group_id} | Get Scim Group |
| [**getScimUserScimV2UsersUserIdGet**](ScimApi.md#getScimUserScimV2UsersUserIdGet) | **GET** /scim/v2/Users/{user_id} | Get Scim User |
| [**getScimUserScimV2UsersUserIdGetWithHttpInfo**](ScimApi.md#getScimUserScimV2UsersUserIdGetWithHttpInfo) | **GET** /scim/v2/Users/{user_id} | Get Scim User |
| [**listScimGroupsScimV2GroupsGet**](ScimApi.md#listScimGroupsScimV2GroupsGet) | **GET** /scim/v2/Groups | List Scim Groups |
| [**listScimGroupsScimV2GroupsGetWithHttpInfo**](ScimApi.md#listScimGroupsScimV2GroupsGetWithHttpInfo) | **GET** /scim/v2/Groups | List Scim Groups |
| [**listScimUsersScimV2UsersGet**](ScimApi.md#listScimUsersScimV2UsersGet) | **GET** /scim/v2/Users | List Scim Users |
| [**listScimUsersScimV2UsersGetWithHttpInfo**](ScimApi.md#listScimUsersScimV2UsersGetWithHttpInfo) | **GET** /scim/v2/Users | List Scim Users |
| [**patchScimGroupScimV2GroupsGroupIdPatch**](ScimApi.md#patchScimGroupScimV2GroupsGroupIdPatch) | **PATCH** /scim/v2/Groups/{group_id} | Patch Scim Group |
| [**patchScimGroupScimV2GroupsGroupIdPatchWithHttpInfo**](ScimApi.md#patchScimGroupScimV2GroupsGroupIdPatchWithHttpInfo) | **PATCH** /scim/v2/Groups/{group_id} | Patch Scim Group |
| [**patchScimUserScimV2UsersUserIdPatch**](ScimApi.md#patchScimUserScimV2UsersUserIdPatch) | **PATCH** /scim/v2/Users/{user_id} | Patch Scim User |
| [**patchScimUserScimV2UsersUserIdPatchWithHttpInfo**](ScimApi.md#patchScimUserScimV2UsersUserIdPatchWithHttpInfo) | **PATCH** /scim/v2/Users/{user_id} | Patch Scim User |
| [**scimServiceProviderConfigScimV2ServiceProviderConfigGet**](ScimApi.md#scimServiceProviderConfigScimV2ServiceProviderConfigGet) | **GET** /scim/v2/ServiceProviderConfig | Scim Service Provider Config |
| [**scimServiceProviderConfigScimV2ServiceProviderConfigGetWithHttpInfo**](ScimApi.md#scimServiceProviderConfigScimV2ServiceProviderConfigGetWithHttpInfo) | **GET** /scim/v2/ServiceProviderConfig | Scim Service Provider Config |



## createScimGroupScimV2GroupsPost

> ScimGroupResource createScimGroupScimV2GroupsPost(scimGroupRequest, authorization)

Create Scim Group

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.ScimApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        ScimApi apiInstance = new ScimApi(defaultClient);
        ScimGroupRequest scimGroupRequest = new ScimGroupRequest(); // ScimGroupRequest |
        String authorization = "authorization_example"; // String |
        try {
            ScimGroupResource result = apiInstance.createScimGroupScimV2GroupsPost(scimGroupRequest, authorization);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling ScimApi#createScimGroupScimV2GroupsPost");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Reason: " + e.getResponseBody());
            System.err.println("Response headers: " + e.getResponseHeaders());
            e.printStackTrace();
        }
    }
}
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **scimGroupRequest** | [**ScimGroupRequest**](ScimGroupRequest.md)|  | |
| **authorization** | **String**|  | [optional] |

### Return type

[**ScimGroupResource**](ScimGroupResource.md)


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **201** | Successful Response |  -  |
| **422** | Validation Error |  -  |

## createScimGroupScimV2GroupsPostWithHttpInfo

> ApiResponse<ScimGroupResource> createScimGroupScimV2GroupsPostWithHttpInfo(scimGroupRequest, authorization)

Create Scim Group

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.ScimApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        ScimApi apiInstance = new ScimApi(defaultClient);
        ScimGroupRequest scimGroupRequest = new ScimGroupRequest(); // ScimGroupRequest |
        String authorization = "authorization_example"; // String |
        try {
            ApiResponse<ScimGroupResource> response = apiInstance.createScimGroupScimV2GroupsPostWithHttpInfo(scimGroupRequest, authorization);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling ScimApi#createScimGroupScimV2GroupsPost");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Response headers: " + e.getResponseHeaders());
            System.err.println("Reason: " + e.getResponseBody());
            e.printStackTrace();
        }
    }
}
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **scimGroupRequest** | [**ScimGroupRequest**](ScimGroupRequest.md)|  | |
| **authorization** | **String**|  | [optional] |

### Return type

ApiResponse<[**ScimGroupResource**](ScimGroupResource.md)>


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **201** | Successful Response |  -  |
| **422** | Validation Error |  -  |


## createScimUserScimV2UsersPost

> ScimUserResource createScimUserScimV2UsersPost(scimUserRequest, authorization)

Create Scim User

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.ScimApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        ScimApi apiInstance = new ScimApi(defaultClient);
        ScimUserRequest scimUserRequest = new ScimUserRequest(); // ScimUserRequest |
        String authorization = "authorization_example"; // String |
        try {
            ScimUserResource result = apiInstance.createScimUserScimV2UsersPost(scimUserRequest, authorization);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling ScimApi#createScimUserScimV2UsersPost");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Reason: " + e.getResponseBody());
            System.err.println("Response headers: " + e.getResponseHeaders());
            e.printStackTrace();
        }
    }
}
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **scimUserRequest** | [**ScimUserRequest**](ScimUserRequest.md)|  | |
| **authorization** | **String**|  | [optional] |

### Return type

[**ScimUserResource**](ScimUserResource.md)


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **201** | Successful Response |  -  |
| **422** | Validation Error |  -  |

## createScimUserScimV2UsersPostWithHttpInfo

> ApiResponse<ScimUserResource> createScimUserScimV2UsersPostWithHttpInfo(scimUserRequest, authorization)

Create Scim User

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.ScimApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        ScimApi apiInstance = new ScimApi(defaultClient);
        ScimUserRequest scimUserRequest = new ScimUserRequest(); // ScimUserRequest |
        String authorization = "authorization_example"; // String |
        try {
            ApiResponse<ScimUserResource> response = apiInstance.createScimUserScimV2UsersPostWithHttpInfo(scimUserRequest, authorization);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling ScimApi#createScimUserScimV2UsersPost");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Response headers: " + e.getResponseHeaders());
            System.err.println("Reason: " + e.getResponseBody());
            e.printStackTrace();
        }
    }
}
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **scimUserRequest** | [**ScimUserRequest**](ScimUserRequest.md)|  | |
| **authorization** | **String**|  | [optional] |

### Return type

ApiResponse<[**ScimUserResource**](ScimUserResource.md)>


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **201** | Successful Response |  -  |
| **422** | Validation Error |  -  |


## deleteScimGroupScimV2GroupsGroupIdDelete

> void deleteScimGroupScimV2GroupsGroupIdDelete(groupId, authorization)

Delete Scim Group

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.ScimApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        ScimApi apiInstance = new ScimApi(defaultClient);
        UUID groupId = UUID.randomUUID(); // UUID |
        String authorization = "authorization_example"; // String |
        try {
            apiInstance.deleteScimGroupScimV2GroupsGroupIdDelete(groupId, authorization);
        } catch (ApiException e) {
            System.err.println("Exception when calling ScimApi#deleteScimGroupScimV2GroupsGroupIdDelete");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Reason: " + e.getResponseBody());
            System.err.println("Response headers: " + e.getResponseHeaders());
            e.printStackTrace();
        }
    }
}
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **groupId** | **UUID**|  | |
| **authorization** | **String**|  | [optional] |

### Return type


null (empty response body)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **204** | Successful Response |  -  |
| **422** | Validation Error |  -  |

## deleteScimGroupScimV2GroupsGroupIdDeleteWithHttpInfo

> ApiResponse<Void> deleteScimGroupScimV2GroupsGroupIdDeleteWithHttpInfo(groupId, authorization)

Delete Scim Group

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.ScimApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        ScimApi apiInstance = new ScimApi(defaultClient);
        UUID groupId = UUID.randomUUID(); // UUID |
        String authorization = "authorization_example"; // String |
        try {
            ApiResponse<Void> response = apiInstance.deleteScimGroupScimV2GroupsGroupIdDeleteWithHttpInfo(groupId, authorization);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
        } catch (ApiException e) {
            System.err.println("Exception when calling ScimApi#deleteScimGroupScimV2GroupsGroupIdDelete");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Response headers: " + e.getResponseHeaders());
            System.err.println("Reason: " + e.getResponseBody());
            e.printStackTrace();
        }
    }
}
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **groupId** | **UUID**|  | |
| **authorization** | **String**|  | [optional] |

### Return type


ApiResponse<Void>

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **204** | Successful Response |  -  |
| **422** | Validation Error |  -  |


## deleteScimUserScimV2UsersUserIdDelete

> void deleteScimUserScimV2UsersUserIdDelete(userId, authorization)

Delete Scim User

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.ScimApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        ScimApi apiInstance = new ScimApi(defaultClient);
        UUID userId = UUID.randomUUID(); // UUID |
        String authorization = "authorization_example"; // String |
        try {
            apiInstance.deleteScimUserScimV2UsersUserIdDelete(userId, authorization);
        } catch (ApiException e) {
            System.err.println("Exception when calling ScimApi#deleteScimUserScimV2UsersUserIdDelete");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Reason: " + e.getResponseBody());
            System.err.println("Response headers: " + e.getResponseHeaders());
            e.printStackTrace();
        }
    }
}
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **userId** | **UUID**|  | |
| **authorization** | **String**|  | [optional] |

### Return type


null (empty response body)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **204** | Successful Response |  -  |
| **422** | Validation Error |  -  |

## deleteScimUserScimV2UsersUserIdDeleteWithHttpInfo

> ApiResponse<Void> deleteScimUserScimV2UsersUserIdDeleteWithHttpInfo(userId, authorization)

Delete Scim User

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.ScimApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        ScimApi apiInstance = new ScimApi(defaultClient);
        UUID userId = UUID.randomUUID(); // UUID |
        String authorization = "authorization_example"; // String |
        try {
            ApiResponse<Void> response = apiInstance.deleteScimUserScimV2UsersUserIdDeleteWithHttpInfo(userId, authorization);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
        } catch (ApiException e) {
            System.err.println("Exception when calling ScimApi#deleteScimUserScimV2UsersUserIdDelete");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Response headers: " + e.getResponseHeaders());
            System.err.println("Reason: " + e.getResponseBody());
            e.printStackTrace();
        }
    }
}
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **userId** | **UUID**|  | |
| **authorization** | **String**|  | [optional] |

### Return type


ApiResponse<Void>

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **204** | Successful Response |  -  |
| **422** | Validation Error |  -  |


## getScimGroupScimV2GroupsGroupIdGet

> ScimGroupResource getScimGroupScimV2GroupsGroupIdGet(groupId, authorization)

Get Scim Group

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.ScimApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        ScimApi apiInstance = new ScimApi(defaultClient);
        UUID groupId = UUID.randomUUID(); // UUID |
        String authorization = "authorization_example"; // String |
        try {
            ScimGroupResource result = apiInstance.getScimGroupScimV2GroupsGroupIdGet(groupId, authorization);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling ScimApi#getScimGroupScimV2GroupsGroupIdGet");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Reason: " + e.getResponseBody());
            System.err.println("Response headers: " + e.getResponseHeaders());
            e.printStackTrace();
        }
    }
}
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **groupId** | **UUID**|  | |
| **authorization** | **String**|  | [optional] |

### Return type

[**ScimGroupResource**](ScimGroupResource.md)


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

## getScimGroupScimV2GroupsGroupIdGetWithHttpInfo

> ApiResponse<ScimGroupResource> getScimGroupScimV2GroupsGroupIdGetWithHttpInfo(groupId, authorization)

Get Scim Group

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.ScimApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        ScimApi apiInstance = new ScimApi(defaultClient);
        UUID groupId = UUID.randomUUID(); // UUID |
        String authorization = "authorization_example"; // String |
        try {
            ApiResponse<ScimGroupResource> response = apiInstance.getScimGroupScimV2GroupsGroupIdGetWithHttpInfo(groupId, authorization);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling ScimApi#getScimGroupScimV2GroupsGroupIdGet");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Response headers: " + e.getResponseHeaders());
            System.err.println("Reason: " + e.getResponseBody());
            e.printStackTrace();
        }
    }
}
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **groupId** | **UUID**|  | |
| **authorization** | **String**|  | [optional] |

### Return type

ApiResponse<[**ScimGroupResource**](ScimGroupResource.md)>


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |


## getScimUserScimV2UsersUserIdGet

> ScimUserResource getScimUserScimV2UsersUserIdGet(userId, authorization)

Get Scim User

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.ScimApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        ScimApi apiInstance = new ScimApi(defaultClient);
        UUID userId = UUID.randomUUID(); // UUID |
        String authorization = "authorization_example"; // String |
        try {
            ScimUserResource result = apiInstance.getScimUserScimV2UsersUserIdGet(userId, authorization);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling ScimApi#getScimUserScimV2UsersUserIdGet");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Reason: " + e.getResponseBody());
            System.err.println("Response headers: " + e.getResponseHeaders());
            e.printStackTrace();
        }
    }
}
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **userId** | **UUID**|  | |
| **authorization** | **String**|  | [optional] |

### Return type

[**ScimUserResource**](ScimUserResource.md)


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

## getScimUserScimV2UsersUserIdGetWithHttpInfo

> ApiResponse<ScimUserResource> getScimUserScimV2UsersUserIdGetWithHttpInfo(userId, authorization)

Get Scim User

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.ScimApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        ScimApi apiInstance = new ScimApi(defaultClient);
        UUID userId = UUID.randomUUID(); // UUID |
        String authorization = "authorization_example"; // String |
        try {
            ApiResponse<ScimUserResource> response = apiInstance.getScimUserScimV2UsersUserIdGetWithHttpInfo(userId, authorization);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling ScimApi#getScimUserScimV2UsersUserIdGet");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Response headers: " + e.getResponseHeaders());
            System.err.println("Reason: " + e.getResponseBody());
            e.printStackTrace();
        }
    }
}
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **userId** | **UUID**|  | |
| **authorization** | **String**|  | [optional] |

### Return type

ApiResponse<[**ScimUserResource**](ScimUserResource.md)>


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |


## listScimGroupsScimV2GroupsGet

> ScimListResponse listScimGroupsScimV2GroupsGet(filter, startIndex, count, authorization)

List Scim Groups

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.ScimApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        ScimApi apiInstance = new ScimApi(defaultClient);
        String filter = "filter_example"; // String |
        Integer startIndex = 1; // Integer |
        Integer count = 100; // Integer |
        String authorization = "authorization_example"; // String |
        try {
            ScimListResponse result = apiInstance.listScimGroupsScimV2GroupsGet(filter, startIndex, count, authorization);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling ScimApi#listScimGroupsScimV2GroupsGet");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Reason: " + e.getResponseBody());
            System.err.println("Response headers: " + e.getResponseHeaders());
            e.printStackTrace();
        }
    }
}
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **filter** | **String**|  | [optional] |
| **startIndex** | **Integer**|  | [optional] [default to 1] |
| **count** | **Integer**|  | [optional] [default to 100] |
| **authorization** | **String**|  | [optional] |

### Return type

[**ScimListResponse**](ScimListResponse.md)


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

## listScimGroupsScimV2GroupsGetWithHttpInfo

> ApiResponse<ScimListResponse> listScimGroupsScimV2GroupsGetWithHttpInfo(filter, startIndex, count, authorization)

List Scim Groups

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.ScimApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        ScimApi apiInstance = new ScimApi(defaultClient);
        String filter = "filter_example"; // String |
        Integer startIndex = 1; // Integer |
        Integer count = 100; // Integer |
        String authorization = "authorization_example"; // String |
        try {
            ApiResponse<ScimListResponse> response = apiInstance.listScimGroupsScimV2GroupsGetWithHttpInfo(filter, startIndex, count, authorization);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling ScimApi#listScimGroupsScimV2GroupsGet");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Response headers: " + e.getResponseHeaders());
            System.err.println("Reason: " + e.getResponseBody());
            e.printStackTrace();
        }
    }
}
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **filter** | **String**|  | [optional] |
| **startIndex** | **Integer**|  | [optional] [default to 1] |
| **count** | **Integer**|  | [optional] [default to 100] |
| **authorization** | **String**|  | [optional] |

### Return type

ApiResponse<[**ScimListResponse**](ScimListResponse.md)>


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |


## listScimUsersScimV2UsersGet

> ScimListResponse listScimUsersScimV2UsersGet(filter, startIndex, count, authorization)

List Scim Users

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.ScimApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        ScimApi apiInstance = new ScimApi(defaultClient);
        String filter = "filter_example"; // String |
        Integer startIndex = 1; // Integer |
        Integer count = 100; // Integer |
        String authorization = "authorization_example"; // String |
        try {
            ScimListResponse result = apiInstance.listScimUsersScimV2UsersGet(filter, startIndex, count, authorization);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling ScimApi#listScimUsersScimV2UsersGet");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Reason: " + e.getResponseBody());
            System.err.println("Response headers: " + e.getResponseHeaders());
            e.printStackTrace();
        }
    }
}
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **filter** | **String**|  | [optional] |
| **startIndex** | **Integer**|  | [optional] [default to 1] |
| **count** | **Integer**|  | [optional] [default to 100] |
| **authorization** | **String**|  | [optional] |

### Return type

[**ScimListResponse**](ScimListResponse.md)


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

## listScimUsersScimV2UsersGetWithHttpInfo

> ApiResponse<ScimListResponse> listScimUsersScimV2UsersGetWithHttpInfo(filter, startIndex, count, authorization)

List Scim Users

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.ScimApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        ScimApi apiInstance = new ScimApi(defaultClient);
        String filter = "filter_example"; // String |
        Integer startIndex = 1; // Integer |
        Integer count = 100; // Integer |
        String authorization = "authorization_example"; // String |
        try {
            ApiResponse<ScimListResponse> response = apiInstance.listScimUsersScimV2UsersGetWithHttpInfo(filter, startIndex, count, authorization);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling ScimApi#listScimUsersScimV2UsersGet");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Response headers: " + e.getResponseHeaders());
            System.err.println("Reason: " + e.getResponseBody());
            e.printStackTrace();
        }
    }
}
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **filter** | **String**|  | [optional] |
| **startIndex** | **Integer**|  | [optional] [default to 1] |
| **count** | **Integer**|  | [optional] [default to 100] |
| **authorization** | **String**|  | [optional] |

### Return type

ApiResponse<[**ScimListResponse**](ScimListResponse.md)>


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |


## patchScimGroupScimV2GroupsGroupIdPatch

> ScimGroupResource patchScimGroupScimV2GroupsGroupIdPatch(groupId, scimPatchRequest, authorization)

Patch Scim Group

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.ScimApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        ScimApi apiInstance = new ScimApi(defaultClient);
        UUID groupId = UUID.randomUUID(); // UUID |
        ScimPatchRequest scimPatchRequest = new ScimPatchRequest(); // ScimPatchRequest |
        String authorization = "authorization_example"; // String |
        try {
            ScimGroupResource result = apiInstance.patchScimGroupScimV2GroupsGroupIdPatch(groupId, scimPatchRequest, authorization);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling ScimApi#patchScimGroupScimV2GroupsGroupIdPatch");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Reason: " + e.getResponseBody());
            System.err.println("Response headers: " + e.getResponseHeaders());
            e.printStackTrace();
        }
    }
}
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **groupId** | **UUID**|  | |
| **scimPatchRequest** | [**ScimPatchRequest**](ScimPatchRequest.md)|  | |
| **authorization** | **String**|  | [optional] |

### Return type

[**ScimGroupResource**](ScimGroupResource.md)


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

## patchScimGroupScimV2GroupsGroupIdPatchWithHttpInfo

> ApiResponse<ScimGroupResource> patchScimGroupScimV2GroupsGroupIdPatchWithHttpInfo(groupId, scimPatchRequest, authorization)

Patch Scim Group

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.ScimApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        ScimApi apiInstance = new ScimApi(defaultClient);
        UUID groupId = UUID.randomUUID(); // UUID |
        ScimPatchRequest scimPatchRequest = new ScimPatchRequest(); // ScimPatchRequest |
        String authorization = "authorization_example"; // String |
        try {
            ApiResponse<ScimGroupResource> response = apiInstance.patchScimGroupScimV2GroupsGroupIdPatchWithHttpInfo(groupId, scimPatchRequest, authorization);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling ScimApi#patchScimGroupScimV2GroupsGroupIdPatch");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Response headers: " + e.getResponseHeaders());
            System.err.println("Reason: " + e.getResponseBody());
            e.printStackTrace();
        }
    }
}
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **groupId** | **UUID**|  | |
| **scimPatchRequest** | [**ScimPatchRequest**](ScimPatchRequest.md)|  | |
| **authorization** | **String**|  | [optional] |

### Return type

ApiResponse<[**ScimGroupResource**](ScimGroupResource.md)>


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |


## patchScimUserScimV2UsersUserIdPatch

> ScimUserResource patchScimUserScimV2UsersUserIdPatch(userId, scimPatchRequest, authorization)

Patch Scim User

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.ScimApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        ScimApi apiInstance = new ScimApi(defaultClient);
        UUID userId = UUID.randomUUID(); // UUID |
        ScimPatchRequest scimPatchRequest = new ScimPatchRequest(); // ScimPatchRequest |
        String authorization = "authorization_example"; // String |
        try {
            ScimUserResource result = apiInstance.patchScimUserScimV2UsersUserIdPatch(userId, scimPatchRequest, authorization);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling ScimApi#patchScimUserScimV2UsersUserIdPatch");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Reason: " + e.getResponseBody());
            System.err.println("Response headers: " + e.getResponseHeaders());
            e.printStackTrace();
        }
    }
}
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **userId** | **UUID**|  | |
| **scimPatchRequest** | [**ScimPatchRequest**](ScimPatchRequest.md)|  | |
| **authorization** | **String**|  | [optional] |

### Return type

[**ScimUserResource**](ScimUserResource.md)


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

## patchScimUserScimV2UsersUserIdPatchWithHttpInfo

> ApiResponse<ScimUserResource> patchScimUserScimV2UsersUserIdPatchWithHttpInfo(userId, scimPatchRequest, authorization)

Patch Scim User

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.ScimApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        ScimApi apiInstance = new ScimApi(defaultClient);
        UUID userId = UUID.randomUUID(); // UUID |
        ScimPatchRequest scimPatchRequest = new ScimPatchRequest(); // ScimPatchRequest |
        String authorization = "authorization_example"; // String |
        try {
            ApiResponse<ScimUserResource> response = apiInstance.patchScimUserScimV2UsersUserIdPatchWithHttpInfo(userId, scimPatchRequest, authorization);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling ScimApi#patchScimUserScimV2UsersUserIdPatch");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Response headers: " + e.getResponseHeaders());
            System.err.println("Reason: " + e.getResponseBody());
            e.printStackTrace();
        }
    }
}
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **userId** | **UUID**|  | |
| **scimPatchRequest** | [**ScimPatchRequest**](ScimPatchRequest.md)|  | |
| **authorization** | **String**|  | [optional] |

### Return type

ApiResponse<[**ScimUserResource**](ScimUserResource.md)>


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |


## scimServiceProviderConfigScimV2ServiceProviderConfigGet

> Map<String, Object> scimServiceProviderConfigScimV2ServiceProviderConfigGet(authorization)

Scim Service Provider Config

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.ScimApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        ScimApi apiInstance = new ScimApi(defaultClient);
        String authorization = "authorization_example"; // String |
        try {
            Map<String, Object> result = apiInstance.scimServiceProviderConfigScimV2ServiceProviderConfigGet(authorization);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling ScimApi#scimServiceProviderConfigScimV2ServiceProviderConfigGet");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Reason: " + e.getResponseBody());
            System.err.println("Response headers: " + e.getResponseHeaders());
            e.printStackTrace();
        }
    }
}
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **authorization** | **String**|  | [optional] |

### Return type

**Map&lt;String, Object&gt;**


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

## scimServiceProviderConfigScimV2ServiceProviderConfigGetWithHttpInfo

> ApiResponse<Map<String, Object>> scimServiceProviderConfigScimV2ServiceProviderConfigGetWithHttpInfo(authorization)

Scim Service Provider Config

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.ScimApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        ScimApi apiInstance = new ScimApi(defaultClient);
        String authorization = "authorization_example"; // String |
        try {
            ApiResponse<Map<String, Object>> response = apiInstance.scimServiceProviderConfigScimV2ServiceProviderConfigGetWithHttpInfo(authorization);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling ScimApi#scimServiceProviderConfigScimV2ServiceProviderConfigGet");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Response headers: " + e.getResponseHeaders());
            System.err.println("Reason: " + e.getResponseBody());
            e.printStackTrace();
        }
    }
}
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **authorization** | **String**|  | [optional] |

### Return type

ApiResponse<**Map&lt;String, Object&gt;**>


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |
