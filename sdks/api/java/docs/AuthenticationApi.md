# AuthenticationApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**changeLocalPasswordApiV1AuthPasswordPost**](AuthenticationApi.md#changeLocalPasswordApiV1AuthPasswordPost) | **POST** /api/v1/auth/password | Change Local Password |
| [**changeLocalPasswordApiV1AuthPasswordPostWithHttpInfo**](AuthenticationApi.md#changeLocalPasswordApiV1AuthPasswordPostWithHttpInfo) | **POST** /api/v1/auth/password | Change Local Password |
| [**listAuthenticationProvidersApiV1AuthProvidersGet**](AuthenticationApi.md#listAuthenticationProvidersApiV1AuthProvidersGet) | **GET** /api/v1/auth/providers | List Authentication Providers |
| [**listAuthenticationProvidersApiV1AuthProvidersGetWithHttpInfo**](AuthenticationApi.md#listAuthenticationProvidersApiV1AuthProvidersGetWithHttpInfo) | **GET** /api/v1/auth/providers | List Authentication Providers |
| [**loginApiV1AuthLoginPost**](AuthenticationApi.md#loginApiV1AuthLoginPost) | **POST** /api/v1/auth/login | Login |
| [**loginApiV1AuthLoginPostWithHttpInfo**](AuthenticationApi.md#loginApiV1AuthLoginPostWithHttpInfo) | **POST** /api/v1/auth/login | Login |
| [**logoutAllApiV1AuthLogoutAllPost**](AuthenticationApi.md#logoutAllApiV1AuthLogoutAllPost) | **POST** /api/v1/auth/logout-all | Logout All |
| [**logoutAllApiV1AuthLogoutAllPostWithHttpInfo**](AuthenticationApi.md#logoutAllApiV1AuthLogoutAllPostWithHttpInfo) | **POST** /api/v1/auth/logout-all | Logout All |
| [**logoutApiV1AuthLogoutPost**](AuthenticationApi.md#logoutApiV1AuthLogoutPost) | **POST** /api/v1/auth/logout | Logout |
| [**logoutApiV1AuthLogoutPostWithHttpInfo**](AuthenticationApi.md#logoutApiV1AuthLogoutPostWithHttpInfo) | **POST** /api/v1/auth/logout | Logout |
| [**revokePrincipalSessionsApiV1AdminPrincipalsPrincipalIdSessionsDelete**](AuthenticationApi.md#revokePrincipalSessionsApiV1AdminPrincipalsPrincipalIdSessionsDelete) | **DELETE** /api/v1/admin/principals/{principal_id}/sessions | Revoke Principal Sessions |
| [**revokePrincipalSessionsApiV1AdminPrincipalsPrincipalIdSessionsDeleteWithHttpInfo**](AuthenticationApi.md#revokePrincipalSessionsApiV1AdminPrincipalsPrincipalIdSessionsDeleteWithHttpInfo) | **DELETE** /api/v1/admin/principals/{principal_id}/sessions | Revoke Principal Sessions |
| [**setLocalPasswordApiV1AdminPrincipalsPrincipalIdLocalPasswordPut**](AuthenticationApi.md#setLocalPasswordApiV1AdminPrincipalsPrincipalIdLocalPasswordPut) | **PUT** /api/v1/admin/principals/{principal_id}/local-password | Set Local Password |
| [**setLocalPasswordApiV1AdminPrincipalsPrincipalIdLocalPasswordPutWithHttpInfo**](AuthenticationApi.md#setLocalPasswordApiV1AdminPrincipalsPrincipalIdLocalPasswordPutWithHttpInfo) | **PUT** /api/v1/admin/principals/{principal_id}/local-password | Set Local Password |



## changeLocalPasswordApiV1AuthPasswordPost

> RevokedSessionsResponse changeLocalPasswordApiV1AuthPasswordPost(changeLocalPasswordRequest, authorization, xAmeshCSRF)

Change Local Password

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AuthenticationApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AuthenticationApi apiInstance = new AuthenticationApi(defaultClient);
        ChangeLocalPasswordRequest changeLocalPasswordRequest = new ChangeLocalPasswordRequest(); // ChangeLocalPasswordRequest |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        try {
            RevokedSessionsResponse result = apiInstance.changeLocalPasswordApiV1AuthPasswordPost(changeLocalPasswordRequest, authorization, xAmeshCSRF);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling AuthenticationApi#changeLocalPasswordApiV1AuthPasswordPost");
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
| **changeLocalPasswordRequest** | [**ChangeLocalPasswordRequest**](ChangeLocalPasswordRequest.md)|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |

### Return type

[**RevokedSessionsResponse**](RevokedSessionsResponse.md)


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

## changeLocalPasswordApiV1AuthPasswordPostWithHttpInfo

> ApiResponse<RevokedSessionsResponse> changeLocalPasswordApiV1AuthPasswordPostWithHttpInfo(changeLocalPasswordRequest, authorization, xAmeshCSRF)

Change Local Password

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AuthenticationApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AuthenticationApi apiInstance = new AuthenticationApi(defaultClient);
        ChangeLocalPasswordRequest changeLocalPasswordRequest = new ChangeLocalPasswordRequest(); // ChangeLocalPasswordRequest |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        try {
            ApiResponse<RevokedSessionsResponse> response = apiInstance.changeLocalPasswordApiV1AuthPasswordPostWithHttpInfo(changeLocalPasswordRequest, authorization, xAmeshCSRF);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling AuthenticationApi#changeLocalPasswordApiV1AuthPasswordPost");
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
| **changeLocalPasswordRequest** | [**ChangeLocalPasswordRequest**](ChangeLocalPasswordRequest.md)|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |

### Return type

ApiResponse<[**RevokedSessionsResponse**](RevokedSessionsResponse.md)>


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


## listAuthenticationProvidersApiV1AuthProvidersGet

> List<AuthenticationProviderDescriptor> listAuthenticationProvidersApiV1AuthProvidersGet()

List Authentication Providers

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AuthenticationApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AuthenticationApi apiInstance = new AuthenticationApi(defaultClient);
        try {
            List<AuthenticationProviderDescriptor> result = apiInstance.listAuthenticationProvidersApiV1AuthProvidersGet();
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling AuthenticationApi#listAuthenticationProvidersApiV1AuthProvidersGet");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Reason: " + e.getResponseBody());
            System.err.println("Response headers: " + e.getResponseHeaders());
            e.printStackTrace();
        }
    }
}
```

### Parameters

This endpoint does not need any parameter.

### Return type

[**List&lt;AuthenticationProviderDescriptor&gt;**](AuthenticationProviderDescriptor.md)


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |

## listAuthenticationProvidersApiV1AuthProvidersGetWithHttpInfo

> ApiResponse<List<AuthenticationProviderDescriptor>> listAuthenticationProvidersApiV1AuthProvidersGetWithHttpInfo()

List Authentication Providers

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AuthenticationApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AuthenticationApi apiInstance = new AuthenticationApi(defaultClient);
        try {
            ApiResponse<List<AuthenticationProviderDescriptor>> response = apiInstance.listAuthenticationProvidersApiV1AuthProvidersGetWithHttpInfo();
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling AuthenticationApi#listAuthenticationProvidersApiV1AuthProvidersGet");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Response headers: " + e.getResponseHeaders());
            System.err.println("Reason: " + e.getResponseBody());
            e.printStackTrace();
        }
    }
}
```

### Parameters

This endpoint does not need any parameter.

### Return type

ApiResponse<[**List&lt;AuthenticationProviderDescriptor&gt;**](AuthenticationProviderDescriptor.md)>


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |


## loginApiV1AuthLoginPost

> LoginResponse loginApiV1AuthLoginPost(loginRequest)

Login

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AuthenticationApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AuthenticationApi apiInstance = new AuthenticationApi(defaultClient);
        LoginRequest loginRequest = new LoginRequest(); // LoginRequest |
        try {
            LoginResponse result = apiInstance.loginApiV1AuthLoginPost(loginRequest);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling AuthenticationApi#loginApiV1AuthLoginPost");
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
| **loginRequest** | [**LoginRequest**](LoginRequest.md)|  | |

### Return type

[**LoginResponse**](LoginResponse.md)


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

## loginApiV1AuthLoginPostWithHttpInfo

> ApiResponse<LoginResponse> loginApiV1AuthLoginPostWithHttpInfo(loginRequest)

Login

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AuthenticationApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AuthenticationApi apiInstance = new AuthenticationApi(defaultClient);
        LoginRequest loginRequest = new LoginRequest(); // LoginRequest |
        try {
            ApiResponse<LoginResponse> response = apiInstance.loginApiV1AuthLoginPostWithHttpInfo(loginRequest);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling AuthenticationApi#loginApiV1AuthLoginPost");
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
| **loginRequest** | [**LoginRequest**](LoginRequest.md)|  | |

### Return type

ApiResponse<[**LoginResponse**](LoginResponse.md)>


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


## logoutAllApiV1AuthLogoutAllPost

> RevokedSessionsResponse logoutAllApiV1AuthLogoutAllPost(authorization, xAmeshCSRF)

Logout All

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AuthenticationApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AuthenticationApi apiInstance = new AuthenticationApi(defaultClient);
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        try {
            RevokedSessionsResponse result = apiInstance.logoutAllApiV1AuthLogoutAllPost(authorization, xAmeshCSRF);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling AuthenticationApi#logoutAllApiV1AuthLogoutAllPost");
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
| **xAmeshCSRF** | **String**|  | [optional] |

### Return type

[**RevokedSessionsResponse**](RevokedSessionsResponse.md)


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

## logoutAllApiV1AuthLogoutAllPostWithHttpInfo

> ApiResponse<RevokedSessionsResponse> logoutAllApiV1AuthLogoutAllPostWithHttpInfo(authorization, xAmeshCSRF)

Logout All

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AuthenticationApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AuthenticationApi apiInstance = new AuthenticationApi(defaultClient);
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        try {
            ApiResponse<RevokedSessionsResponse> response = apiInstance.logoutAllApiV1AuthLogoutAllPostWithHttpInfo(authorization, xAmeshCSRF);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling AuthenticationApi#logoutAllApiV1AuthLogoutAllPost");
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
| **xAmeshCSRF** | **String**|  | [optional] |

### Return type

ApiResponse<[**RevokedSessionsResponse**](RevokedSessionsResponse.md)>


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


## logoutApiV1AuthLogoutPost

> void logoutApiV1AuthLogoutPost(authorization, xAmeshCSRF)

Logout

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AuthenticationApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AuthenticationApi apiInstance = new AuthenticationApi(defaultClient);
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        try {
            apiInstance.logoutApiV1AuthLogoutPost(authorization, xAmeshCSRF);
        } catch (ApiException e) {
            System.err.println("Exception when calling AuthenticationApi#logoutApiV1AuthLogoutPost");
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
| **xAmeshCSRF** | **String**|  | [optional] |

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

## logoutApiV1AuthLogoutPostWithHttpInfo

> ApiResponse<Void> logoutApiV1AuthLogoutPostWithHttpInfo(authorization, xAmeshCSRF)

Logout

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AuthenticationApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AuthenticationApi apiInstance = new AuthenticationApi(defaultClient);
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        try {
            ApiResponse<Void> response = apiInstance.logoutApiV1AuthLogoutPostWithHttpInfo(authorization, xAmeshCSRF);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
        } catch (ApiException e) {
            System.err.println("Exception when calling AuthenticationApi#logoutApiV1AuthLogoutPost");
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
| **xAmeshCSRF** | **String**|  | [optional] |

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


## revokePrincipalSessionsApiV1AdminPrincipalsPrincipalIdSessionsDelete

> RevokedSessionsResponse revokePrincipalSessionsApiV1AdminPrincipalsPrincipalIdSessionsDelete(principalId, authorization, xAmeshCSRF)

Revoke Principal Sessions

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AuthenticationApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AuthenticationApi apiInstance = new AuthenticationApi(defaultClient);
        UUID principalId = UUID.randomUUID(); // UUID |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        try {
            RevokedSessionsResponse result = apiInstance.revokePrincipalSessionsApiV1AdminPrincipalsPrincipalIdSessionsDelete(principalId, authorization, xAmeshCSRF);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling AuthenticationApi#revokePrincipalSessionsApiV1AdminPrincipalsPrincipalIdSessionsDelete");
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
| **principalId** | **UUID**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |

### Return type

[**RevokedSessionsResponse**](RevokedSessionsResponse.md)


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

## revokePrincipalSessionsApiV1AdminPrincipalsPrincipalIdSessionsDeleteWithHttpInfo

> ApiResponse<RevokedSessionsResponse> revokePrincipalSessionsApiV1AdminPrincipalsPrincipalIdSessionsDeleteWithHttpInfo(principalId, authorization, xAmeshCSRF)

Revoke Principal Sessions

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AuthenticationApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AuthenticationApi apiInstance = new AuthenticationApi(defaultClient);
        UUID principalId = UUID.randomUUID(); // UUID |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        try {
            ApiResponse<RevokedSessionsResponse> response = apiInstance.revokePrincipalSessionsApiV1AdminPrincipalsPrincipalIdSessionsDeleteWithHttpInfo(principalId, authorization, xAmeshCSRF);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling AuthenticationApi#revokePrincipalSessionsApiV1AdminPrincipalsPrincipalIdSessionsDelete");
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
| **principalId** | **UUID**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |

### Return type

ApiResponse<[**RevokedSessionsResponse**](RevokedSessionsResponse.md)>


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


## setLocalPasswordApiV1AdminPrincipalsPrincipalIdLocalPasswordPut

> RevokedSessionsResponse setLocalPasswordApiV1AdminPrincipalsPrincipalIdLocalPasswordPut(principalId, setLocalPasswordRequest, authorization, xAmeshCSRF)

Set Local Password

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AuthenticationApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AuthenticationApi apiInstance = new AuthenticationApi(defaultClient);
        UUID principalId = UUID.randomUUID(); // UUID |
        SetLocalPasswordRequest setLocalPasswordRequest = new SetLocalPasswordRequest(); // SetLocalPasswordRequest |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        try {
            RevokedSessionsResponse result = apiInstance.setLocalPasswordApiV1AdminPrincipalsPrincipalIdLocalPasswordPut(principalId, setLocalPasswordRequest, authorization, xAmeshCSRF);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling AuthenticationApi#setLocalPasswordApiV1AdminPrincipalsPrincipalIdLocalPasswordPut");
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
| **principalId** | **UUID**|  | |
| **setLocalPasswordRequest** | [**SetLocalPasswordRequest**](SetLocalPasswordRequest.md)|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |

### Return type

[**RevokedSessionsResponse**](RevokedSessionsResponse.md)


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

## setLocalPasswordApiV1AdminPrincipalsPrincipalIdLocalPasswordPutWithHttpInfo

> ApiResponse<RevokedSessionsResponse> setLocalPasswordApiV1AdminPrincipalsPrincipalIdLocalPasswordPutWithHttpInfo(principalId, setLocalPasswordRequest, authorization, xAmeshCSRF)

Set Local Password

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.AuthenticationApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        AuthenticationApi apiInstance = new AuthenticationApi(defaultClient);
        UUID principalId = UUID.randomUUID(); // UUID |
        SetLocalPasswordRequest setLocalPasswordRequest = new SetLocalPasswordRequest(); // SetLocalPasswordRequest |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        try {
            ApiResponse<RevokedSessionsResponse> response = apiInstance.setLocalPasswordApiV1AdminPrincipalsPrincipalIdLocalPasswordPutWithHttpInfo(principalId, setLocalPasswordRequest, authorization, xAmeshCSRF);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling AuthenticationApi#setLocalPasswordApiV1AdminPrincipalsPrincipalIdLocalPasswordPut");
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
| **principalId** | **UUID**|  | |
| **setLocalPasswordRequest** | [**SetLocalPasswordRequest**](SetLocalPasswordRequest.md)|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |

### Return type

ApiResponse<[**RevokedSessionsResponse**](RevokedSessionsResponse.md)>


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
