# amesh_client.LifecycleApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_lifecycle_legal_hold_api_v1_lifecycle_legal_holds_post**](LifecycleApi.md#create_lifecycle_legal_hold_api_v1_lifecycle_legal_holds_post) | **POST** /api/v1/lifecycle/legal-holds | Create Lifecycle Legal Hold
[**create_lifecycle_policy_api_v1_lifecycle_policies_post**](LifecycleApi.md#create_lifecycle_policy_api_v1_lifecycle_policies_post) | **POST** /api/v1/lifecycle/policies | Create Lifecycle Policy
[**execute_lifecycle_job_api_v1_lifecycle_jobs_job_id_execute_post**](LifecycleApi.md#execute_lifecycle_job_api_v1_lifecycle_jobs_job_id_execute_post) | **POST** /api/v1/lifecycle/jobs/{job_id}/execute | Execute Lifecycle Job
[**get_lifecycle_job_api_v1_lifecycle_jobs_job_id_get**](LifecycleApi.md#get_lifecycle_job_api_v1_lifecycle_jobs_job_id_get) | **GET** /api/v1/lifecycle/jobs/{job_id} | Get Lifecycle Job
[**list_lifecycle_jobs_api_v1_lifecycle_jobs_get**](LifecycleApi.md#list_lifecycle_jobs_api_v1_lifecycle_jobs_get) | **GET** /api/v1/lifecycle/jobs | List Lifecycle Jobs
[**list_lifecycle_legal_holds_api_v1_lifecycle_legal_holds_get**](LifecycleApi.md#list_lifecycle_legal_holds_api_v1_lifecycle_legal_holds_get) | **GET** /api/v1/lifecycle/legal-holds | List Lifecycle Legal Holds
[**list_lifecycle_policies_api_v1_lifecycle_policies_get**](LifecycleApi.md#list_lifecycle_policies_api_v1_lifecycle_policies_get) | **GET** /api/v1/lifecycle/policies | List Lifecycle Policies
[**preview_lifecycle_purge_api_v1_lifecycle_previews_post**](LifecycleApi.md#preview_lifecycle_purge_api_v1_lifecycle_previews_post) | **POST** /api/v1/lifecycle/previews | Preview Lifecycle Purge
[**release_lifecycle_legal_hold_api_v1_lifecycle_legal_holds_hold_id_release_post**](LifecycleApi.md#release_lifecycle_legal_hold_api_v1_lifecycle_legal_holds_hold_id_release_post) | **POST** /api/v1/lifecycle/legal-holds/{hold_id}/release | Release Lifecycle Legal Hold
[**resume_lifecycle_job_api_v1_lifecycle_jobs_job_id_resume_post**](LifecycleApi.md#resume_lifecycle_job_api_v1_lifecycle_jobs_job_id_resume_post) | **POST** /api/v1/lifecycle/jobs/{job_id}/resume | Resume Lifecycle Job
[**update_lifecycle_policy_api_v1_lifecycle_policies_policy_id_put**](LifecycleApi.md#update_lifecycle_policy_api_v1_lifecycle_policies_policy_id_put) | **PUT** /api/v1/lifecycle/policies/{policy_id} | Update Lifecycle Policy


# **create_lifecycle_legal_hold_api_v1_lifecycle_legal_holds_post**
> LifecycleLegalHold create_lifecycle_legal_hold_api_v1_lifecycle_legal_holds_post(lifecycle_legal_hold_draft, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Create Lifecycle Legal Hold

### Example


```python
import amesh_client
from amesh_client.models.lifecycle_legal_hold import LifecycleLegalHold
from amesh_client.models.lifecycle_legal_hold_draft import LifecycleLegalHoldDraft
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
    api_instance = amesh_client.LifecycleApi(api_client)
    lifecycle_legal_hold_draft = amesh_client.LifecycleLegalHoldDraft() # LifecycleLegalHoldDraft |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Create Lifecycle Legal Hold
        api_response = api_instance.create_lifecycle_legal_hold_api_v1_lifecycle_legal_holds_post(lifecycle_legal_hold_draft, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of LifecycleApi->create_lifecycle_legal_hold_api_v1_lifecycle_legal_holds_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling LifecycleApi->create_lifecycle_legal_hold_api_v1_lifecycle_legal_holds_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **lifecycle_legal_hold_draft** | **LifecycleLegalHoldDraft**|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

**LifecycleLegalHold**

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

# **create_lifecycle_policy_api_v1_lifecycle_policies_post**
> LifecyclePolicy create_lifecycle_policy_api_v1_lifecycle_policies_post(lifecycle_policy_draft, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Create Lifecycle Policy

### Example


```python
import amesh_client
from amesh_client.models.lifecycle_policy import LifecyclePolicy
from amesh_client.models.lifecycle_policy_draft import LifecyclePolicyDraft
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
    api_instance = amesh_client.LifecycleApi(api_client)
    lifecycle_policy_draft = amesh_client.LifecyclePolicyDraft() # LifecyclePolicyDraft |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Create Lifecycle Policy
        api_response = api_instance.create_lifecycle_policy_api_v1_lifecycle_policies_post(lifecycle_policy_draft, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of LifecycleApi->create_lifecycle_policy_api_v1_lifecycle_policies_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling LifecycleApi->create_lifecycle_policy_api_v1_lifecycle_policies_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **lifecycle_policy_draft** | **LifecyclePolicyDraft**|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

**LifecyclePolicy**

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

# **execute_lifecycle_job_api_v1_lifecycle_jobs_job_id_execute_post**
> LifecycleJob execute_lifecycle_job_api_v1_lifecycle_jobs_job_id_execute_post(job_id, lifecycle_execute_request, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Execute Lifecycle Job

### Example


```python
import amesh_client
from amesh_client.models.lifecycle_execute_request import LifecycleExecuteRequest
from amesh_client.models.lifecycle_job import LifecycleJob
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
    api_instance = amesh_client.LifecycleApi(api_client)
    job_id = UUID('38400000-8cf0-11bd-b23e-10b96e4ef00d') # UUID |
    lifecycle_execute_request = amesh_client.LifecycleExecuteRequest() # LifecycleExecuteRequest |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Execute Lifecycle Job
        api_response = api_instance.execute_lifecycle_job_api_v1_lifecycle_jobs_job_id_execute_post(job_id, lifecycle_execute_request, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of LifecycleApi->execute_lifecycle_job_api_v1_lifecycle_jobs_job_id_execute_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling LifecycleApi->execute_lifecycle_job_api_v1_lifecycle_jobs_job_id_execute_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **job_id** | **UUID**|  |
 **lifecycle_execute_request** | **LifecycleExecuteRequest**|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

**LifecycleJob**

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

# **get_lifecycle_job_api_v1_lifecycle_jobs_job_id_get**
> LifecycleJob get_lifecycle_job_api_v1_lifecycle_jobs_job_id_get(job_id, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Get Lifecycle Job

### Example


```python
import amesh_client
from amesh_client.models.lifecycle_job import LifecycleJob
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
    api_instance = amesh_client.LifecycleApi(api_client)
    job_id = UUID('38400000-8cf0-11bd-b23e-10b96e4ef00d') # UUID |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Get Lifecycle Job
        api_response = api_instance.get_lifecycle_job_api_v1_lifecycle_jobs_job_id_get(job_id, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of LifecycleApi->get_lifecycle_job_api_v1_lifecycle_jobs_job_id_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling LifecycleApi->get_lifecycle_job_api_v1_lifecycle_jobs_job_id_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **job_id** | **UUID**|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

**LifecycleJob**

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

# **list_lifecycle_jobs_api_v1_lifecycle_jobs_get**
> List[LifecycleJob] list_lifecycle_jobs_api_v1_lifecycle_jobs_get(limit=limit, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

List Lifecycle Jobs

### Example


```python
import amesh_client
from amesh_client.models.lifecycle_job import LifecycleJob
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
    api_instance = amesh_client.LifecycleApi(api_client)
    limit = 50 # int |  (optional) (default to 50)
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # List Lifecycle Jobs
        api_response = api_instance.list_lifecycle_jobs_api_v1_lifecycle_jobs_get(limit=limit, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of LifecycleApi->list_lifecycle_jobs_api_v1_lifecycle_jobs_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling LifecycleApi->list_lifecycle_jobs_api_v1_lifecycle_jobs_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **limit** | **int**|  | [optional] [default to 50]
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

[**List[LifecycleJob]**](LifecycleJob.md)

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

# **list_lifecycle_legal_holds_api_v1_lifecycle_legal_holds_get**
> List[LifecycleLegalHold] list_lifecycle_legal_holds_api_v1_lifecycle_legal_holds_get(authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

List Lifecycle Legal Holds

### Example


```python
import amesh_client
from amesh_client.models.lifecycle_legal_hold import LifecycleLegalHold
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
    api_instance = amesh_client.LifecycleApi(api_client)
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # List Lifecycle Legal Holds
        api_response = api_instance.list_lifecycle_legal_holds_api_v1_lifecycle_legal_holds_get(authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of LifecycleApi->list_lifecycle_legal_holds_api_v1_lifecycle_legal_holds_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling LifecycleApi->list_lifecycle_legal_holds_api_v1_lifecycle_legal_holds_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

[**List[LifecycleLegalHold]**](LifecycleLegalHold.md)

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

# **list_lifecycle_policies_api_v1_lifecycle_policies_get**
> List[LifecyclePolicy] list_lifecycle_policies_api_v1_lifecycle_policies_get(authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

List Lifecycle Policies

### Example


```python
import amesh_client
from amesh_client.models.lifecycle_policy import LifecyclePolicy
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
    api_instance = amesh_client.LifecycleApi(api_client)
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # List Lifecycle Policies
        api_response = api_instance.list_lifecycle_policies_api_v1_lifecycle_policies_get(authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of LifecycleApi->list_lifecycle_policies_api_v1_lifecycle_policies_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling LifecycleApi->list_lifecycle_policies_api_v1_lifecycle_policies_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

[**List[LifecyclePolicy]**](LifecyclePolicy.md)

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

# **preview_lifecycle_purge_api_v1_lifecycle_previews_post**
> LifecycleJob preview_lifecycle_purge_api_v1_lifecycle_previews_post(lifecycle_preview_request, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Preview Lifecycle Purge

### Example


```python
import amesh_client
from amesh_client.models.lifecycle_job import LifecycleJob
from amesh_client.models.lifecycle_preview_request import LifecyclePreviewRequest
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
    api_instance = amesh_client.LifecycleApi(api_client)
    lifecycle_preview_request = amesh_client.LifecyclePreviewRequest() # LifecyclePreviewRequest |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Preview Lifecycle Purge
        api_response = api_instance.preview_lifecycle_purge_api_v1_lifecycle_previews_post(lifecycle_preview_request, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of LifecycleApi->preview_lifecycle_purge_api_v1_lifecycle_previews_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling LifecycleApi->preview_lifecycle_purge_api_v1_lifecycle_previews_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **lifecycle_preview_request** | **LifecyclePreviewRequest**|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

**LifecycleJob**

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

# **release_lifecycle_legal_hold_api_v1_lifecycle_legal_holds_hold_id_release_post**
> LifecycleLegalHold release_lifecycle_legal_hold_api_v1_lifecycle_legal_holds_hold_id_release_post(hold_id, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Release Lifecycle Legal Hold

### Example


```python
import amesh_client
from amesh_client.models.lifecycle_legal_hold import LifecycleLegalHold
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
    api_instance = amesh_client.LifecycleApi(api_client)
    hold_id = UUID('38400000-8cf0-11bd-b23e-10b96e4ef00d') # UUID |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Release Lifecycle Legal Hold
        api_response = api_instance.release_lifecycle_legal_hold_api_v1_lifecycle_legal_holds_hold_id_release_post(hold_id, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of LifecycleApi->release_lifecycle_legal_hold_api_v1_lifecycle_legal_holds_hold_id_release_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling LifecycleApi->release_lifecycle_legal_hold_api_v1_lifecycle_legal_holds_hold_id_release_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **hold_id** | **UUID**|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

**LifecycleLegalHold**

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

# **resume_lifecycle_job_api_v1_lifecycle_jobs_job_id_resume_post**
> LifecycleJob resume_lifecycle_job_api_v1_lifecycle_jobs_job_id_resume_post(job_id, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Resume Lifecycle Job

### Example


```python
import amesh_client
from amesh_client.models.lifecycle_job import LifecycleJob
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
    api_instance = amesh_client.LifecycleApi(api_client)
    job_id = UUID('38400000-8cf0-11bd-b23e-10b96e4ef00d') # UUID |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Resume Lifecycle Job
        api_response = api_instance.resume_lifecycle_job_api_v1_lifecycle_jobs_job_id_resume_post(job_id, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of LifecycleApi->resume_lifecycle_job_api_v1_lifecycle_jobs_job_id_resume_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling LifecycleApi->resume_lifecycle_job_api_v1_lifecycle_jobs_job_id_resume_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **job_id** | **UUID**|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

**LifecycleJob**

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

# **update_lifecycle_policy_api_v1_lifecycle_policies_policy_id_put**
> LifecyclePolicy update_lifecycle_policy_api_v1_lifecycle_policies_policy_id_put(policy_id, lifecycle_policy_draft, expected_version=expected_version, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Update Lifecycle Policy

### Example


```python
import amesh_client
from amesh_client.models.lifecycle_policy import LifecyclePolicy
from amesh_client.models.lifecycle_policy_draft import LifecyclePolicyDraft
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
    api_instance = amesh_client.LifecycleApi(api_client)
    policy_id = UUID('38400000-8cf0-11bd-b23e-10b96e4ef00d') # UUID |
    lifecycle_policy_draft = amesh_client.LifecyclePolicyDraft() # LifecyclePolicyDraft |
    expected_version = 56 # int |  (optional)
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Update Lifecycle Policy
        api_response = api_instance.update_lifecycle_policy_api_v1_lifecycle_policies_policy_id_put(policy_id, lifecycle_policy_draft, expected_version=expected_version, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of LifecycleApi->update_lifecycle_policy_api_v1_lifecycle_policies_policy_id_put:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling LifecycleApi->update_lifecycle_policy_api_v1_lifecycle_policies_policy_id_put: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **policy_id** | **UUID**|  |
 **lifecycle_policy_draft** | **LifecyclePolicyDraft**|  |
 **expected_version** | **int**|  | [optional]
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

**LifecyclePolicy**

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
