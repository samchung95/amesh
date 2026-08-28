# amesh_client.AuthorizationApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**add_group_member_api_v1_admin_groups_group_id_members_member_id_put**](AuthorizationApi.md#add_group_member_api_v1_admin_groups_group_id_members_member_id_put) | **PUT** /api/v1/admin/groups/{group_id}/members/{member_id} | Add Group Member
[**create_principal_api_v1_admin_principals_post**](AuthorizationApi.md#create_principal_api_v1_admin_principals_post) | **POST** /api/v1/admin/principals | Create Principal
[**create_role_binding_api_v1_admin_bindings_post**](AuthorizationApi.md#create_role_binding_api_v1_admin_bindings_post) | **POST** /api/v1/admin/bindings | Create Role Binding
[**delete_role_binding_api_v1_admin_bindings_binding_id_delete**](AuthorizationApi.md#delete_role_binding_api_v1_admin_bindings_binding_id_delete) | **DELETE** /api/v1/admin/bindings/{binding_id} | Delete Role Binding
[**explain_authorization_api_v1_authorization_explain_post**](AuthorizationApi.md#explain_authorization_api_v1_authorization_explain_post) | **POST** /api/v1/authorization/explain | Explain Authorization
[**list_principals_api_v1_admin_principals_get**](AuthorizationApi.md#list_principals_api_v1_admin_principals_get) | **GET** /api/v1/admin/principals | List Principals
[**list_role_bindings_api_v1_admin_bindings_get**](AuthorizationApi.md#list_role_bindings_api_v1_admin_bindings_get) | **GET** /api/v1/admin/bindings | List Role Bindings
[**list_roles_api_v1_admin_roles_get**](AuthorizationApi.md#list_roles_api_v1_admin_roles_get) | **GET** /api/v1/admin/roles | List Roles
[**remove_group_member_api_v1_admin_groups_group_id_members_member_id_delete**](AuthorizationApi.md#remove_group_member_api_v1_admin_groups_group_id_members_member_id_delete) | **DELETE** /api/v1/admin/groups/{group_id}/members/{member_id} | Remove Group Member
[**set_namespace_authorization_boundary_api_v1_admin_tenants_tenant_id_namespaces_namespace_authorization_boundary_put**](AuthorizationApi.md#set_namespace_authorization_boundary_api_v1_admin_tenants_tenant_id_namespaces_namespace_authorization_boundary_put) | **PUT** /api/v1/admin/tenants/{tenant_id}/namespaces/{namespace}/authorization-boundary | Set Namespace Authorization Boundary
[**upsert_role_api_v1_admin_roles_role_name_put**](AuthorizationApi.md#upsert_role_api_v1_admin_roles_role_name_put) | **PUT** /api/v1/admin/roles/{role_name} | Upsert Role


# **add_group_member_api_v1_admin_groups_group_id_members_member_id_put**
> add_group_member_api_v1_admin_groups_group_id_members_member_id_put(group_id, member_id, authorization=authorization, x_amesh_csrf=x_amesh_csrf)

Add Group Member

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
    api_instance = amesh_client.AuthorizationApi(api_client)
    group_id = UUID('38400000-8cf0-11bd-b23e-10b96e4ef00d') # UUID |
    member_id = UUID('38400000-8cf0-11bd-b23e-10b96e4ef00d') # UUID |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)

    try:
        # Add Group Member
        api_instance.add_group_member_api_v1_admin_groups_group_id_members_member_id_put(group_id, member_id, authorization=authorization, x_amesh_csrf=x_amesh_csrf)
    except Exception as e:
        print("Exception when calling AuthorizationApi->add_group_member_api_v1_admin_groups_group_id_members_member_id_put: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **group_id** | **UUID**|  |
 **member_id** | **UUID**|  |
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

# **create_principal_api_v1_admin_principals_post**
> PrincipalDefinition create_principal_api_v1_admin_principals_post(principal_definition, authorization=authorization, x_amesh_csrf=x_amesh_csrf)

Create Principal

### Example


```python
import amesh_client
from amesh_client.models.principal_definition import PrincipalDefinition
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
    api_instance = amesh_client.AuthorizationApi(api_client)
    principal_definition = amesh_client.PrincipalDefinition() # PrincipalDefinition |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)

    try:
        # Create Principal
        api_response = api_instance.create_principal_api_v1_admin_principals_post(principal_definition, authorization=authorization, x_amesh_csrf=x_amesh_csrf)
        print("The response of AuthorizationApi->create_principal_api_v1_admin_principals_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AuthorizationApi->create_principal_api_v1_admin_principals_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **principal_definition** | **PrincipalDefinition**|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]

### Return type

**PrincipalDefinition**

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

# **create_role_binding_api_v1_admin_bindings_post**
> RoleBinding create_role_binding_api_v1_admin_bindings_post(role_binding, authorization=authorization, x_amesh_csrf=x_amesh_csrf)

Create Role Binding

### Example


```python
import amesh_client
from amesh_client.models.role_binding import RoleBinding
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
    api_instance = amesh_client.AuthorizationApi(api_client)
    role_binding = amesh_client.RoleBinding() # RoleBinding |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)

    try:
        # Create Role Binding
        api_response = api_instance.create_role_binding_api_v1_admin_bindings_post(role_binding, authorization=authorization, x_amesh_csrf=x_amesh_csrf)
        print("The response of AuthorizationApi->create_role_binding_api_v1_admin_bindings_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AuthorizationApi->create_role_binding_api_v1_admin_bindings_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **role_binding** | **RoleBinding**|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]

### Return type

**RoleBinding**

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

# **delete_role_binding_api_v1_admin_bindings_binding_id_delete**
> delete_role_binding_api_v1_admin_bindings_binding_id_delete(binding_id, x_amesh_tenant=x_amesh_tenant, x_amesh_namespace=x_amesh_namespace, authorization=authorization, x_amesh_csrf=x_amesh_csrf)

Delete Role Binding

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
    api_instance = amesh_client.AuthorizationApi(api_client)
    binding_id = UUID('38400000-8cf0-11bd-b23e-10b96e4ef00d') # UUID |
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)
    x_amesh_namespace = 'x_amesh_namespace_example' # str |  (optional)
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)

    try:
        # Delete Role Binding
        api_instance.delete_role_binding_api_v1_admin_bindings_binding_id_delete(binding_id, x_amesh_tenant=x_amesh_tenant, x_amesh_namespace=x_amesh_namespace, authorization=authorization, x_amesh_csrf=x_amesh_csrf)
    except Exception as e:
        print("Exception when calling AuthorizationApi->delete_role_binding_api_v1_admin_bindings_binding_id_delete: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **binding_id** | **UUID**|  |
 **x_amesh_tenant** | **str**|  | [optional]
 **x_amesh_namespace** | **str**|  | [optional]
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

# **explain_authorization_api_v1_authorization_explain_post**
> AuthorizationDecision explain_authorization_api_v1_authorization_explain_post(authorization_explanation_request, authorization=authorization, x_amesh_csrf=x_amesh_csrf)

Explain Authorization

### Example


```python
import amesh_client
from amesh_client.models.authorization_decision import AuthorizationDecision
from amesh_client.models.authorization_explanation_request import AuthorizationExplanationRequest
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
    api_instance = amesh_client.AuthorizationApi(api_client)
    authorization_explanation_request = amesh_client.AuthorizationExplanationRequest() # AuthorizationExplanationRequest |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)

    try:
        # Explain Authorization
        api_response = api_instance.explain_authorization_api_v1_authorization_explain_post(authorization_explanation_request, authorization=authorization, x_amesh_csrf=x_amesh_csrf)
        print("The response of AuthorizationApi->explain_authorization_api_v1_authorization_explain_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AuthorizationApi->explain_authorization_api_v1_authorization_explain_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **authorization_explanation_request** | **AuthorizationExplanationRequest**|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]

### Return type

**AuthorizationDecision**

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

# **list_principals_api_v1_admin_principals_get**
> List[PrincipalDefinition] list_principals_api_v1_admin_principals_get(cursor=cursor, limit=limit, filter=filter, sort=sort, fields=fields, authorization=authorization, x_amesh_csrf=x_amesh_csrf)

List Principals

### Example


```python
import amesh_client
from amesh_client.models.principal_definition import PrincipalDefinition
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
    api_instance = amesh_client.AuthorizationApi(api_client)
    cursor = 'cursor_example' # str | Opaque cursor from the prior page (optional)
    limit = 56 # int |  (optional)
    filter = ['filter_example'] # List[str] | Repeatable top-level equality filter in field=value form (optional)
    sort = 'sort_example' # str | Comma-separated top-level fields; prefix descending fields with - (optional)
    fields = 'fields_example' # str | Comma-separated top-level response fields (optional)
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)

    try:
        # List Principals
        api_response = api_instance.list_principals_api_v1_admin_principals_get(cursor=cursor, limit=limit, filter=filter, sort=sort, fields=fields, authorization=authorization, x_amesh_csrf=x_amesh_csrf)
        print("The response of AuthorizationApi->list_principals_api_v1_admin_principals_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AuthorizationApi->list_principals_api_v1_admin_principals_get: %s\n" % e)
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

[**List[PrincipalDefinition]**](PrincipalDefinition.md)

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

# **list_role_bindings_api_v1_admin_bindings_get**
> List[RoleBinding] list_role_bindings_api_v1_admin_bindings_get(cursor=cursor, limit=limit, filter=filter, sort=sort, fields=fields, authorization=authorization, x_amesh_csrf=x_amesh_csrf)

List Role Bindings

### Example


```python
import amesh_client
from amesh_client.models.role_binding import RoleBinding
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
    api_instance = amesh_client.AuthorizationApi(api_client)
    cursor = 'cursor_example' # str | Opaque cursor from the prior page (optional)
    limit = 56 # int |  (optional)
    filter = ['filter_example'] # List[Optional[str]] | Repeatable top-level equality filter in field=value form (optional)
    sort = 'sort_example' # str | Comma-separated top-level fields; prefix descending fields with - (optional)
    fields = 'fields_example' # str | Comma-separated top-level response fields (optional)
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)

    try:
        # List Role Bindings
        api_response = api_instance.list_role_bindings_api_v1_admin_bindings_get(cursor=cursor, limit=limit, filter=filter, sort=sort, fields=fields, authorization=authorization, x_amesh_csrf=x_amesh_csrf)
        print("The response of AuthorizationApi->list_role_bindings_api_v1_admin_bindings_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AuthorizationApi->list_role_bindings_api_v1_admin_bindings_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **cursor** | **str**| Opaque cursor from the prior page | [optional]
 **limit** | **int**|  | [optional]
 **filter** | [**List[Optional[str]]**](str.md)| Repeatable top-level equality filter in field&#x3D;value form | [optional]
 **sort** | **str**| Comma-separated top-level fields; prefix descending fields with - | [optional]
 **fields** | **str**| Comma-separated top-level response fields | [optional]
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]

### Return type

[**List[RoleBinding]**](RoleBinding.md)

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

# **list_roles_api_v1_admin_roles_get**
> List[RoleDefinition] list_roles_api_v1_admin_roles_get(cursor=cursor, limit=limit, filter=filter, sort=sort, fields=fields, authorization=authorization, x_amesh_csrf=x_amesh_csrf)

List Roles

### Example


```python
import amesh_client
from amesh_client.models.role_definition import RoleDefinition
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
    api_instance = amesh_client.AuthorizationApi(api_client)
    cursor = 'cursor_example' # str | Opaque cursor from the prior page (optional)
    limit = 56 # int |  (optional)
    filter = ['filter_example'] # List[str] | Repeatable top-level equality filter in field=value form (optional)
    sort = 'sort_example' # str | Comma-separated top-level fields; prefix descending fields with - (optional)
    fields = 'fields_example' # str | Comma-separated top-level response fields (optional)
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)

    try:
        # List Roles
        api_response = api_instance.list_roles_api_v1_admin_roles_get(cursor=cursor, limit=limit, filter=filter, sort=sort, fields=fields, authorization=authorization, x_amesh_csrf=x_amesh_csrf)
        print("The response of AuthorizationApi->list_roles_api_v1_admin_roles_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AuthorizationApi->list_roles_api_v1_admin_roles_get: %s\n" % e)
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

[**List[RoleDefinition]**](RoleDefinition.md)

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

# **remove_group_member_api_v1_admin_groups_group_id_members_member_id_delete**
> remove_group_member_api_v1_admin_groups_group_id_members_member_id_delete(group_id, member_id, authorization=authorization, x_amesh_csrf=x_amesh_csrf)

Remove Group Member

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
    api_instance = amesh_client.AuthorizationApi(api_client)
    group_id = UUID('38400000-8cf0-11bd-b23e-10b96e4ef00d') # UUID |
    member_id = UUID('38400000-8cf0-11bd-b23e-10b96e4ef00d') # UUID |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)

    try:
        # Remove Group Member
        api_instance.remove_group_member_api_v1_admin_groups_group_id_members_member_id_delete(group_id, member_id, authorization=authorization, x_amesh_csrf=x_amesh_csrf)
    except Exception as e:
        print("Exception when calling AuthorizationApi->remove_group_member_api_v1_admin_groups_group_id_members_member_id_delete: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **group_id** | **UUID**|  |
 **member_id** | **UUID**|  |
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

# **set_namespace_authorization_boundary_api_v1_admin_tenants_tenant_id_namespaces_namespace_authorization_boundary_put**
> NamespaceAuthorizationBoundary set_namespace_authorization_boundary_api_v1_admin_tenants_tenant_id_namespaces_namespace_authorization_boundary_put(tenant_id, namespace, authorization=authorization, x_amesh_csrf=x_amesh_csrf)

Set Namespace Authorization Boundary

### Example


```python
import amesh_client
from amesh_client.models.namespace_authorization_boundary import NamespaceAuthorizationBoundary
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
    api_instance = amesh_client.AuthorizationApi(api_client)
    tenant_id = 'tenant_id_example' # str |
    namespace = 'namespace_example' # str |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)

    try:
        # Set Namespace Authorization Boundary
        api_response = api_instance.set_namespace_authorization_boundary_api_v1_admin_tenants_tenant_id_namespaces_namespace_authorization_boundary_put(tenant_id, namespace, authorization=authorization, x_amesh_csrf=x_amesh_csrf)
        print("The response of AuthorizationApi->set_namespace_authorization_boundary_api_v1_admin_tenants_tenant_id_namespaces_namespace_authorization_boundary_put:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AuthorizationApi->set_namespace_authorization_boundary_api_v1_admin_tenants_tenant_id_namespaces_namespace_authorization_boundary_put: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **tenant_id** | **str**|  |
 **namespace** | **str**|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]

### Return type

**NamespaceAuthorizationBoundary**

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

# **upsert_role_api_v1_admin_roles_role_name_put**
> RoleDefinition upsert_role_api_v1_admin_roles_role_name_put(role_name, role_definition, authorization=authorization, x_amesh_csrf=x_amesh_csrf)

Upsert Role

### Example


```python
import amesh_client
from amesh_client.models.role_definition import RoleDefinition
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
    api_instance = amesh_client.AuthorizationApi(api_client)
    role_name = 'role_name_example' # str |
    role_definition = amesh_client.RoleDefinition() # RoleDefinition |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)

    try:
        # Upsert Role
        api_response = api_instance.upsert_role_api_v1_admin_roles_role_name_put(role_name, role_definition, authorization=authorization, x_amesh_csrf=x_amesh_csrf)
        print("The response of AuthorizationApi->upsert_role_api_v1_admin_roles_role_name_put:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AuthorizationApi->upsert_role_api_v1_admin_roles_role_name_put: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **role_name** | **str**|  |
 **role_definition** | **RoleDefinition**|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]

### Return type

**RoleDefinition**

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
