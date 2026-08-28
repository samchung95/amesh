# amesh_client.ScimApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_scim_group_scim_v2_groups_post**](ScimApi.md#create_scim_group_scim_v2_groups_post) | **POST** /scim/v2/Groups | Create Scim Group
[**create_scim_user_scim_v2_users_post**](ScimApi.md#create_scim_user_scim_v2_users_post) | **POST** /scim/v2/Users | Create Scim User
[**delete_scim_group_scim_v2_groups_group_id_delete**](ScimApi.md#delete_scim_group_scim_v2_groups_group_id_delete) | **DELETE** /scim/v2/Groups/{group_id} | Delete Scim Group
[**delete_scim_user_scim_v2_users_user_id_delete**](ScimApi.md#delete_scim_user_scim_v2_users_user_id_delete) | **DELETE** /scim/v2/Users/{user_id} | Delete Scim User
[**get_scim_group_scim_v2_groups_group_id_get**](ScimApi.md#get_scim_group_scim_v2_groups_group_id_get) | **GET** /scim/v2/Groups/{group_id} | Get Scim Group
[**get_scim_user_scim_v2_users_user_id_get**](ScimApi.md#get_scim_user_scim_v2_users_user_id_get) | **GET** /scim/v2/Users/{user_id} | Get Scim User
[**list_scim_groups_scim_v2_groups_get**](ScimApi.md#list_scim_groups_scim_v2_groups_get) | **GET** /scim/v2/Groups | List Scim Groups
[**list_scim_users_scim_v2_users_get**](ScimApi.md#list_scim_users_scim_v2_users_get) | **GET** /scim/v2/Users | List Scim Users
[**patch_scim_group_scim_v2_groups_group_id_patch**](ScimApi.md#patch_scim_group_scim_v2_groups_group_id_patch) | **PATCH** /scim/v2/Groups/{group_id} | Patch Scim Group
[**patch_scim_user_scim_v2_users_user_id_patch**](ScimApi.md#patch_scim_user_scim_v2_users_user_id_patch) | **PATCH** /scim/v2/Users/{user_id} | Patch Scim User
[**scim_service_provider_config_scim_v2_service_provider_config_get**](ScimApi.md#scim_service_provider_config_scim_v2_service_provider_config_get) | **GET** /scim/v2/ServiceProviderConfig | Scim Service Provider Config


# **create_scim_group_scim_v2_groups_post**
> ScimGroupResource create_scim_group_scim_v2_groups_post(scim_group_request, authorization=authorization)

Create Scim Group

### Example


```python
import amesh_client
from amesh_client.models.scim_group_request import ScimGroupRequest
from amesh_client.models.scim_group_resource import ScimGroupResource
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
    api_instance = amesh_client.ScimApi(api_client)
    scim_group_request = amesh_client.ScimGroupRequest() # ScimGroupRequest |
    authorization = 'authorization_example' # str |  (optional)

    try:
        # Create Scim Group
        api_response = api_instance.create_scim_group_scim_v2_groups_post(scim_group_request, authorization=authorization)
        print("The response of ScimApi->create_scim_group_scim_v2_groups_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ScimApi->create_scim_group_scim_v2_groups_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **scim_group_request** | **ScimGroupRequest**|  |
 **authorization** | **str**|  | [optional]

### Return type

**ScimGroupResource**

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

# **create_scim_user_scim_v2_users_post**
> ScimUserResource create_scim_user_scim_v2_users_post(scim_user_request, authorization=authorization)

Create Scim User

### Example


```python
import amesh_client
from amesh_client.models.scim_user_request import ScimUserRequest
from amesh_client.models.scim_user_resource import ScimUserResource
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
    api_instance = amesh_client.ScimApi(api_client)
    scim_user_request = amesh_client.ScimUserRequest() # ScimUserRequest |
    authorization = 'authorization_example' # str |  (optional)

    try:
        # Create Scim User
        api_response = api_instance.create_scim_user_scim_v2_users_post(scim_user_request, authorization=authorization)
        print("The response of ScimApi->create_scim_user_scim_v2_users_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ScimApi->create_scim_user_scim_v2_users_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **scim_user_request** | **ScimUserRequest**|  |
 **authorization** | **str**|  | [optional]

### Return type

**ScimUserResource**

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

# **delete_scim_group_scim_v2_groups_group_id_delete**
> delete_scim_group_scim_v2_groups_group_id_delete(group_id, authorization=authorization)

Delete Scim Group

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
    api_instance = amesh_client.ScimApi(api_client)
    group_id = UUID('38400000-8cf0-11bd-b23e-10b96e4ef00d') # UUID |
    authorization = 'authorization_example' # str |  (optional)

    try:
        # Delete Scim Group
        api_instance.delete_scim_group_scim_v2_groups_group_id_delete(group_id, authorization=authorization)
    except Exception as e:
        print("Exception when calling ScimApi->delete_scim_group_scim_v2_groups_group_id_delete: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **group_id** | **UUID**|  |
 **authorization** | **str**|  | [optional]

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

# **delete_scim_user_scim_v2_users_user_id_delete**
> delete_scim_user_scim_v2_users_user_id_delete(user_id, authorization=authorization)

Delete Scim User

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
    api_instance = amesh_client.ScimApi(api_client)
    user_id = UUID('38400000-8cf0-11bd-b23e-10b96e4ef00d') # UUID |
    authorization = 'authorization_example' # str |  (optional)

    try:
        # Delete Scim User
        api_instance.delete_scim_user_scim_v2_users_user_id_delete(user_id, authorization=authorization)
    except Exception as e:
        print("Exception when calling ScimApi->delete_scim_user_scim_v2_users_user_id_delete: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **user_id** | **UUID**|  |
 **authorization** | **str**|  | [optional]

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

# **get_scim_group_scim_v2_groups_group_id_get**
> ScimGroupResource get_scim_group_scim_v2_groups_group_id_get(group_id, authorization=authorization)

Get Scim Group

### Example


```python
import amesh_client
from amesh_client.models.scim_group_resource import ScimGroupResource
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
    api_instance = amesh_client.ScimApi(api_client)
    group_id = UUID('38400000-8cf0-11bd-b23e-10b96e4ef00d') # UUID |
    authorization = 'authorization_example' # str |  (optional)

    try:
        # Get Scim Group
        api_response = api_instance.get_scim_group_scim_v2_groups_group_id_get(group_id, authorization=authorization)
        print("The response of ScimApi->get_scim_group_scim_v2_groups_group_id_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ScimApi->get_scim_group_scim_v2_groups_group_id_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **group_id** | **UUID**|  |
 **authorization** | **str**|  | [optional]

### Return type

**ScimGroupResource**

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

# **get_scim_user_scim_v2_users_user_id_get**
> ScimUserResource get_scim_user_scim_v2_users_user_id_get(user_id, authorization=authorization)

Get Scim User

### Example


```python
import amesh_client
from amesh_client.models.scim_user_resource import ScimUserResource
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
    api_instance = amesh_client.ScimApi(api_client)
    user_id = UUID('38400000-8cf0-11bd-b23e-10b96e4ef00d') # UUID |
    authorization = 'authorization_example' # str |  (optional)

    try:
        # Get Scim User
        api_response = api_instance.get_scim_user_scim_v2_users_user_id_get(user_id, authorization=authorization)
        print("The response of ScimApi->get_scim_user_scim_v2_users_user_id_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ScimApi->get_scim_user_scim_v2_users_user_id_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **user_id** | **UUID**|  |
 **authorization** | **str**|  | [optional]

### Return type

**ScimUserResource**

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

# **list_scim_groups_scim_v2_groups_get**
> ScimListResponse list_scim_groups_scim_v2_groups_get(filter=filter, start_index=start_index, count=count, authorization=authorization)

List Scim Groups

### Example


```python
import amesh_client
from amesh_client.models.scim_list_response import ScimListResponse
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
    api_instance = amesh_client.ScimApi(api_client)
    filter = 'filter_example' # str |  (optional)
    start_index = 1 # int |  (optional) (default to 1)
    count = 100 # int |  (optional) (default to 100)
    authorization = 'authorization_example' # str |  (optional)

    try:
        # List Scim Groups
        api_response = api_instance.list_scim_groups_scim_v2_groups_get(filter=filter, start_index=start_index, count=count, authorization=authorization)
        print("The response of ScimApi->list_scim_groups_scim_v2_groups_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ScimApi->list_scim_groups_scim_v2_groups_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **filter** | **str**|  | [optional]
 **start_index** | **int**|  | [optional] [default to 1]
 **count** | **int**|  | [optional] [default to 100]
 **authorization** | **str**|  | [optional]

### Return type

**ScimListResponse**

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

# **list_scim_users_scim_v2_users_get**
> ScimListResponse list_scim_users_scim_v2_users_get(filter=filter, start_index=start_index, count=count, authorization=authorization)

List Scim Users

### Example


```python
import amesh_client
from amesh_client.models.scim_list_response import ScimListResponse
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
    api_instance = amesh_client.ScimApi(api_client)
    filter = 'filter_example' # str |  (optional)
    start_index = 1 # int |  (optional) (default to 1)
    count = 100 # int |  (optional) (default to 100)
    authorization = 'authorization_example' # str |  (optional)

    try:
        # List Scim Users
        api_response = api_instance.list_scim_users_scim_v2_users_get(filter=filter, start_index=start_index, count=count, authorization=authorization)
        print("The response of ScimApi->list_scim_users_scim_v2_users_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ScimApi->list_scim_users_scim_v2_users_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **filter** | **str**|  | [optional]
 **start_index** | **int**|  | [optional] [default to 1]
 **count** | **int**|  | [optional] [default to 100]
 **authorization** | **str**|  | [optional]

### Return type

**ScimListResponse**

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

# **patch_scim_group_scim_v2_groups_group_id_patch**
> ScimGroupResource patch_scim_group_scim_v2_groups_group_id_patch(group_id, scim_patch_request, authorization=authorization)

Patch Scim Group

### Example


```python
import amesh_client
from amesh_client.models.scim_group_resource import ScimGroupResource
from amesh_client.models.scim_patch_request import ScimPatchRequest
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
    api_instance = amesh_client.ScimApi(api_client)
    group_id = UUID('38400000-8cf0-11bd-b23e-10b96e4ef00d') # UUID |
    scim_patch_request = amesh_client.ScimPatchRequest() # ScimPatchRequest |
    authorization = 'authorization_example' # str |  (optional)

    try:
        # Patch Scim Group
        api_response = api_instance.patch_scim_group_scim_v2_groups_group_id_patch(group_id, scim_patch_request, authorization=authorization)
        print("The response of ScimApi->patch_scim_group_scim_v2_groups_group_id_patch:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ScimApi->patch_scim_group_scim_v2_groups_group_id_patch: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **group_id** | **UUID**|  |
 **scim_patch_request** | **ScimPatchRequest**|  |
 **authorization** | **str**|  | [optional]

### Return type

**ScimGroupResource**

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

# **patch_scim_user_scim_v2_users_user_id_patch**
> ScimUserResource patch_scim_user_scim_v2_users_user_id_patch(user_id, scim_patch_request, authorization=authorization)

Patch Scim User

### Example


```python
import amesh_client
from amesh_client.models.scim_patch_request import ScimPatchRequest
from amesh_client.models.scim_user_resource import ScimUserResource
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
    api_instance = amesh_client.ScimApi(api_client)
    user_id = UUID('38400000-8cf0-11bd-b23e-10b96e4ef00d') # UUID |
    scim_patch_request = amesh_client.ScimPatchRequest() # ScimPatchRequest |
    authorization = 'authorization_example' # str |  (optional)

    try:
        # Patch Scim User
        api_response = api_instance.patch_scim_user_scim_v2_users_user_id_patch(user_id, scim_patch_request, authorization=authorization)
        print("The response of ScimApi->patch_scim_user_scim_v2_users_user_id_patch:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ScimApi->patch_scim_user_scim_v2_users_user_id_patch: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **user_id** | **UUID**|  |
 **scim_patch_request** | **ScimPatchRequest**|  |
 **authorization** | **str**|  | [optional]

### Return type

**ScimUserResource**

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

# **scim_service_provider_config_scim_v2_service_provider_config_get**
> Dict[str, Optional[object]] scim_service_provider_config_scim_v2_service_provider_config_get(authorization=authorization)

Scim Service Provider Config

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
    api_instance = amesh_client.ScimApi(api_client)
    authorization = 'authorization_example' # str |  (optional)

    try:
        # Scim Service Provider Config
        api_response = api_instance.scim_service_provider_config_scim_v2_service_provider_config_get(authorization=authorization)
        print("The response of ScimApi->scim_service_provider_config_scim_v2_service_provider_config_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ScimApi->scim_service_provider_config_scim_v2_service_provider_config_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **authorization** | **str**|  | [optional]

### Return type

**Dict[str, Optional[object]]**

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
