# amesh_client.AgentSessionTransfersApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**export_agent_profile_transfer_api_v1_admin_agent_session_transfers_profiles_namespace_agent_key_export_get**](AgentSessionTransfersApi.md#export_agent_profile_transfer_api_v1_admin_agent_session_transfers_profiles_namespace_agent_key_export_get) | **GET** /api/v1/admin/agent-session-transfers/profiles/{namespace}/{agent_key}/export | Export Agent Profile Transfer
[**export_agent_profile_transfer_api_v1_admin_agent_session_transfers_profiles_namespace_agent_key_export_post**](AgentSessionTransfersApi.md#export_agent_profile_transfer_api_v1_admin_agent_session_transfers_profiles_namespace_agent_key_export_post) | **POST** /api/v1/admin/agent-session-transfers/profiles/{namespace}/{agent_key}/export | Export Agent Profile Transfer
[**export_agent_session_transfer_api_v1_admin_agent_session_transfers_sessions_session_id_export_post**](AgentSessionTransfersApi.md#export_agent_session_transfer_api_v1_admin_agent_session_transfers_sessions_session_id_export_post) | **POST** /api/v1/admin/agent-session-transfers/sessions/{session_id}/export | Export Agent Session Transfer
[**import_agent_profile_transfer_api_v1_admin_agent_session_transfers_profiles_import_post**](AgentSessionTransfersApi.md#import_agent_profile_transfer_api_v1_admin_agent_session_transfers_profiles_import_post) | **POST** /api/v1/admin/agent-session-transfers/profiles/import | Import Agent Profile Transfer
[**import_agent_session_transfer_api_v1_admin_agent_session_transfers_sessions_import_post**](AgentSessionTransfersApi.md#import_agent_session_transfer_api_v1_admin_agent_session_transfers_sessions_import_post) | **POST** /api/v1/admin/agent-session-transfers/sessions/import | Import Agent Session Transfer
[**plan_agent_profile_transfer_api_v1_admin_agent_session_transfers_profiles_plan_post**](AgentSessionTransfersApi.md#plan_agent_profile_transfer_api_v1_admin_agent_session_transfers_profiles_plan_post) | **POST** /api/v1/admin/agent-session-transfers/profiles/plan | Plan Agent Profile Transfer
[**plan_agent_session_transfer_api_v1_admin_agent_session_transfers_sessions_plan_post**](AgentSessionTransfersApi.md#plan_agent_session_transfer_api_v1_admin_agent_session_transfers_sessions_plan_post) | **POST** /api/v1/admin/agent-session-transfers/sessions/plan | Plan Agent Session Transfer


# **export_agent_profile_transfer_api_v1_admin_agent_session_transfers_profiles_namespace_agent_key_export_get**
> ProfileBundleOutput export_agent_profile_transfer_api_v1_admin_agent_session_transfers_profiles_namespace_agent_key_export_get(namespace, agent_key, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Export Agent Profile Transfer

### Example


```python
import amesh_client
from amesh_client.models.profile_bundle_output import ProfileBundleOutput
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
    api_instance = amesh_client.AgentSessionTransfersApi(api_client)
    namespace = 'namespace_example' # str |
    agent_key = 'agent_key_example' # str |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Export Agent Profile Transfer
        api_response = api_instance.export_agent_profile_transfer_api_v1_admin_agent_session_transfers_profiles_namespace_agent_key_export_get(namespace, agent_key, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of AgentSessionTransfersApi->export_agent_profile_transfer_api_v1_admin_agent_session_transfers_profiles_namespace_agent_key_export_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AgentSessionTransfersApi->export_agent_profile_transfer_api_v1_admin_agent_session_transfers_profiles_namespace_agent_key_export_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **namespace** | **str**|  |
 **agent_key** | **str**|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

**ProfileBundleOutput**

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

# **export_agent_profile_transfer_api_v1_admin_agent_session_transfers_profiles_namespace_agent_key_export_post**
> ProfileBundleOutput export_agent_profile_transfer_api_v1_admin_agent_session_transfers_profiles_namespace_agent_key_export_post(namespace, agent_key, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Export Agent Profile Transfer

### Example


```python
import amesh_client
from amesh_client.models.profile_bundle_output import ProfileBundleOutput
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
    api_instance = amesh_client.AgentSessionTransfersApi(api_client)
    namespace = 'namespace_example' # str |
    agent_key = 'agent_key_example' # str |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Export Agent Profile Transfer
        api_response = api_instance.export_agent_profile_transfer_api_v1_admin_agent_session_transfers_profiles_namespace_agent_key_export_post(namespace, agent_key, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of AgentSessionTransfersApi->export_agent_profile_transfer_api_v1_admin_agent_session_transfers_profiles_namespace_agent_key_export_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AgentSessionTransfersApi->export_agent_profile_transfer_api_v1_admin_agent_session_transfers_profiles_namespace_agent_key_export_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **namespace** | **str**|  |
 **agent_key** | **str**|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

**ProfileBundleOutput**

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

# **export_agent_session_transfer_api_v1_admin_agent_session_transfers_sessions_session_id_export_post**
> SessionTransferBundleOutput export_agent_session_transfer_api_v1_admin_agent_session_transfers_sessions_session_id_export_post(session_id, agent_session_transfer_session_export_request, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Export Agent Session Transfer

### Example


```python
import amesh_client
from amesh_client.models.agent_session_transfer_session_export_request import AgentSessionTransferSessionExportRequest
from amesh_client.models.session_transfer_bundle_output import SessionTransferBundleOutput
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
    api_instance = amesh_client.AgentSessionTransfersApi(api_client)
    session_id = UUID('38400000-8cf0-11bd-b23e-10b96e4ef00d') # UUID |
    agent_session_transfer_session_export_request = amesh_client.AgentSessionTransferSessionExportRequest() # AgentSessionTransferSessionExportRequest |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Export Agent Session Transfer
        api_response = api_instance.export_agent_session_transfer_api_v1_admin_agent_session_transfers_sessions_session_id_export_post(session_id, agent_session_transfer_session_export_request, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of AgentSessionTransfersApi->export_agent_session_transfer_api_v1_admin_agent_session_transfers_sessions_session_id_export_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AgentSessionTransfersApi->export_agent_session_transfer_api_v1_admin_agent_session_transfers_sessions_session_id_export_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **session_id** | **UUID**|  |
 **agent_session_transfer_session_export_request** | **AgentSessionTransferSessionExportRequest**|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

**SessionTransferBundleOutput**

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

# **import_agent_profile_transfer_api_v1_admin_agent_session_transfers_profiles_import_post**
> ProfileImportResult import_agent_profile_transfer_api_v1_admin_agent_session_transfers_profiles_import_post(agent_session_transfer_profile_import_request, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Import Agent Profile Transfer

### Example


```python
import amesh_client
from amesh_client.models.agent_session_transfer_profile_import_request import AgentSessionTransferProfileImportRequest
from amesh_client.models.profile_import_result import ProfileImportResult
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
    api_instance = amesh_client.AgentSessionTransfersApi(api_client)
    agent_session_transfer_profile_import_request = amesh_client.AgentSessionTransferProfileImportRequest() # AgentSessionTransferProfileImportRequest |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Import Agent Profile Transfer
        api_response = api_instance.import_agent_profile_transfer_api_v1_admin_agent_session_transfers_profiles_import_post(agent_session_transfer_profile_import_request, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of AgentSessionTransfersApi->import_agent_profile_transfer_api_v1_admin_agent_session_transfers_profiles_import_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AgentSessionTransfersApi->import_agent_profile_transfer_api_v1_admin_agent_session_transfers_profiles_import_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **agent_session_transfer_profile_import_request** | **AgentSessionTransferProfileImportRequest**|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

**ProfileImportResult**

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

# **import_agent_session_transfer_api_v1_admin_agent_session_transfers_sessions_import_post**
> SessionTransferImportResult import_agent_session_transfer_api_v1_admin_agent_session_transfers_sessions_import_post(agent_session_transfer_session_import_request, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Import Agent Session Transfer

### Example


```python
import amesh_client
from amesh_client.models.agent_session_transfer_session_import_request import AgentSessionTransferSessionImportRequest
from amesh_client.models.session_transfer_import_result import SessionTransferImportResult
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
    api_instance = amesh_client.AgentSessionTransfersApi(api_client)
    agent_session_transfer_session_import_request = amesh_client.AgentSessionTransferSessionImportRequest() # AgentSessionTransferSessionImportRequest |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Import Agent Session Transfer
        api_response = api_instance.import_agent_session_transfer_api_v1_admin_agent_session_transfers_sessions_import_post(agent_session_transfer_session_import_request, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of AgentSessionTransfersApi->import_agent_session_transfer_api_v1_admin_agent_session_transfers_sessions_import_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AgentSessionTransfersApi->import_agent_session_transfer_api_v1_admin_agent_session_transfers_sessions_import_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **agent_session_transfer_session_import_request** | **AgentSessionTransferSessionImportRequest**|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

**SessionTransferImportResult**

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

# **plan_agent_profile_transfer_api_v1_admin_agent_session_transfers_profiles_plan_post**
> ProfileCompatibilityReport plan_agent_profile_transfer_api_v1_admin_agent_session_transfers_profiles_plan_post(agent_session_transfer_profile_plan_request, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Plan Agent Profile Transfer

### Example


```python
import amesh_client
from amesh_client.models.agent_session_transfer_profile_plan_request import AgentSessionTransferProfilePlanRequest
from amesh_client.models.profile_compatibility_report import ProfileCompatibilityReport
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
    api_instance = amesh_client.AgentSessionTransfersApi(api_client)
    agent_session_transfer_profile_plan_request = amesh_client.AgentSessionTransferProfilePlanRequest() # AgentSessionTransferProfilePlanRequest |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Plan Agent Profile Transfer
        api_response = api_instance.plan_agent_profile_transfer_api_v1_admin_agent_session_transfers_profiles_plan_post(agent_session_transfer_profile_plan_request, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of AgentSessionTransfersApi->plan_agent_profile_transfer_api_v1_admin_agent_session_transfers_profiles_plan_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AgentSessionTransfersApi->plan_agent_profile_transfer_api_v1_admin_agent_session_transfers_profiles_plan_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **agent_session_transfer_profile_plan_request** | **AgentSessionTransferProfilePlanRequest**|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

**ProfileCompatibilityReport**

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

# **plan_agent_session_transfer_api_v1_admin_agent_session_transfers_sessions_plan_post**
> SessionTransferCompatibilityReport plan_agent_session_transfer_api_v1_admin_agent_session_transfers_sessions_plan_post(agent_session_transfer_session_plan_request, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Plan Agent Session Transfer

### Example


```python
import amesh_client
from amesh_client.models.agent_session_transfer_session_plan_request import AgentSessionTransferSessionPlanRequest
from amesh_client.models.session_transfer_compatibility_report import SessionTransferCompatibilityReport
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
    api_instance = amesh_client.AgentSessionTransfersApi(api_client)
    agent_session_transfer_session_plan_request = amesh_client.AgentSessionTransferSessionPlanRequest() # AgentSessionTransferSessionPlanRequest |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Plan Agent Session Transfer
        api_response = api_instance.plan_agent_session_transfer_api_v1_admin_agent_session_transfers_sessions_plan_post(agent_session_transfer_session_plan_request, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of AgentSessionTransfersApi->plan_agent_session_transfer_api_v1_admin_agent_session_transfers_sessions_plan_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AgentSessionTransfersApi->plan_agent_session_transfer_api_v1_admin_agent_session_transfers_sessions_plan_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **agent_session_transfer_session_plan_request** | **AgentSessionTransferSessionPlanRequest**|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

**SessionTransferCompatibilityReport**

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
