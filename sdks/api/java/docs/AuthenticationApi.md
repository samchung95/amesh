# AuthenticationApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**beginFederatedLoginApiV1AuthFederatedProviderIdStartGet**](AuthenticationApi.md#beginFederatedLoginApiV1AuthFederatedProviderIdStartGet) | **GET** /api/v1/auth/federated/{provider_id}/start | Begin Federated Login |
| [**beginFederatedLoginApiV1AuthFederatedProviderIdStartGetWithHttpInfo**](AuthenticationApi.md#beginFederatedLoginApiV1AuthFederatedProviderIdStartGetWithHttpInfo) | **GET** /api/v1/auth/federated/{provider_id}/start | Begin Federated Login |
| [**changeLocalPasswordApiV1AuthPasswordPost**](AuthenticationApi.md#changeLocalPasswordApiV1AuthPasswordPost) | **POST** /api/v1/auth/password | Change Local Password |
| [**changeLocalPasswordApiV1AuthPasswordPostWithHttpInfo**](AuthenticationApi.md#changeLocalPasswordApiV1AuthPasswordPostWithHttpInfo) | **POST** /api/v1/auth/password | Change Local Password |
| [**completeOidcLoginApiV1AuthFederatedProviderIdCallbackGet**](AuthenticationApi.md#completeOidcLoginApiV1AuthFederatedProviderIdCallbackGet) | **GET** /api/v1/auth/federated/{provider_id}/callback | Complete Oidc Login |
| [**completeOidcLoginApiV1AuthFederatedProviderIdCallbackGetWithHttpInfo**](AuthenticationApi.md#completeOidcLoginApiV1AuthFederatedProviderIdCallbackGetWithHttpInfo) | **GET** /api/v1/auth/federated/{provider_id}/callback | Complete Oidc Login |
| [**completeSamlLoginApiV1AuthFederatedProviderIdCallbackPost**](AuthenticationApi.md#completeSamlLoginApiV1AuthFederatedProviderIdCallbackPost) | **POST** /api/v1/auth/federated/{provider_id}/callback | Complete Saml Login |
| [**completeSamlLoginApiV1AuthFederatedProviderIdCallbackPostWithHttpInfo**](AuthenticationApi.md#completeSamlLoginApiV1AuthFederatedProviderIdCallbackPostWithHttpInfo) | **POST** /api/v1/auth/federated/{provider_id}/callback | Complete Saml Login |
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
| [**samlServiceProviderMetadataApiV1AuthFederatedProviderIdSamlMetadataGet**](AuthenticationApi.md#samlServiceProviderMetadataApiV1AuthFederatedProviderIdSamlMetadataGet) | **GET** /api/v1/auth/federated/{provider_id}/saml/metadata | Saml Service Provider Metadata |
| [**samlServiceProviderMetadataApiV1AuthFederatedProviderIdSamlMetadataGetWithHttpInfo**](AuthenticationApi.md#samlServiceProviderMetadataApiV1AuthFederatedProviderIdSamlMetadataGetWithHttpInfo) | **GET** /api/v1/auth/federated/{provider_id}/saml/metadata | Saml Service Provider Metadata |
| [**setLocalPasswordApiV1AdminPrincipalsPrincipalIdLocalPasswordPut**](AuthenticationApi.md#setLocalPasswordApiV1AdminPrincipalsPrincipalIdLocalPasswordPut) | **PUT** /api/v1/admin/principals/{principal_id}/local-password | Set Local Password |
| [**setLocalPasswordApiV1AdminPrincipalsPrincipalIdLocalPasswordPutWithHttpInfo**](AuthenticationApi.md#setLocalPasswordApiV1AdminPrincipalsPrincipalIdLocalPasswordPutWithHttpInfo) | **PUT** /api/v1/admin/principals/{principal_id}/local-password | Set Local Password |



## beginFederatedLoginApiV1AuthFederatedProviderIdStartGet

> void beginFederatedLoginApiV1AuthFederatedProviderIdStartGet(providerId, tenant, returnTo)

Begin Federated Login

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
        String providerId = "providerId_example"; // String |
        String tenant = "tenant_example"; // String |
        String returnTo = "/"; // String |
        try {
            apiInstance.beginFederatedLoginApiV1AuthFederatedProviderIdStartGet(providerId, tenant, returnTo);
        } catch (ApiException e) {
            System.err.println("Exception when calling AuthenticationApi#beginFederatedLoginApiV1AuthFederatedProviderIdStartGet");
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
| **providerId** | **String**|  | |
| **tenant** | **String**|  | [optional] |
| **returnTo** | **String**|  | [optional] [default to /] |

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
| **307** | Successful Response |  -  |
| **422** | Validation Error |  -  |

## beginFederatedLoginApiV1AuthFederatedProviderIdStartGetWithHttpInfo

> ApiResponse<Void> beginFederatedLoginApiV1AuthFederatedProviderIdStartGetWithHttpInfo(providerId, tenant, returnTo)

Begin Federated Login

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
        String providerId = "providerId_example"; // String |
        String tenant = "tenant_example"; // String |
        String returnTo = "/"; // String |
        try {
            ApiResponse<Void> response = apiInstance.beginFederatedLoginApiV1AuthFederatedProviderIdStartGetWithHttpInfo(providerId, tenant, returnTo);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
        } catch (ApiException e) {
            System.err.println("Exception when calling AuthenticationApi#beginFederatedLoginApiV1AuthFederatedProviderIdStartGet");
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
| **providerId** | **String**|  | |
| **tenant** | **String**|  | [optional] |
| **returnTo** | **String**|  | [optional] [default to /] |

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
| **307** | Successful Response |  -  |
| **422** | Validation Error |  -  |


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


## completeOidcLoginApiV1AuthFederatedProviderIdCallbackGet

> void completeOidcLoginApiV1AuthFederatedProviderIdCallbackGet(providerId, state, code, error)

Complete Oidc Login

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
        String providerId = "providerId_example"; // String |
        String state = "state_example"; // String |
        String code = "code_example"; // String |
        String error = "error_example"; // String |
        try {
            apiInstance.completeOidcLoginApiV1AuthFederatedProviderIdCallbackGet(providerId, state, code, error);
        } catch (ApiException e) {
            System.err.println("Exception when calling AuthenticationApi#completeOidcLoginApiV1AuthFederatedProviderIdCallbackGet");
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
| **providerId** | **String**|  | |
| **state** | **String**|  | |
| **code** | **String**|  | [optional] |
| **error** | **String**|  | [optional] |

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
| **307** | Successful Response |  -  |
| **422** | Validation Error |  -  |

## completeOidcLoginApiV1AuthFederatedProviderIdCallbackGetWithHttpInfo

> ApiResponse<Void> completeOidcLoginApiV1AuthFederatedProviderIdCallbackGetWithHttpInfo(providerId, state, code, error)

Complete Oidc Login

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
        String providerId = "providerId_example"; // String |
        String state = "state_example"; // String |
        String code = "code_example"; // String |
        String error = "error_example"; // String |
        try {
            ApiResponse<Void> response = apiInstance.completeOidcLoginApiV1AuthFederatedProviderIdCallbackGetWithHttpInfo(providerId, state, code, error);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
        } catch (ApiException e) {
            System.err.println("Exception when calling AuthenticationApi#completeOidcLoginApiV1AuthFederatedProviderIdCallbackGet");
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
| **providerId** | **String**|  | |
| **state** | **String**|  | |
| **code** | **String**|  | [optional] |
| **error** | **String**|  | [optional] |

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
| **307** | Successful Response |  -  |
| **422** | Validation Error |  -  |


## completeSamlLoginApiV1AuthFederatedProviderIdCallbackPost

> void completeSamlLoginApiV1AuthFederatedProviderIdCallbackPost(providerId)

Complete Saml Login

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
        String providerId = "providerId_example"; // String |
        try {
            apiInstance.completeSamlLoginApiV1AuthFederatedProviderIdCallbackPost(providerId);
        } catch (ApiException e) {
            System.err.println("Exception when calling AuthenticationApi#completeSamlLoginApiV1AuthFederatedProviderIdCallbackPost");
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
| **providerId** | **String**|  | |

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
| **307** | Successful Response |  -  |
| **422** | Validation Error |  -  |

## completeSamlLoginApiV1AuthFederatedProviderIdCallbackPostWithHttpInfo

> ApiResponse<Void> completeSamlLoginApiV1AuthFederatedProviderIdCallbackPostWithHttpInfo(providerId)

Complete Saml Login

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
        String providerId = "providerId_example"; // String |
        try {
            ApiResponse<Void> response = apiInstance.completeSamlLoginApiV1AuthFederatedProviderIdCallbackPostWithHttpInfo(providerId);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
        } catch (ApiException e) {
            System.err.println("Exception when calling AuthenticationApi#completeSamlLoginApiV1AuthFederatedProviderIdCallbackPost");
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
| **providerId** | **String**|  | |

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
| **307** | Successful Response |  -  |
| **422** | Validation Error |  -  |


## listAuthenticationProvidersApiV1AuthProvidersGet

> List<AuthenticationProviderDescriptor> listAuthenticationProvidersApiV1AuthProvidersGet(identifier, tenant)

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
        String identifier = "identifier_example"; // String |
        String tenant = "tenant_example"; // String |
        try {
            List<AuthenticationProviderDescriptor> result = apiInstance.listAuthenticationProvidersApiV1AuthProvidersGet(identifier, tenant);
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


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **identifier** | **String**|  | [optional] |
| **tenant** | **String**|  | [optional] |

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
| **422** | Validation Error |  -  |

## listAuthenticationProvidersApiV1AuthProvidersGetWithHttpInfo

> ApiResponse<List<AuthenticationProviderDescriptor>> listAuthenticationProvidersApiV1AuthProvidersGetWithHttpInfo(identifier, tenant)

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
        String identifier = "identifier_example"; // String |
        String tenant = "tenant_example"; // String |
        try {
            ApiResponse<List<AuthenticationProviderDescriptor>> response = apiInstance.listAuthenticationProvidersApiV1AuthProvidersGetWithHttpInfo(identifier, tenant);
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


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **identifier** | **String**|  | [optional] |
| **tenant** | **String**|  | [optional] |

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
| **422** | Validation Error |  -  |


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


## samlServiceProviderMetadataApiV1AuthFederatedProviderIdSamlMetadataGet

> String samlServiceProviderMetadataApiV1AuthFederatedProviderIdSamlMetadataGet(providerId)

Saml Service Provider Metadata

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
        String providerId = "providerId_example"; // String |
        try {
            String result = apiInstance.samlServiceProviderMetadataApiV1AuthFederatedProviderIdSamlMetadataGet(providerId);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling AuthenticationApi#samlServiceProviderMetadataApiV1AuthFederatedProviderIdSamlMetadataGet");
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
| **providerId** | **String**|  | |

### Return type

**String**


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: text/plain, application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

## samlServiceProviderMetadataApiV1AuthFederatedProviderIdSamlMetadataGetWithHttpInfo

> ApiResponse<String> samlServiceProviderMetadataApiV1AuthFederatedProviderIdSamlMetadataGetWithHttpInfo(providerId)

Saml Service Provider Metadata

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
        String providerId = "providerId_example"; // String |
        try {
            ApiResponse<String> response = apiInstance.samlServiceProviderMetadataApiV1AuthFederatedProviderIdSamlMetadataGetWithHttpInfo(providerId);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling AuthenticationApi#samlServiceProviderMetadataApiV1AuthFederatedProviderIdSamlMetadataGet");
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
| **providerId** | **String**|  | |

### Return type

ApiResponse<**String**>


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: text/plain, application/json

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
