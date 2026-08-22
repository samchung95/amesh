# AuthenticationApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**changeLocalPasswordApiV1AuthPasswordPost**](AuthenticationApi.md#changelocalpasswordapiv1authpasswordpost) | **POST** /api/v1/auth/password | Change Local Password |
| [**listAuthenticationProvidersApiV1AuthProvidersGet**](AuthenticationApi.md#listauthenticationprovidersapiv1authprovidersget) | **GET** /api/v1/auth/providers | List Authentication Providers |
| [**loginApiV1AuthLoginPost**](AuthenticationApi.md#loginapiv1authloginpost) | **POST** /api/v1/auth/login | Login |
| [**logoutAllApiV1AuthLogoutAllPost**](AuthenticationApi.md#logoutallapiv1authlogoutallpost) | **POST** /api/v1/auth/logout-all | Logout All |
| [**logoutApiV1AuthLogoutPost**](AuthenticationApi.md#logoutapiv1authlogoutpost) | **POST** /api/v1/auth/logout | Logout |
| [**revokePrincipalSessionsApiV1AdminPrincipalsPrincipalIdSessionsDelete**](AuthenticationApi.md#revokeprincipalsessionsapiv1adminprincipalsprincipalidsessionsdelete) | **DELETE** /api/v1/admin/principals/{principal_id}/sessions | Revoke Principal Sessions |
| [**setLocalPasswordApiV1AdminPrincipalsPrincipalIdLocalPasswordPut**](AuthenticationApi.md#setlocalpasswordapiv1adminprincipalsprincipalidlocalpasswordput) | **PUT** /api/v1/admin/principals/{principal_id}/local-password | Set Local Password |



## changeLocalPasswordApiV1AuthPasswordPost

> RevokedSessionsResponse changeLocalPasswordApiV1AuthPasswordPost(changeLocalPasswordRequest, authorization, xAmeshCSRF)

Change Local Password

### Example

```ts
import {
  Configuration,
  AuthenticationApi,
} from '@amesh/client';
import type { ChangeLocalPasswordApiV1AuthPasswordPostRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new AuthenticationApi();

  const body = {
    // ChangeLocalPasswordRequest
    changeLocalPasswordRequest: ...,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
  } satisfies ChangeLocalPasswordApiV1AuthPasswordPostRequest;

  try {
    const data = await api.changeLocalPasswordApiV1AuthPasswordPost(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **changeLocalPasswordRequest** | [ChangeLocalPasswordRequest](ChangeLocalPasswordRequest.md) |  | |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**RevokedSessionsResponse**](RevokedSessionsResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## listAuthenticationProvidersApiV1AuthProvidersGet

> Array&lt;AuthenticationProviderDescriptor&gt; listAuthenticationProvidersApiV1AuthProvidersGet()

List Authentication Providers

### Example

```ts
import {
  Configuration,
  AuthenticationApi,
} from '@amesh/client';
import type { ListAuthenticationProvidersApiV1AuthProvidersGetRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new AuthenticationApi();

  try {
    const data = await api.listAuthenticationProvidersApiV1AuthProvidersGet();
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters

This endpoint does not need any parameter.

### Return type

[**Array&lt;AuthenticationProviderDescriptor&gt;**](AuthenticationProviderDescriptor.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## loginApiV1AuthLoginPost

> LoginResponse loginApiV1AuthLoginPost(loginRequest)

Login

### Example

```ts
import {
  Configuration,
  AuthenticationApi,
} from '@amesh/client';
import type { LoginApiV1AuthLoginPostRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new AuthenticationApi();

  const body = {
    // LoginRequest
    loginRequest: ...,
  } satisfies LoginApiV1AuthLoginPostRequest;

  try {
    const data = await api.loginApiV1AuthLoginPost(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **loginRequest** | [LoginRequest](LoginRequest.md) |  | |

### Return type

[**LoginResponse**](LoginResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## logoutAllApiV1AuthLogoutAllPost

> RevokedSessionsResponse logoutAllApiV1AuthLogoutAllPost(authorization, xAmeshCSRF)

Logout All

### Example

```ts
import {
  Configuration,
  AuthenticationApi,
} from '@amesh/client';
import type { LogoutAllApiV1AuthLogoutAllPostRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new AuthenticationApi();

  const body = {
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
  } satisfies LogoutAllApiV1AuthLogoutAllPostRequest;

  try {
    const data = await api.logoutAllApiV1AuthLogoutAllPost(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**RevokedSessionsResponse**](RevokedSessionsResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## logoutApiV1AuthLogoutPost

> logoutApiV1AuthLogoutPost(authorization, xAmeshCSRF)

Logout

### Example

```ts
import {
  Configuration,
  AuthenticationApi,
} from '@amesh/client';
import type { LogoutApiV1AuthLogoutPostRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new AuthenticationApi();

  const body = {
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
  } satisfies LogoutApiV1AuthLogoutPostRequest;

  try {
    const data = await api.logoutApiV1AuthLogoutPost(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

`void` (Empty response body)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **204** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## revokePrincipalSessionsApiV1AdminPrincipalsPrincipalIdSessionsDelete

> RevokedSessionsResponse revokePrincipalSessionsApiV1AdminPrincipalsPrincipalIdSessionsDelete(principalId, authorization, xAmeshCSRF)

Revoke Principal Sessions

### Example

```ts
import {
  Configuration,
  AuthenticationApi,
} from '@amesh/client';
import type { RevokePrincipalSessionsApiV1AdminPrincipalsPrincipalIdSessionsDeleteRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new AuthenticationApi();

  const body = {
    // string
    principalId: 38400000-8cf0-11bd-b23e-10b96e4ef00d,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
  } satisfies RevokePrincipalSessionsApiV1AdminPrincipalsPrincipalIdSessionsDeleteRequest;

  try {
    const data = await api.revokePrincipalSessionsApiV1AdminPrincipalsPrincipalIdSessionsDelete(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **principalId** | `string` |  | [Defaults to `undefined`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**RevokedSessionsResponse**](RevokedSessionsResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## setLocalPasswordApiV1AdminPrincipalsPrincipalIdLocalPasswordPut

> RevokedSessionsResponse setLocalPasswordApiV1AdminPrincipalsPrincipalIdLocalPasswordPut(principalId, setLocalPasswordRequest, authorization, xAmeshCSRF)

Set Local Password

### Example

```ts
import {
  Configuration,
  AuthenticationApi,
} from '@amesh/client';
import type { SetLocalPasswordApiV1AdminPrincipalsPrincipalIdLocalPasswordPutRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new AuthenticationApi();

  const body = {
    // string
    principalId: 38400000-8cf0-11bd-b23e-10b96e4ef00d,
    // SetLocalPasswordRequest
    setLocalPasswordRequest: ...,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
  } satisfies SetLocalPasswordApiV1AdminPrincipalsPrincipalIdLocalPasswordPutRequest;

  try {
    const data = await api.setLocalPasswordApiV1AdminPrincipalsPrincipalIdLocalPasswordPut(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **principalId** | `string` |  | [Defaults to `undefined`] |
| **setLocalPasswordRequest** | [SetLocalPasswordRequest](SetLocalPasswordRequest.md) |  | |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**RevokedSessionsResponse**](RevokedSessionsResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)
