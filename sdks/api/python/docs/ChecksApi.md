# amesh_client.ChecksApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_check_compliance_api_v1_check_compliance_get**](ChecksApi.md#get_check_compliance_api_v1_check_compliance_get) | **GET** /api/v1/check-compliance | Get Check Compliance
[**list_check_evaluations_api_v1_check_evaluations_get**](ChecksApi.md#list_check_evaluations_api_v1_check_evaluations_get) | **GET** /api/v1/check-evaluations | List Check Evaluations
[**list_check_policies_api_v1_check_policies_get**](ChecksApi.md#list_check_policies_api_v1_check_policies_get) | **GET** /api/v1/check-policies | List Check Policies
[**upsert_check_policy_api_v1_check_policies_namespace_policy_key_put**](ChecksApi.md#upsert_check_policy_api_v1_check_policies_namespace_policy_key_put) | **PUT** /api/v1/check-policies/{namespace}/{policy_key} | Upsert Check Policy


# **get_check_compliance_api_v1_check_compliance_get**
> List[CheckComplianceSummary] get_check_compliance_api_v1_check_compliance_get(group_by=group_by, from_time=from_time, to_time=to_time, namespace=namespace, flow_id=flow_id, limit=limit, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Get Check Compliance

### Example


```python
import amesh_client
from amesh_client.models.check_compliance_summary import CheckComplianceSummary
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
    api_instance = amesh_client.ChecksApi(api_client)
    group_by = 'flow' # str |  (optional) (default to 'flow')
    from_time = '2013-10-20T19:20:30+01:00' # datetime |  (optional)
    to_time = '2013-10-20T19:20:30+01:00' # datetime |  (optional)
    namespace = 'namespace_example' # str |  (optional)
    flow_id = 'flow_id_example' # str |  (optional)
    limit = 100 # int |  (optional) (default to 100)
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Get Check Compliance
        api_response = api_instance.get_check_compliance_api_v1_check_compliance_get(group_by=group_by, from_time=from_time, to_time=to_time, namespace=namespace, flow_id=flow_id, limit=limit, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of ChecksApi->get_check_compliance_api_v1_check_compliance_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ChecksApi->get_check_compliance_api_v1_check_compliance_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **group_by** | **str**|  | [optional] [default to &#39;flow&#39;]
 **from_time** | **datetime**|  | [optional]
 **to_time** | **datetime**|  | [optional]
 **namespace** | **str**|  | [optional]
 **flow_id** | **str**|  | [optional]
 **limit** | **int**|  | [optional] [default to 100]
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

[**List[CheckComplianceSummary]**](CheckComplianceSummary.md)

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

# **list_check_evaluations_api_v1_check_evaluations_get**
> List[CheckEvaluation] list_check_evaluations_api_v1_check_evaluations_get(namespace=namespace, flow_id=flow_id, execution_id=execution_id, outcome=outcome, limit=limit, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

List Check Evaluations

### Example


```python
import amesh_client
from amesh_client.models.check_evaluation import CheckEvaluation
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
    api_instance = amesh_client.ChecksApi(api_client)
    namespace = 'namespace_example' # str |  (optional)
    flow_id = 'flow_id_example' # str |  (optional)
    execution_id = UUID('38400000-8cf0-11bd-b23e-10b96e4ef00d') # UUID |  (optional)
    outcome = amesh_client.CheckOutcome() # CheckOutcome |  (optional)
    limit = 100 # int |  (optional) (default to 100)
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # List Check Evaluations
        api_response = api_instance.list_check_evaluations_api_v1_check_evaluations_get(namespace=namespace, flow_id=flow_id, execution_id=execution_id, outcome=outcome, limit=limit, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of ChecksApi->list_check_evaluations_api_v1_check_evaluations_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ChecksApi->list_check_evaluations_api_v1_check_evaluations_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **namespace** | **str**|  | [optional]
 **flow_id** | **str**|  | [optional]
 **execution_id** | **UUID**|  | [optional]
 **outcome** | **CheckOutcome**|  | [optional]
 **limit** | **int**|  | [optional] [default to 100]
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

[**List[CheckEvaluation]**](CheckEvaluation.md)

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

# **list_check_policies_api_v1_check_policies_get**
> List[NamespaceCheckPolicy] list_check_policies_api_v1_check_policies_get(namespace=namespace, limit=limit, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

List Check Policies

### Example


```python
import amesh_client
from amesh_client.models.namespace_check_policy import NamespaceCheckPolicy
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
    api_instance = amesh_client.ChecksApi(api_client)
    namespace = 'namespace_example' # str |  (optional)
    limit = 100 # int |  (optional) (default to 100)
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # List Check Policies
        api_response = api_instance.list_check_policies_api_v1_check_policies_get(namespace=namespace, limit=limit, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of ChecksApi->list_check_policies_api_v1_check_policies_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ChecksApi->list_check_policies_api_v1_check_policies_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **namespace** | **str**|  | [optional]
 **limit** | **int**|  | [optional] [default to 100]
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

[**List[NamespaceCheckPolicy]**](NamespaceCheckPolicy.md)

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

# **upsert_check_policy_api_v1_check_policies_namespace_policy_key_put**
> NamespaceCheckPolicy upsert_check_policy_api_v1_check_policies_namespace_policy_key_put(namespace, policy_key, check_policy_upsert_request, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Upsert Check Policy

### Example


```python
import amesh_client
from amesh_client.models.check_policy_upsert_request import CheckPolicyUpsertRequest
from amesh_client.models.namespace_check_policy import NamespaceCheckPolicy
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
    api_instance = amesh_client.ChecksApi(api_client)
    namespace = 'namespace_example' # str |
    policy_key = 'policy_key_example' # str |
    check_policy_upsert_request = amesh_client.CheckPolicyUpsertRequest() # CheckPolicyUpsertRequest |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Upsert Check Policy
        api_response = api_instance.upsert_check_policy_api_v1_check_policies_namespace_policy_key_put(namespace, policy_key, check_policy_upsert_request, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of ChecksApi->upsert_check_policy_api_v1_check_policies_namespace_policy_key_put:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ChecksApi->upsert_check_policy_api_v1_check_policies_namespace_policy_key_put: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **namespace** | **str**|  |
 **policy_key** | **str**|  |
 **check_policy_upsert_request** | **CheckPolicyUpsertRequest**|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

**NamespaceCheckPolicy**

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
