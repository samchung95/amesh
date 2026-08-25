# amesh_client.ReleasesApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**apply_policy_api_v1_releases_policies_policy_id_apply_post**](ReleasesApi.md#apply_policy_api_v1_releases_policies_policy_id_apply_post) | **POST** /api/v1/releases/policies/{policy_id}/apply | Apply Policy
[**create_policy_api_v1_releases_policies_post**](ReleasesApi.md#create_policy_api_v1_releases_policies_post) | **POST** /api/v1/releases/policies | Create Policy
[**kill_switch_api_v1_releases_target_kind_target_key_kill_switch_post**](ReleasesApi.md#kill_switch_api_v1_releases_target_kind_target_key_kill_switch_post) | **POST** /api/v1/releases/{target_kind}/{target_key}/kill-switch | Kill Switch
[**preview_policy_api_v1_releases_policies_policy_id_preview_post**](ReleasesApi.md#preview_policy_api_v1_releases_policies_policy_id_preview_post) | **POST** /api/v1/releases/policies/{policy_id}/preview | Preview Policy
[**record_evidence_api_v1_releases_evidence_post**](ReleasesApi.md#record_evidence_api_v1_releases_evidence_post) | **POST** /api/v1/releases/evidence | Record Evidence
[**rollback_api_v1_releases_target_kind_target_key_rollback_post**](ReleasesApi.md#rollback_api_v1_releases_target_kind_target_key_rollback_post) | **POST** /api/v1/releases/{target_kind}/{target_key}/rollback | Rollback
[**target_history_api_v1_releases_target_kind_target_key_history_get**](ReleasesApi.md#target_history_api_v1_releases_target_kind_target_key_history_get) | **GET** /api/v1/releases/{target_kind}/{target_key}/history | Target History
[**target_state_api_v1_releases_target_kind_target_key_get**](ReleasesApi.md#target_state_api_v1_releases_target_kind_target_key_get) | **GET** /api/v1/releases/{target_kind}/{target_key} | Target State


# **apply_policy_api_v1_releases_policies_policy_id_apply_post**
> object apply_policy_api_v1_releases_policies_policy_id_apply_post(policy_id, promotion_apply_request, x_amesh_tenant=x_amesh_tenant, authorization=authorization, x_amesh_csrf=x_amesh_csrf)

Apply Policy

### Example


```python
import amesh_client
from amesh_client.models.promotion_apply_request import PromotionApplyRequest
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
    api_instance = amesh_client.ReleasesApi(api_client)
    policy_id = UUID('38400000-8cf0-11bd-b23e-10b96e4ef00d') # UUID |
    promotion_apply_request = amesh_client.PromotionApplyRequest() # PromotionApplyRequest |
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)

    try:
        # Apply Policy
        api_response = api_instance.apply_policy_api_v1_releases_policies_policy_id_apply_post(policy_id, promotion_apply_request, x_amesh_tenant=x_amesh_tenant, authorization=authorization, x_amesh_csrf=x_amesh_csrf)
        print("The response of ReleasesApi->apply_policy_api_v1_releases_policies_policy_id_apply_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ReleasesApi->apply_policy_api_v1_releases_policies_policy_id_apply_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **policy_id** | **UUID**|  |
 **promotion_apply_request** | [**PromotionApplyRequest**](PromotionApplyRequest.md)|  |
 **x_amesh_tenant** | **str**|  | [optional]
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]

### Return type

**object**

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

# **create_policy_api_v1_releases_policies_post**
> PromotionPolicyOutput create_policy_api_v1_releases_policies_post(promotion_policy_input, x_amesh_tenant=x_amesh_tenant, authorization=authorization, x_amesh_csrf=x_amesh_csrf)

Create Policy

### Example


```python
import amesh_client
from amesh_client.models.promotion_policy_input import PromotionPolicyInput
from amesh_client.models.promotion_policy_output import PromotionPolicyOutput
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
    api_instance = amesh_client.ReleasesApi(api_client)
    promotion_policy_input = amesh_client.PromotionPolicyInput() # PromotionPolicyInput |
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)

    try:
        # Create Policy
        api_response = api_instance.create_policy_api_v1_releases_policies_post(promotion_policy_input, x_amesh_tenant=x_amesh_tenant, authorization=authorization, x_amesh_csrf=x_amesh_csrf)
        print("The response of ReleasesApi->create_policy_api_v1_releases_policies_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ReleasesApi->create_policy_api_v1_releases_policies_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **promotion_policy_input** | [**PromotionPolicyInput**](PromotionPolicyInput.md)|  |
 **x_amesh_tenant** | **str**|  | [optional]
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]

### Return type

[**PromotionPolicyOutput**](PromotionPolicyOutput.md)

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

# **kill_switch_api_v1_releases_target_kind_target_key_kill_switch_post**
> object kill_switch_api_v1_releases_target_kind_target_key_kill_switch_post(target_kind, target_key, promotion_kill_switch_request, x_amesh_tenant=x_amesh_tenant, authorization=authorization, x_amesh_csrf=x_amesh_csrf)

Kill Switch

### Example


```python
import amesh_client
from amesh_client.models.promotion_kill_switch_request import PromotionKillSwitchRequest
from amesh_client.models.promotion_target_kind import PromotionTargetKind
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
    api_instance = amesh_client.ReleasesApi(api_client)
    target_kind = amesh_client.PromotionTargetKind() # PromotionTargetKind |
    target_key = 'target_key_example' # str |
    promotion_kill_switch_request = amesh_client.PromotionKillSwitchRequest() # PromotionKillSwitchRequest |
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)

    try:
        # Kill Switch
        api_response = api_instance.kill_switch_api_v1_releases_target_kind_target_key_kill_switch_post(target_kind, target_key, promotion_kill_switch_request, x_amesh_tenant=x_amesh_tenant, authorization=authorization, x_amesh_csrf=x_amesh_csrf)
        print("The response of ReleasesApi->kill_switch_api_v1_releases_target_kind_target_key_kill_switch_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ReleasesApi->kill_switch_api_v1_releases_target_kind_target_key_kill_switch_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **target_kind** | [**PromotionTargetKind**](.md)|  |
 **target_key** | **str**|  |
 **promotion_kill_switch_request** | [**PromotionKillSwitchRequest**](PromotionKillSwitchRequest.md)|  |
 **x_amesh_tenant** | **str**|  | [optional]
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]

### Return type

**object**

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

# **preview_policy_api_v1_releases_policies_policy_id_preview_post**
> object preview_policy_api_v1_releases_policies_policy_id_preview_post(policy_id, x_amesh_tenant=x_amesh_tenant, authorization=authorization, x_amesh_csrf=x_amesh_csrf, promotion_preview_request=promotion_preview_request)

Preview Policy

### Example


```python
import amesh_client
from amesh_client.models.promotion_preview_request import PromotionPreviewRequest
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
    api_instance = amesh_client.ReleasesApi(api_client)
    policy_id = UUID('38400000-8cf0-11bd-b23e-10b96e4ef00d') # UUID |
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    promotion_preview_request = amesh_client.PromotionPreviewRequest() # PromotionPreviewRequest |  (optional)

    try:
        # Preview Policy
        api_response = api_instance.preview_policy_api_v1_releases_policies_policy_id_preview_post(policy_id, x_amesh_tenant=x_amesh_tenant, authorization=authorization, x_amesh_csrf=x_amesh_csrf, promotion_preview_request=promotion_preview_request)
        print("The response of ReleasesApi->preview_policy_api_v1_releases_policies_policy_id_preview_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ReleasesApi->preview_policy_api_v1_releases_policies_policy_id_preview_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **policy_id** | **UUID**|  |
 **x_amesh_tenant** | **str**|  | [optional]
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **promotion_preview_request** | [**PromotionPreviewRequest**](PromotionPreviewRequest.md)|  | [optional]

### Return type

**object**

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

# **record_evidence_api_v1_releases_evidence_post**
> EvidenceArtifact record_evidence_api_v1_releases_evidence_post(evidence_artifact, x_amesh_tenant=x_amesh_tenant, authorization=authorization, x_amesh_csrf=x_amesh_csrf)

Record Evidence

### Example


```python
import amesh_client
from amesh_client.models.evidence_artifact import EvidenceArtifact
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
    api_instance = amesh_client.ReleasesApi(api_client)
    evidence_artifact = amesh_client.EvidenceArtifact() # EvidenceArtifact |
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)

    try:
        # Record Evidence
        api_response = api_instance.record_evidence_api_v1_releases_evidence_post(evidence_artifact, x_amesh_tenant=x_amesh_tenant, authorization=authorization, x_amesh_csrf=x_amesh_csrf)
        print("The response of ReleasesApi->record_evidence_api_v1_releases_evidence_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ReleasesApi->record_evidence_api_v1_releases_evidence_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **evidence_artifact** | [**EvidenceArtifact**](EvidenceArtifact.md)|  |
 **x_amesh_tenant** | **str**|  | [optional]
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]

### Return type

[**EvidenceArtifact**](EvidenceArtifact.md)

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

# **rollback_api_v1_releases_target_kind_target_key_rollback_post**
> object rollback_api_v1_releases_target_kind_target_key_rollback_post(target_kind, target_key, promotion_rollback_request, x_amesh_tenant=x_amesh_tenant, authorization=authorization, x_amesh_csrf=x_amesh_csrf)

Rollback

### Example


```python
import amesh_client
from amesh_client.models.promotion_rollback_request import PromotionRollbackRequest
from amesh_client.models.promotion_target_kind import PromotionTargetKind
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
    api_instance = amesh_client.ReleasesApi(api_client)
    target_kind = amesh_client.PromotionTargetKind() # PromotionTargetKind |
    target_key = 'target_key_example' # str |
    promotion_rollback_request = amesh_client.PromotionRollbackRequest() # PromotionRollbackRequest |
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)

    try:
        # Rollback
        api_response = api_instance.rollback_api_v1_releases_target_kind_target_key_rollback_post(target_kind, target_key, promotion_rollback_request, x_amesh_tenant=x_amesh_tenant, authorization=authorization, x_amesh_csrf=x_amesh_csrf)
        print("The response of ReleasesApi->rollback_api_v1_releases_target_kind_target_key_rollback_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ReleasesApi->rollback_api_v1_releases_target_kind_target_key_rollback_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **target_kind** | [**PromotionTargetKind**](.md)|  |
 **target_key** | **str**|  |
 **promotion_rollback_request** | [**PromotionRollbackRequest**](PromotionRollbackRequest.md)|  |
 **x_amesh_tenant** | **str**|  | [optional]
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]

### Return type

**object**

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

# **target_history_api_v1_releases_target_kind_target_key_history_get**
> object target_history_api_v1_releases_target_kind_target_key_history_get(target_kind, target_key, x_amesh_tenant=x_amesh_tenant, authorization=authorization, x_amesh_csrf=x_amesh_csrf)

Target History

### Example


```python
import amesh_client
from amesh_client.models.promotion_target_kind import PromotionTargetKind
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
    api_instance = amesh_client.ReleasesApi(api_client)
    target_kind = amesh_client.PromotionTargetKind() # PromotionTargetKind |
    target_key = 'target_key_example' # str |
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)

    try:
        # Target History
        api_response = api_instance.target_history_api_v1_releases_target_kind_target_key_history_get(target_kind, target_key, x_amesh_tenant=x_amesh_tenant, authorization=authorization, x_amesh_csrf=x_amesh_csrf)
        print("The response of ReleasesApi->target_history_api_v1_releases_target_kind_target_key_history_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ReleasesApi->target_history_api_v1_releases_target_kind_target_key_history_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **target_kind** | [**PromotionTargetKind**](.md)|  |
 **target_key** | **str**|  |
 **x_amesh_tenant** | **str**|  | [optional]
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]

### Return type

**object**

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

# **target_state_api_v1_releases_target_kind_target_key_get**
> object target_state_api_v1_releases_target_kind_target_key_get(target_kind, target_key, x_amesh_tenant=x_amesh_tenant, authorization=authorization, x_amesh_csrf=x_amesh_csrf)

Target State

### Example


```python
import amesh_client
from amesh_client.models.promotion_target_kind import PromotionTargetKind
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
    api_instance = amesh_client.ReleasesApi(api_client)
    target_kind = amesh_client.PromotionTargetKind() # PromotionTargetKind |
    target_key = 'target_key_example' # str |
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)

    try:
        # Target State
        api_response = api_instance.target_state_api_v1_releases_target_kind_target_key_get(target_kind, target_key, x_amesh_tenant=x_amesh_tenant, authorization=authorization, x_amesh_csrf=x_amesh_csrf)
        print("The response of ReleasesApi->target_state_api_v1_releases_target_kind_target_key_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ReleasesApi->target_state_api_v1_releases_target_kind_target_key_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **target_kind** | [**PromotionTargetKind**](.md)|  |
 **target_key** | **str**|  |
 **x_amesh_tenant** | **str**|  | [optional]
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]

### Return type

**object**

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
