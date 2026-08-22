# amesh_client.AuthenticationApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**change_local_password_api_v1_auth_password_post**](AuthenticationApi.md#change_local_password_api_v1_auth_password_post) | **POST** /api/v1/auth/password | Change Local Password
[**list_authentication_providers_api_v1_auth_providers_get**](AuthenticationApi.md#list_authentication_providers_api_v1_auth_providers_get) | **GET** /api/v1/auth/providers | List Authentication Providers
[**login_api_v1_auth_login_post**](AuthenticationApi.md#login_api_v1_auth_login_post) | **POST** /api/v1/auth/login | Login
[**logout_all_api_v1_auth_logout_all_post**](AuthenticationApi.md#logout_all_api_v1_auth_logout_all_post) | **POST** /api/v1/auth/logout-all | Logout All
[**logout_api_v1_auth_logout_post**](AuthenticationApi.md#logout_api_v1_auth_logout_post) | **POST** /api/v1/auth/logout | Logout
[**revoke_principal_sessions_api_v1_admin_principals_principal_id_sessions_delete**](AuthenticationApi.md#revoke_principal_sessions_api_v1_admin_principals_principal_id_sessions_delete) | **DELETE** /api/v1/admin/principals/{principal_id}/sessions | Revoke Principal Sessions
[**set_local_password_api_v1_admin_principals_principal_id_local_password_put**](AuthenticationApi.md#set_local_password_api_v1_admin_principals_principal_id_local_password_put) | **PUT** /api/v1/admin/principals/{principal_id}/local-password | Set Local Password


# **change_local_password_api_v1_auth_password_post**
> RevokedSessionsResponse change_local_password_api_v1_auth_password_post(change_local_password_request, authorization=authorization, x_amesh_csrf=x_amesh_csrf)

Change Local Password

### Example


```python
import amesh_client
from amesh_client.models.change_local_password_request import ChangeLocalPasswordRequest
from amesh_client.models.revoked_sessions_response import RevokedSessionsResponse
from amesh_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = amesh_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with amesh_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = amesh_client.AuthenticationApi(api_client)
    change_local_password_request = amesh_client.ChangeLocalPasswordRequest() # ChangeLocalPasswordRequest |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)

    try:
        # Change Local Password
        api_response = api_instance.change_local_password_api_v1_auth_password_post(change_local_password_request, authorization=authorization, x_amesh_csrf=x_amesh_csrf)
        print("The response of AuthenticationApi->change_local_password_api_v1_auth_password_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AuthenticationApi->change_local_password_api_v1_auth_password_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **change_local_password_request** | [**ChangeLocalPasswordRequest**](ChangeLocalPasswordRequest.md)|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]

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
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_authentication_providers_api_v1_auth_providers_get**
> List[AuthenticationProviderDescriptor] list_authentication_providers_api_v1_auth_providers_get()

List Authentication Providers

### Example


```python
import amesh_client
from amesh_client.models.authentication_provider_descriptor import AuthenticationProviderDescriptor
from amesh_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = amesh_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with amesh_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = amesh_client.AuthenticationApi(api_client)

    try:
        # List Authentication Providers
        api_response = api_instance.list_authentication_providers_api_v1_auth_providers_get()
        print("The response of AuthenticationApi->list_authentication_providers_api_v1_auth_providers_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AuthenticationApi->list_authentication_providers_api_v1_auth_providers_get: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

[**List[AuthenticationProviderDescriptor]**](AuthenticationProviderDescriptor.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **login_api_v1_auth_login_post**
> LoginResponse login_api_v1_auth_login_post(login_request)

Login

### Example


```python
import amesh_client
from amesh_client.models.login_request import LoginRequest
from amesh_client.models.login_response import LoginResponse
from amesh_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = amesh_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with amesh_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = amesh_client.AuthenticationApi(api_client)
    login_request = amesh_client.LoginRequest() # LoginRequest |

    try:
        # Login
        api_response = api_instance.login_api_v1_auth_login_post(login_request)
        print("The response of AuthenticationApi->login_api_v1_auth_login_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AuthenticationApi->login_api_v1_auth_login_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **login_request** | [**LoginRequest**](LoginRequest.md)|  |

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
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **logout_all_api_v1_auth_logout_all_post**
> RevokedSessionsResponse logout_all_api_v1_auth_logout_all_post(authorization=authorization, x_amesh_csrf=x_amesh_csrf)

Logout All

### Example


```python
import amesh_client
from amesh_client.models.revoked_sessions_response import RevokedSessionsResponse
from amesh_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = amesh_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with amesh_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = amesh_client.AuthenticationApi(api_client)
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)

    try:
        # Logout All
        api_response = api_instance.logout_all_api_v1_auth_logout_all_post(authorization=authorization, x_amesh_csrf=x_amesh_csrf)
        print("The response of AuthenticationApi->logout_all_api_v1_auth_logout_all_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AuthenticationApi->logout_all_api_v1_auth_logout_all_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]

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
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **logout_api_v1_auth_logout_post**
> logout_api_v1_auth_logout_post(authorization=authorization, x_amesh_csrf=x_amesh_csrf)

Logout

### Example


```python
import amesh_client
from amesh_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = amesh_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with amesh_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = amesh_client.AuthenticationApi(api_client)
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)

    try:
        # Logout
        api_instance.logout_api_v1_auth_logout_post(authorization=authorization, x_amesh_csrf=x_amesh_csrf)
    except Exception as e:
        print("Exception when calling AuthenticationApi->logout_api_v1_auth_logout_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**204** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **revoke_principal_sessions_api_v1_admin_principals_principal_id_sessions_delete**
> RevokedSessionsResponse revoke_principal_sessions_api_v1_admin_principals_principal_id_sessions_delete(principal_id, authorization=authorization, x_amesh_csrf=x_amesh_csrf)

Revoke Principal Sessions

### Example


```python
import amesh_client
from amesh_client.models.revoked_sessions_response import RevokedSessionsResponse
from amesh_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = amesh_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with amesh_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = amesh_client.AuthenticationApi(api_client)
    principal_id = UUID('38400000-8cf0-11bd-b23e-10b96e4ef00d') # UUID |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)

    try:
        # Revoke Principal Sessions
        api_response = api_instance.revoke_principal_sessions_api_v1_admin_principals_principal_id_sessions_delete(principal_id, authorization=authorization, x_amesh_csrf=x_amesh_csrf)
        print("The response of AuthenticationApi->revoke_principal_sessions_api_v1_admin_principals_principal_id_sessions_delete:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AuthenticationApi->revoke_principal_sessions_api_v1_admin_principals_principal_id_sessions_delete: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **principal_id** | **UUID**|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]

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
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **set_local_password_api_v1_admin_principals_principal_id_local_password_put**
> RevokedSessionsResponse set_local_password_api_v1_admin_principals_principal_id_local_password_put(principal_id, set_local_password_request, authorization=authorization, x_amesh_csrf=x_amesh_csrf)

Set Local Password

### Example


```python
import amesh_client
from amesh_client.models.revoked_sessions_response import RevokedSessionsResponse
from amesh_client.models.set_local_password_request import SetLocalPasswordRequest
from amesh_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = amesh_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with amesh_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = amesh_client.AuthenticationApi(api_client)
    principal_id = UUID('38400000-8cf0-11bd-b23e-10b96e4ef00d') # UUID |
    set_local_password_request = amesh_client.SetLocalPasswordRequest() # SetLocalPasswordRequest |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)

    try:
        # Set Local Password
        api_response = api_instance.set_local_password_api_v1_admin_principals_principal_id_local_password_put(principal_id, set_local_password_request, authorization=authorization, x_amesh_csrf=x_amesh_csrf)
        print("The response of AuthenticationApi->set_local_password_api_v1_admin_principals_principal_id_local_password_put:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AuthenticationApi->set_local_password_api_v1_admin_principals_principal_id_local_password_put: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **principal_id** | **UUID**|  |
 **set_local_password_request** | [**SetLocalPasswordRequest**](SetLocalPasswordRequest.md)|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]

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
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)
