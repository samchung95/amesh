# amesh_client.TenantsApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_tenant_api_v1_admin_tenants_post**](TenantsApi.md#create_tenant_api_v1_admin_tenants_post) | **POST** /api/v1/admin/tenants | Create Tenant
[**delete_tenant_api_v1_admin_tenants_tenant_slug_delete**](TenantsApi.md#delete_tenant_api_v1_admin_tenants_tenant_slug_delete) | **DELETE** /api/v1/admin/tenants/{tenant_slug} | Delete Tenant
[**export_tenant_api_v1_admin_tenants_tenant_slug_exports_post**](TenantsApi.md#export_tenant_api_v1_admin_tenants_tenant_slug_exports_post) | **POST** /api/v1/admin/tenants/{tenant_slug}/exports | Export Tenant
[**get_tenant_api_v1_admin_tenants_tenant_slug_get**](TenantsApi.md#get_tenant_api_v1_admin_tenants_tenant_slug_get) | **GET** /api/v1/admin/tenants/{tenant_slug} | Get Tenant
[**list_tenants_api_v1_admin_tenants_get**](TenantsApi.md#list_tenants_api_v1_admin_tenants_get) | **GET** /api/v1/admin/tenants | List Tenants
[**restore_tenant_api_v1_admin_tenants_tenant_slug_restore_post**](TenantsApi.md#restore_tenant_api_v1_admin_tenants_tenant_slug_restore_post) | **POST** /api/v1/admin/tenants/{tenant_slug}/restore | Restore Tenant
[**suspend_tenant_api_v1_admin_tenants_tenant_slug_suspend_post**](TenantsApi.md#suspend_tenant_api_v1_admin_tenants_tenant_slug_suspend_post) | **POST** /api/v1/admin/tenants/{tenant_slug}/suspend | Suspend Tenant
[**update_tenant_policy_api_v1_admin_tenants_tenant_slug_policy_put**](TenantsApi.md#update_tenant_policy_api_v1_admin_tenants_tenant_slug_policy_put) | **PUT** /api/v1/admin/tenants/{tenant_slug}/policy | Update Tenant Policy


# **create_tenant_api_v1_admin_tenants_post**
> TenantDefinition create_tenant_api_v1_admin_tenants_post(create_tenant_request, authorization=authorization, x_amesh_csrf=x_amesh_csrf)

Create Tenant

### Example


```python
import amesh_client
from amesh_client.models.create_tenant_request import CreateTenantRequest
from amesh_client.models.tenant_definition import TenantDefinition
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
    api_instance = amesh_client.TenantsApi(api_client)
    create_tenant_request = amesh_client.CreateTenantRequest() # CreateTenantRequest |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)

    try:
        # Create Tenant
        api_response = api_instance.create_tenant_api_v1_admin_tenants_post(create_tenant_request, authorization=authorization, x_amesh_csrf=x_amesh_csrf)
        print("The response of TenantsApi->create_tenant_api_v1_admin_tenants_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TenantsApi->create_tenant_api_v1_admin_tenants_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **create_tenant_request** | **CreateTenantRequest**|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]

### Return type

**TenantDefinition**

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

# **delete_tenant_api_v1_admin_tenants_tenant_slug_delete**
> TenantDefinition delete_tenant_api_v1_admin_tenants_tenant_slug_delete(tenant_slug, authorization=authorization, x_amesh_csrf=x_amesh_csrf)

Delete Tenant

### Example


```python
import amesh_client
from amesh_client.models.tenant_definition import TenantDefinition
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
    api_instance = amesh_client.TenantsApi(api_client)
    tenant_slug = 'tenant_slug_example' # str |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)

    try:
        # Delete Tenant
        api_response = api_instance.delete_tenant_api_v1_admin_tenants_tenant_slug_delete(tenant_slug, authorization=authorization, x_amesh_csrf=x_amesh_csrf)
        print("The response of TenantsApi->delete_tenant_api_v1_admin_tenants_tenant_slug_delete:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TenantsApi->delete_tenant_api_v1_admin_tenants_tenant_slug_delete: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **tenant_slug** | **str**|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]

### Return type

**TenantDefinition**

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

# **export_tenant_api_v1_admin_tenants_tenant_slug_exports_post**
> TenantExport export_tenant_api_v1_admin_tenants_tenant_slug_exports_post(tenant_slug, authorization=authorization, x_amesh_csrf=x_amesh_csrf)

Export Tenant

### Example


```python
import amesh_client
from amesh_client.models.tenant_export import TenantExport
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
    api_instance = amesh_client.TenantsApi(api_client)
    tenant_slug = 'tenant_slug_example' # str |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)

    try:
        # Export Tenant
        api_response = api_instance.export_tenant_api_v1_admin_tenants_tenant_slug_exports_post(tenant_slug, authorization=authorization, x_amesh_csrf=x_amesh_csrf)
        print("The response of TenantsApi->export_tenant_api_v1_admin_tenants_tenant_slug_exports_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TenantsApi->export_tenant_api_v1_admin_tenants_tenant_slug_exports_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **tenant_slug** | **str**|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]

### Return type

**TenantExport**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_tenant_api_v1_admin_tenants_tenant_slug_get**
> TenantDefinition get_tenant_api_v1_admin_tenants_tenant_slug_get(tenant_slug, authorization=authorization, x_amesh_csrf=x_amesh_csrf)

Get Tenant

### Example


```python
import amesh_client
from amesh_client.models.tenant_definition import TenantDefinition
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
    api_instance = amesh_client.TenantsApi(api_client)
    tenant_slug = 'tenant_slug_example' # str |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)

    try:
        # Get Tenant
        api_response = api_instance.get_tenant_api_v1_admin_tenants_tenant_slug_get(tenant_slug, authorization=authorization, x_amesh_csrf=x_amesh_csrf)
        print("The response of TenantsApi->get_tenant_api_v1_admin_tenants_tenant_slug_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TenantsApi->get_tenant_api_v1_admin_tenants_tenant_slug_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **tenant_slug** | **str**|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]

### Return type

**TenantDefinition**

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

# **list_tenants_api_v1_admin_tenants_get**
> List[TenantDefinition] list_tenants_api_v1_admin_tenants_get(cursor=cursor, limit=limit, filter=filter, sort=sort, fields=fields, authorization=authorization, x_amesh_csrf=x_amesh_csrf)

List Tenants

### Example


```python
import amesh_client
from amesh_client.models.tenant_definition import TenantDefinition
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
    api_instance = amesh_client.TenantsApi(api_client)
    cursor = 'cursor_example' # str | Opaque cursor from the prior page (optional)
    limit = 56 # int |  (optional)
    filter = ['filter_example'] # List[str] | Repeatable top-level equality filter in field=value form (optional)
    sort = 'sort_example' # str | Comma-separated top-level fields; prefix descending fields with - (optional)
    fields = 'fields_example' # str | Comma-separated top-level response fields (optional)
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)

    try:
        # List Tenants
        api_response = api_instance.list_tenants_api_v1_admin_tenants_get(cursor=cursor, limit=limit, filter=filter, sort=sort, fields=fields, authorization=authorization, x_amesh_csrf=x_amesh_csrf)
        print("The response of TenantsApi->list_tenants_api_v1_admin_tenants_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TenantsApi->list_tenants_api_v1_admin_tenants_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **cursor** | **str**| Opaque cursor from the prior page | [optional]
 **limit** | **int**|  | [optional]
 **filter** | [**List[str]**](str.md)| Repeatable top-level equality filter in field&#x3D;value form | [optional]
 **sort** | **str**| Comma-separated top-level fields; prefix descending fields with - | [optional]
 **fields** | **str**| Comma-separated top-level response fields | [optional]
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]

### Return type

[**List[TenantDefinition]**](TenantDefinition.md)

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

# **restore_tenant_api_v1_admin_tenants_tenant_slug_restore_post**
> TenantDefinition restore_tenant_api_v1_admin_tenants_tenant_slug_restore_post(tenant_slug, authorization=authorization, x_amesh_csrf=x_amesh_csrf)

Restore Tenant

### Example


```python
import amesh_client
from amesh_client.models.tenant_definition import TenantDefinition
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
    api_instance = amesh_client.TenantsApi(api_client)
    tenant_slug = 'tenant_slug_example' # str |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)

    try:
        # Restore Tenant
        api_response = api_instance.restore_tenant_api_v1_admin_tenants_tenant_slug_restore_post(tenant_slug, authorization=authorization, x_amesh_csrf=x_amesh_csrf)
        print("The response of TenantsApi->restore_tenant_api_v1_admin_tenants_tenant_slug_restore_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TenantsApi->restore_tenant_api_v1_admin_tenants_tenant_slug_restore_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **tenant_slug** | **str**|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]

### Return type

**TenantDefinition**

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

# **suspend_tenant_api_v1_admin_tenants_tenant_slug_suspend_post**
> TenantDefinition suspend_tenant_api_v1_admin_tenants_tenant_slug_suspend_post(tenant_slug, authorization=authorization, x_amesh_csrf=x_amesh_csrf)

Suspend Tenant

### Example


```python
import amesh_client
from amesh_client.models.tenant_definition import TenantDefinition
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
    api_instance = amesh_client.TenantsApi(api_client)
    tenant_slug = 'tenant_slug_example' # str |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)

    try:
        # Suspend Tenant
        api_response = api_instance.suspend_tenant_api_v1_admin_tenants_tenant_slug_suspend_post(tenant_slug, authorization=authorization, x_amesh_csrf=x_amesh_csrf)
        print("The response of TenantsApi->suspend_tenant_api_v1_admin_tenants_tenant_slug_suspend_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TenantsApi->suspend_tenant_api_v1_admin_tenants_tenant_slug_suspend_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **tenant_slug** | **str**|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]

### Return type

**TenantDefinition**

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

# **update_tenant_policy_api_v1_admin_tenants_tenant_slug_policy_put**
> TenantDefinition update_tenant_policy_api_v1_admin_tenants_tenant_slug_policy_put(tenant_slug, tenant_policy, authorization=authorization, x_amesh_csrf=x_amesh_csrf)

Update Tenant Policy

### Example


```python
import amesh_client
from amesh_client.models.tenant_definition import TenantDefinition
from amesh_client.models.tenant_policy import TenantPolicy
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
    api_instance = amesh_client.TenantsApi(api_client)
    tenant_slug = 'tenant_slug_example' # str |
    tenant_policy = amesh_client.TenantPolicy() # TenantPolicy |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)

    try:
        # Update Tenant Policy
        api_response = api_instance.update_tenant_policy_api_v1_admin_tenants_tenant_slug_policy_put(tenant_slug, tenant_policy, authorization=authorization, x_amesh_csrf=x_amesh_csrf)
        print("The response of TenantsApi->update_tenant_policy_api_v1_admin_tenants_tenant_slug_policy_put:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TenantsApi->update_tenant_policy_api_v1_admin_tenants_tenant_slug_policy_put: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **tenant_slug** | **str**|  |
 **tenant_policy** | **TenantPolicy**|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]

### Return type

**TenantDefinition**

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
