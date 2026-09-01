# amesh_client.AgentSessionAdministrationApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**bulk_control_agent_sessions_api_v1_admin_agent_sessions_actions_post**](AgentSessionAdministrationApi.md#bulk_control_agent_sessions_api_v1_admin_agent_sessions_actions_post) | **POST** /api/v1/admin/agent-sessions/actions | Bulk Control Agent Sessions
[**get_agent_session_instance_aggregate_api_v1_admin_agent_sessions_aggregate_get**](AgentSessionAdministrationApi.md#get_agent_session_instance_aggregate_api_v1_admin_agent_sessions_aggregate_get) | **GET** /api/v1/admin/agent-sessions/aggregate | Get Agent Session Instance Aggregate
[**get_agent_session_policy_revision_api_v1_admin_agent_session_policies_policy_id_get**](AgentSessionAdministrationApi.md#get_agent_session_policy_revision_api_v1_admin_agent_session_policies_policy_id_get) | **GET** /api/v1/admin/agent-session-policies/{policy_id} | Get Agent Session Policy Revision
[**get_effective_agent_session_policies_api_v1_admin_agent_session_policies_effective_get**](AgentSessionAdministrationApi.md#get_effective_agent_session_policies_api_v1_admin_agent_session_policies_effective_get) | **GET** /api/v1/admin/agent-session-policies/effective | Get Effective Agent Session Policies
[**list_agent_session_fleet_api_v1_admin_agent_sessions_get**](AgentSessionAdministrationApi.md#list_agent_session_fleet_api_v1_admin_agent_sessions_get) | **GET** /api/v1/admin/agent-sessions | List Agent Session Fleet
[**list_agent_session_policies_api_v1_admin_agent_session_policies_get**](AgentSessionAdministrationApi.md#list_agent_session_policies_api_v1_admin_agent_session_policies_get) | **GET** /api/v1/admin/agent-session-policies | List Agent Session Policies
[**put_agent_session_policy_api_v1_admin_agent_session_policies_put**](AgentSessionAdministrationApi.md#put_agent_session_policy_api_v1_admin_agent_session_policies_put) | **PUT** /api/v1/admin/agent-session-policies | Put Agent Session Policy


# **bulk_control_agent_sessions_api_v1_admin_agent_sessions_actions_post**
> AgentSessionBulkActionResponse bulk_control_agent_sessions_api_v1_admin_agent_sessions_actions_post(agent_session_bulk_action_request, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Bulk Control Agent Sessions

Apply bounded, independently fenced lifecycle controls to agent sessions.

### Example


```python
import amesh_client
from amesh_client.models.agent_session_bulk_action_request import AgentSessionBulkActionRequest
from amesh_client.models.agent_session_bulk_action_response import AgentSessionBulkActionResponse
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
    api_instance = amesh_client.AgentSessionAdministrationApi(api_client)
    agent_session_bulk_action_request = amesh_client.AgentSessionBulkActionRequest() # AgentSessionBulkActionRequest |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Bulk Control Agent Sessions
        api_response = api_instance.bulk_control_agent_sessions_api_v1_admin_agent_sessions_actions_post(agent_session_bulk_action_request, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of AgentSessionAdministrationApi->bulk_control_agent_sessions_api_v1_admin_agent_sessions_actions_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AgentSessionAdministrationApi->bulk_control_agent_sessions_api_v1_admin_agent_sessions_actions_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **agent_session_bulk_action_request** | **AgentSessionBulkActionRequest**|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

**AgentSessionBulkActionResponse**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**207** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_agent_session_instance_aggregate_api_v1_admin_agent_sessions_aggregate_get**
> AgentSessionInstanceAggregate get_agent_session_instance_aggregate_api_v1_admin_agent_sessions_aggregate_get(authorization=authorization, x_amesh_csrf=x_amesh_csrf)

Get Agent Session Instance Aggregate

Return instance-wide metadata-only totals without exposing tenant session rows.

### Example


```python
import amesh_client
from amesh_client.models.agent_session_instance_aggregate import AgentSessionInstanceAggregate
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
    api_instance = amesh_client.AgentSessionAdministrationApi(api_client)
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)

    try:
        # Get Agent Session Instance Aggregate
        api_response = api_instance.get_agent_session_instance_aggregate_api_v1_admin_agent_sessions_aggregate_get(authorization=authorization, x_amesh_csrf=x_amesh_csrf)
        print("The response of AgentSessionAdministrationApi->get_agent_session_instance_aggregate_api_v1_admin_agent_sessions_aggregate_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AgentSessionAdministrationApi->get_agent_session_instance_aggregate_api_v1_admin_agent_sessions_aggregate_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]

### Return type

**AgentSessionInstanceAggregate**

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

# **get_agent_session_policy_revision_api_v1_admin_agent_session_policies_policy_id_get**
> AgentSessionPolicyRevision get_agent_session_policy_revision_api_v1_admin_agent_session_policies_policy_id_get(policy_id, revision=revision, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Get Agent Session Policy Revision

### Example


```python
import amesh_client
from amesh_client.models.agent_session_policy_revision import AgentSessionPolicyRevision
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
    api_instance = amesh_client.AgentSessionAdministrationApi(api_client)
    policy_id = UUID('38400000-8cf0-11bd-b23e-10b96e4ef00d') # UUID |
    revision = 56 # int |  (optional)
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Get Agent Session Policy Revision
        api_response = api_instance.get_agent_session_policy_revision_api_v1_admin_agent_session_policies_policy_id_get(policy_id, revision=revision, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of AgentSessionAdministrationApi->get_agent_session_policy_revision_api_v1_admin_agent_session_policies_policy_id_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AgentSessionAdministrationApi->get_agent_session_policy_revision_api_v1_admin_agent_session_policies_policy_id_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **policy_id** | **UUID**|  |
 **revision** | **int**|  | [optional]
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

**AgentSessionPolicyRevision**

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

# **get_effective_agent_session_policies_api_v1_admin_agent_session_policies_effective_get**
> List[AgentSessionPolicyRevision] get_effective_agent_session_policies_api_v1_admin_agent_session_policies_effective_get(namespace, application_id=application_id, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Get Effective Agent Session Policies

### Example


```python
import amesh_client
from amesh_client.models.agent_session_policy_revision import AgentSessionPolicyRevision
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
    api_instance = amesh_client.AgentSessionAdministrationApi(api_client)
    namespace = 'namespace_example' # str |
    application_id = 'application_id_example' # str |  (optional)
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Get Effective Agent Session Policies
        api_response = api_instance.get_effective_agent_session_policies_api_v1_admin_agent_session_policies_effective_get(namespace, application_id=application_id, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of AgentSessionAdministrationApi->get_effective_agent_session_policies_api_v1_admin_agent_session_policies_effective_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AgentSessionAdministrationApi->get_effective_agent_session_policies_api_v1_admin_agent_session_policies_effective_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **namespace** | **str**|  |
 **application_id** | **str**|  | [optional]
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

[**List[AgentSessionPolicyRevision]**](AgentSessionPolicyRevision.md)

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

# **list_agent_session_fleet_api_v1_admin_agent_sessions_get**
> AgentSessionFleetPage list_agent_session_fleet_api_v1_admin_agent_sessions_get(limit=limit, cursor=cursor, state=state, namespace=namespace, agent_ref=agent_ref, owner_id=owner_id, harness=harness, created_from=created_from, created_to=created_to, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

List Agent Session Fleet

Return a bounded, tenant-isolated administrative session fleet projection.

### Example


```python
import amesh_client
from amesh_client.models.agent_session_fleet_page import AgentSessionFleetPage
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
    api_instance = amesh_client.AgentSessionAdministrationApi(api_client)
    limit = 100 # int |  (optional) (default to 100)
    cursor = 'cursor_example' # str |  (optional)
    state = 'state_example' # str |  (optional)
    namespace = 'namespace_example' # str |  (optional)
    agent_ref = 'agent_ref_example' # str |  (optional)
    owner_id = 'owner_id_example' # str |  (optional)
    harness = 'harness_example' # str |  (optional)
    created_from = '2013-10-20T19:20:30+01:00' # datetime |  (optional)
    created_to = '2013-10-20T19:20:30+01:00' # datetime |  (optional)
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # List Agent Session Fleet
        api_response = api_instance.list_agent_session_fleet_api_v1_admin_agent_sessions_get(limit=limit, cursor=cursor, state=state, namespace=namespace, agent_ref=agent_ref, owner_id=owner_id, harness=harness, created_from=created_from, created_to=created_to, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of AgentSessionAdministrationApi->list_agent_session_fleet_api_v1_admin_agent_sessions_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AgentSessionAdministrationApi->list_agent_session_fleet_api_v1_admin_agent_sessions_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **limit** | **int**|  | [optional] [default to 100]
 **cursor** | **str**|  | [optional]
 **state** | **str**|  | [optional]
 **namespace** | **str**|  | [optional]
 **agent_ref** | **str**|  | [optional]
 **owner_id** | **str**|  | [optional]
 **harness** | **str**|  | [optional]
 **created_from** | **datetime**|  | [optional]
 **created_to** | **datetime**|  | [optional]
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

**AgentSessionFleetPage**

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

# **list_agent_session_policies_api_v1_admin_agent_session_policies_get**
> List[AgentSessionPolicyRevision] list_agent_session_policies_api_v1_admin_agent_session_policies_get(namespace=namespace, application_id=application_id, limit=limit, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

List Agent Session Policies

### Example


```python
import amesh_client
from amesh_client.models.agent_session_policy_revision import AgentSessionPolicyRevision
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
    api_instance = amesh_client.AgentSessionAdministrationApi(api_client)
    namespace = 'namespace_example' # str |  (optional)
    application_id = 'application_id_example' # str |  (optional)
    limit = 100 # int |  (optional) (default to 100)
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # List Agent Session Policies
        api_response = api_instance.list_agent_session_policies_api_v1_admin_agent_session_policies_get(namespace=namespace, application_id=application_id, limit=limit, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of AgentSessionAdministrationApi->list_agent_session_policies_api_v1_admin_agent_session_policies_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AgentSessionAdministrationApi->list_agent_session_policies_api_v1_admin_agent_session_policies_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **namespace** | **str**|  | [optional]
 **application_id** | **str**|  | [optional]
 **limit** | **int**|  | [optional] [default to 100]
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

[**List[AgentSessionPolicyRevision]**](AgentSessionPolicyRevision.md)

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

# **put_agent_session_policy_api_v1_admin_agent_session_policies_put**
> AgentSessionPolicyRevision put_agent_session_policy_api_v1_admin_agent_session_policies_put(agent_session_policy_upsert_request, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Put Agent Session Policy

### Example


```python
import amesh_client
from amesh_client.models.agent_session_policy_revision import AgentSessionPolicyRevision
from amesh_client.models.agent_session_policy_upsert_request import AgentSessionPolicyUpsertRequest
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
    api_instance = amesh_client.AgentSessionAdministrationApi(api_client)
    agent_session_policy_upsert_request = amesh_client.AgentSessionPolicyUpsertRequest() # AgentSessionPolicyUpsertRequest |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Put Agent Session Policy
        api_response = api_instance.put_agent_session_policy_api_v1_admin_agent_session_policies_put(agent_session_policy_upsert_request, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of AgentSessionAdministrationApi->put_agent_session_policy_api_v1_admin_agent_session_policies_put:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AgentSessionAdministrationApi->put_agent_session_policy_api_v1_admin_agent_session_policies_put: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **agent_session_policy_upsert_request** | **AgentSessionPolicyUpsertRequest**|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

**AgentSessionPolicyRevision**

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
