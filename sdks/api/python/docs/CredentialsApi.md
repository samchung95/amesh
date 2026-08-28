# amesh_client.CredentialsApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**exchange_workload_credential_api_v1_credentials_exchange_post**](CredentialsApi.md#exchange_workload_credential_api_v1_credentials_exchange_post) | **POST** /api/v1/credentials/exchange | Exchange Workload Credential
[**issue_credential_api_v1_admin_principals_principal_id_credentials_post**](CredentialsApi.md#issue_credential_api_v1_admin_principals_principal_id_credentials_post) | **POST** /api/v1/admin/principals/{principal_id}/credentials | Issue Credential
[**list_credentials_api_v1_admin_principals_principal_id_credentials_get**](CredentialsApi.md#list_credentials_api_v1_admin_principals_principal_id_credentials_get) | **GET** /api/v1/admin/principals/{principal_id}/credentials | List Credentials
[**revoke_all_credentials_api_v1_admin_principals_principal_id_credentials_delete**](CredentialsApi.md#revoke_all_credentials_api_v1_admin_principals_principal_id_credentials_delete) | **DELETE** /api/v1/admin/principals/{principal_id}/credentials | Revoke All Credentials
[**revoke_credential_api_v1_admin_credentials_credential_id_delete**](CredentialsApi.md#revoke_credential_api_v1_admin_credentials_credential_id_delete) | **DELETE** /api/v1/admin/credentials/{credential_id} | Revoke Credential
[**rotate_credential_api_v1_admin_credentials_credential_id_rotate_post**](CredentialsApi.md#rotate_credential_api_v1_admin_credentials_credential_id_rotate_post) | **POST** /api/v1/admin/credentials/{credential_id}/rotate | Rotate Credential


# **exchange_workload_credential_api_v1_credentials_exchange_post**
> IssuedCredentialResponse exchange_workload_credential_api_v1_credentials_exchange_post(exchange_credential_request, authorization=authorization, x_amesh_csrf=x_amesh_csrf)

Exchange Workload Credential

### Example


```python
import amesh_client
from amesh_client.models.exchange_credential_request import ExchangeCredentialRequest
from amesh_client.models.issued_credential_response import IssuedCredentialResponse
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
    api_instance = amesh_client.CredentialsApi(api_client)
    exchange_credential_request = amesh_client.ExchangeCredentialRequest() # ExchangeCredentialRequest |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)

    try:
        # Exchange Workload Credential
        api_response = api_instance.exchange_workload_credential_api_v1_credentials_exchange_post(exchange_credential_request, authorization=authorization, x_amesh_csrf=x_amesh_csrf)
        print("The response of CredentialsApi->exchange_workload_credential_api_v1_credentials_exchange_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CredentialsApi->exchange_workload_credential_api_v1_credentials_exchange_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **exchange_credential_request** | **ExchangeCredentialRequest**|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]

### Return type

**IssuedCredentialResponse**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **issue_credential_api_v1_admin_principals_principal_id_credentials_post**
> IssuedCredentialResponse issue_credential_api_v1_admin_principals_principal_id_credentials_post(principal_id, issue_credential_request, authorization=authorization, x_amesh_csrf=x_amesh_csrf)

Issue Credential

### Example


```python
import amesh_client
from amesh_client.models.issue_credential_request import IssueCredentialRequest
from amesh_client.models.issued_credential_response import IssuedCredentialResponse
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
    api_instance = amesh_client.CredentialsApi(api_client)
    principal_id = UUID('38400000-8cf0-11bd-b23e-10b96e4ef00d') # UUID |
    issue_credential_request = amesh_client.IssueCredentialRequest() # IssueCredentialRequest |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)

    try:
        # Issue Credential
        api_response = api_instance.issue_credential_api_v1_admin_principals_principal_id_credentials_post(principal_id, issue_credential_request, authorization=authorization, x_amesh_csrf=x_amesh_csrf)
        print("The response of CredentialsApi->issue_credential_api_v1_admin_principals_principal_id_credentials_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CredentialsApi->issue_credential_api_v1_admin_principals_principal_id_credentials_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **principal_id** | **UUID**|  |
 **issue_credential_request** | **IssueCredentialRequest**|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]

### Return type

**IssuedCredentialResponse**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_credentials_api_v1_admin_principals_principal_id_credentials_get**
> List[CredentialMetadata] list_credentials_api_v1_admin_principals_principal_id_credentials_get(principal_id, cursor=cursor, limit=limit, filter=filter, sort=sort, fields=fields, authorization=authorization, x_amesh_csrf=x_amesh_csrf)

List Credentials

### Example


```python
import amesh_client
from amesh_client.models.credential_metadata import CredentialMetadata
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
    api_instance = amesh_client.CredentialsApi(api_client)
    principal_id = UUID('38400000-8cf0-11bd-b23e-10b96e4ef00d') # UUID |
    cursor = 'cursor_example' # str | Opaque cursor from the prior page (optional)
    limit = 56 # int |  (optional)
    filter = ['filter_example'] # List[str] | Repeatable top-level equality filter in field=value form (optional)
    sort = 'sort_example' # str | Comma-separated top-level fields; prefix descending fields with - (optional)
    fields = 'fields_example' # str | Comma-separated top-level response fields (optional)
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)

    try:
        # List Credentials
        api_response = api_instance.list_credentials_api_v1_admin_principals_principal_id_credentials_get(principal_id, cursor=cursor, limit=limit, filter=filter, sort=sort, fields=fields, authorization=authorization, x_amesh_csrf=x_amesh_csrf)
        print("The response of CredentialsApi->list_credentials_api_v1_admin_principals_principal_id_credentials_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CredentialsApi->list_credentials_api_v1_admin_principals_principal_id_credentials_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **principal_id** | **UUID**|  |
 **cursor** | **str**| Opaque cursor from the prior page | [optional]
 **limit** | **int**|  | [optional]
 **filter** | [**List[str]**](str.md)| Repeatable top-level equality filter in field&#x3D;value form | [optional]
 **sort** | **str**| Comma-separated top-level fields; prefix descending fields with - | [optional]
 **fields** | **str**| Comma-separated top-level response fields | [optional]
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]

### Return type

[**List[CredentialMetadata]**](CredentialMetadata.md)

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

# **revoke_all_credentials_api_v1_admin_principals_principal_id_credentials_delete**
> RevokedCredentialsResponse revoke_all_credentials_api_v1_admin_principals_principal_id_credentials_delete(principal_id, authorization=authorization, x_amesh_csrf=x_amesh_csrf)

Revoke All Credentials

### Example


```python
import amesh_client
from amesh_client.models.revoked_credentials_response import RevokedCredentialsResponse
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
    api_instance = amesh_client.CredentialsApi(api_client)
    principal_id = UUID('38400000-8cf0-11bd-b23e-10b96e4ef00d') # UUID |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)

    try:
        # Revoke All Credentials
        api_response = api_instance.revoke_all_credentials_api_v1_admin_principals_principal_id_credentials_delete(principal_id, authorization=authorization, x_amesh_csrf=x_amesh_csrf)
        print("The response of CredentialsApi->revoke_all_credentials_api_v1_admin_principals_principal_id_credentials_delete:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CredentialsApi->revoke_all_credentials_api_v1_admin_principals_principal_id_credentials_delete: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **principal_id** | **UUID**|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]

### Return type

**RevokedCredentialsResponse**

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

# **revoke_credential_api_v1_admin_credentials_credential_id_delete**
> RevokedCredentialsResponse revoke_credential_api_v1_admin_credentials_credential_id_delete(credential_id, authorization=authorization, x_amesh_csrf=x_amesh_csrf)

Revoke Credential

### Example


```python
import amesh_client
from amesh_client.models.revoked_credentials_response import RevokedCredentialsResponse
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
    api_instance = amesh_client.CredentialsApi(api_client)
    credential_id = UUID('38400000-8cf0-11bd-b23e-10b96e4ef00d') # UUID |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)

    try:
        # Revoke Credential
        api_response = api_instance.revoke_credential_api_v1_admin_credentials_credential_id_delete(credential_id, authorization=authorization, x_amesh_csrf=x_amesh_csrf)
        print("The response of CredentialsApi->revoke_credential_api_v1_admin_credentials_credential_id_delete:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CredentialsApi->revoke_credential_api_v1_admin_credentials_credential_id_delete: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **credential_id** | **UUID**|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]

### Return type

**RevokedCredentialsResponse**

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

# **rotate_credential_api_v1_admin_credentials_credential_id_rotate_post**
> IssuedCredentialResponse rotate_credential_api_v1_admin_credentials_credential_id_rotate_post(credential_id, rotate_credential_request, authorization=authorization, x_amesh_csrf=x_amesh_csrf)

Rotate Credential

### Example


```python
import amesh_client
from amesh_client.models.issued_credential_response import IssuedCredentialResponse
from amesh_client.models.rotate_credential_request import RotateCredentialRequest
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
    api_instance = amesh_client.CredentialsApi(api_client)
    credential_id = UUID('38400000-8cf0-11bd-b23e-10b96e4ef00d') # UUID |
    rotate_credential_request = amesh_client.RotateCredentialRequest() # RotateCredentialRequest |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)

    try:
        # Rotate Credential
        api_response = api_instance.rotate_credential_api_v1_admin_credentials_credential_id_rotate_post(credential_id, rotate_credential_request, authorization=authorization, x_amesh_csrf=x_amesh_csrf)
        print("The response of CredentialsApi->rotate_credential_api_v1_admin_credentials_credential_id_rotate_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling CredentialsApi->rotate_credential_api_v1_admin_credentials_credential_id_rotate_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **credential_id** | **UUID**|  |
 **rotate_credential_request** | **RotateCredentialRequest**|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]

### Return type

**IssuedCredentialResponse**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)
