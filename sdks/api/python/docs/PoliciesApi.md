# amesh_client.PoliciesApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_admission_policy_api_v1_policies_post**](PoliciesApi.md#create_admission_policy_api_v1_policies_post) | **POST** /api/v1/policies | Create Admission Policy
[**evaluate_admission_policies_api_v1_policies_evaluate_post**](PoliciesApi.md#evaluate_admission_policies_api_v1_policies_evaluate_post) | **POST** /api/v1/policies/evaluate | Evaluate Admission Policies
[**get_admission_policy_api_v1_policies_policy_key_get**](PoliciesApi.md#get_admission_policy_api_v1_policies_policy_key_get) | **GET** /api/v1/policies/{policy_key} | Get Admission Policy
[**list_admission_policies_api_v1_policies_get**](PoliciesApi.md#list_admission_policies_api_v1_policies_get) | **GET** /api/v1/policies | List Admission Policies
[**list_admission_policy_decisions_api_v1_policies_decisions_get**](PoliciesApi.md#list_admission_policy_decisions_api_v1_policies_decisions_get) | **GET** /api/v1/policies/decisions | List Admission Policy Decisions
[**test_admission_policy_api_v1_policies_policy_key_test_post**](PoliciesApi.md#test_admission_policy_api_v1_policies_policy_key_test_post) | **POST** /api/v1/policies/{policy_key}/test | Test Admission Policy
[**update_admission_policy_api_v1_policies_policy_key_put**](PoliciesApi.md#update_admission_policy_api_v1_policies_policy_key_put) | **PUT** /api/v1/policies/{policy_key} | Update Admission Policy
[**validate_flow_admission_policy_api_v1_policies_flows_validate_post**](PoliciesApi.md#validate_flow_admission_policy_api_v1_policies_flows_validate_post) | **POST** /api/v1/policies/flows/validate | Validate Flow Admission Policy


# **create_admission_policy_api_v1_policies_post**
> PolicyRevision create_admission_policy_api_v1_policies_post(policy_document, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Create Admission Policy

### Example


```python
import amesh_client
from amesh_client.models.policy_document import PolicyDocument
from amesh_client.models.policy_revision import PolicyRevision
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
    api_instance = amesh_client.PoliciesApi(api_client)
    policy_document = amesh_client.PolicyDocument() # PolicyDocument |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Create Admission Policy
        api_response = api_instance.create_admission_policy_api_v1_policies_post(policy_document, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of PoliciesApi->create_admission_policy_api_v1_policies_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PoliciesApi->create_admission_policy_api_v1_policies_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **policy_document** | **PolicyDocument**|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

**PolicyRevision**

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

# **evaluate_admission_policies_api_v1_policies_evaluate_post**
> PolicyDecision evaluate_admission_policies_api_v1_policies_evaluate_post(policy_evaluation_request, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Evaluate Admission Policies

### Example


```python
import amesh_client
from amesh_client.models.policy_decision import PolicyDecision
from amesh_client.models.policy_evaluation_request import PolicyEvaluationRequest
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
    api_instance = amesh_client.PoliciesApi(api_client)
    policy_evaluation_request = amesh_client.PolicyEvaluationRequest() # PolicyEvaluationRequest |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Evaluate Admission Policies
        api_response = api_instance.evaluate_admission_policies_api_v1_policies_evaluate_post(policy_evaluation_request, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of PoliciesApi->evaluate_admission_policies_api_v1_policies_evaluate_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PoliciesApi->evaluate_admission_policies_api_v1_policies_evaluate_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **policy_evaluation_request** | **PolicyEvaluationRequest**|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

**PolicyDecision**

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

# **get_admission_policy_api_v1_policies_policy_key_get**
> PolicyRevision get_admission_policy_api_v1_policies_policy_key_get(policy_key, revision=revision, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Get Admission Policy

### Example


```python
import amesh_client
from amesh_client.models.policy_revision import PolicyRevision
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
    api_instance = amesh_client.PoliciesApi(api_client)
    policy_key = 'policy_key_example' # str |
    revision = 56 # int |  (optional)
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Get Admission Policy
        api_response = api_instance.get_admission_policy_api_v1_policies_policy_key_get(policy_key, revision=revision, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of PoliciesApi->get_admission_policy_api_v1_policies_policy_key_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PoliciesApi->get_admission_policy_api_v1_policies_policy_key_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **policy_key** | **str**|  |
 **revision** | **int**|  | [optional]
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

**PolicyRevision**

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

# **list_admission_policies_api_v1_policies_get**
> List[PolicyRevision] list_admission_policies_api_v1_policies_get(namespace=namespace, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

List Admission Policies

### Example


```python
import amesh_client
from amesh_client.models.policy_revision import PolicyRevision
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
    api_instance = amesh_client.PoliciesApi(api_client)
    namespace = 'default' # str |  (optional) (default to 'default')
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # List Admission Policies
        api_response = api_instance.list_admission_policies_api_v1_policies_get(namespace=namespace, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of PoliciesApi->list_admission_policies_api_v1_policies_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PoliciesApi->list_admission_policies_api_v1_policies_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **namespace** | **str**|  | [optional] [default to &#39;default&#39;]
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

[**List[PolicyRevision]**](PolicyRevision.md)

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

# **list_admission_policy_decisions_api_v1_policies_decisions_get**
> List[PolicyDecision] list_admission_policy_decisions_api_v1_policies_decisions_get(limit=limit, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

List Admission Policy Decisions

### Example


```python
import amesh_client
from amesh_client.models.policy_decision import PolicyDecision
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
    api_instance = amesh_client.PoliciesApi(api_client)
    limit = 100 # int |  (optional) (default to 100)
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # List Admission Policy Decisions
        api_response = api_instance.list_admission_policy_decisions_api_v1_policies_decisions_get(limit=limit, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of PoliciesApi->list_admission_policy_decisions_api_v1_policies_decisions_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PoliciesApi->list_admission_policy_decisions_api_v1_policies_decisions_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **limit** | **int**|  | [optional] [default to 100]
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

[**List[PolicyDecision]**](PolicyDecision.md)

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

# **test_admission_policy_api_v1_policies_policy_key_test_post**
> PolicyFixtureResult test_admission_policy_api_v1_policies_policy_key_test_post(policy_key, policy_fixture, revision=revision, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Test Admission Policy

### Example


```python
import amesh_client
from amesh_client.models.policy_fixture import PolicyFixture
from amesh_client.models.policy_fixture_result import PolicyFixtureResult
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
    api_instance = amesh_client.PoliciesApi(api_client)
    policy_key = 'policy_key_example' # str |
    policy_fixture = amesh_client.PolicyFixture() # PolicyFixture |
    revision = 56 # int |  (optional)
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Test Admission Policy
        api_response = api_instance.test_admission_policy_api_v1_policies_policy_key_test_post(policy_key, policy_fixture, revision=revision, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of PoliciesApi->test_admission_policy_api_v1_policies_policy_key_test_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PoliciesApi->test_admission_policy_api_v1_policies_policy_key_test_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **policy_key** | **str**|  |
 **policy_fixture** | **PolicyFixture**|  |
 **revision** | **int**|  | [optional]
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

**PolicyFixtureResult**

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

# **update_admission_policy_api_v1_policies_policy_key_put**
> PolicyRevision update_admission_policy_api_v1_policies_policy_key_put(policy_key, policy_document, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Update Admission Policy

### Example


```python
import amesh_client
from amesh_client.models.policy_document import PolicyDocument
from amesh_client.models.policy_revision import PolicyRevision
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
    api_instance = amesh_client.PoliciesApi(api_client)
    policy_key = 'policy_key_example' # str |
    policy_document = amesh_client.PolicyDocument() # PolicyDocument |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Update Admission Policy
        api_response = api_instance.update_admission_policy_api_v1_policies_policy_key_put(policy_key, policy_document, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of PoliciesApi->update_admission_policy_api_v1_policies_policy_key_put:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PoliciesApi->update_admission_policy_api_v1_policies_policy_key_put: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **policy_key** | **str**|  |
 **policy_document** | **PolicyDocument**|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

**PolicyRevision**

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

# **validate_flow_admission_policy_api_v1_policies_flows_validate_post**
> PolicyDecision validate_flow_admission_policy_api_v1_policies_flows_validate_post(authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Validate Flow Admission Policy

### Example


```python
import amesh_client
from amesh_client.models.policy_decision import PolicyDecision
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
    api_instance = amesh_client.PoliciesApi(api_client)
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Validate Flow Admission Policy
        api_response = api_instance.validate_flow_admission_policy_api_v1_policies_flows_validate_post(authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of PoliciesApi->validate_flow_admission_policy_api_v1_policies_flows_validate_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PoliciesApi->validate_flow_admission_policy_api_v1_policies_flows_validate_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

**PolicyDecision**

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
