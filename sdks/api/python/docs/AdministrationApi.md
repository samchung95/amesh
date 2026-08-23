# amesh_client.AdministrationApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**apply_administration_control_api_v1_admin_controls_key_put**](AdministrationApi.md#apply_administration_control_api_v1_admin_controls_key_put) | **PUT** /api/v1/admin/controls/{key} | Apply Administration Control
[**list_administration_audit_api_v1_admin_audit_get**](AdministrationApi.md#list_administration_audit_api_v1_admin_audit_get) | **GET** /api/v1/admin/audit | List Administration Audit
[**list_administration_controls_api_v1_admin_controls_get**](AdministrationApi.md#list_administration_controls_api_v1_admin_controls_get) | **GET** /api/v1/admin/controls | List Administration Controls
[**preview_administration_control_api_v1_admin_controls_preview_post**](AdministrationApi.md#preview_administration_control_api_v1_admin_controls_preview_post) | **POST** /api/v1/admin/controls/preview | Preview Administration Control


# **apply_administration_control_api_v1_admin_controls_key_put**
> AdministrationControl apply_administration_control_api_v1_admin_controls_key_put(key, administration_apply_request, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Apply Administration Control

### Example


```python
import amesh_client
from amesh_client.models.administration_apply_request import AdministrationApplyRequest
from amesh_client.models.administration_control import AdministrationControl
from amesh_client.models.administration_control_key import AdministrationControlKey
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
    api_instance = amesh_client.AdministrationApi(api_client)
    key = amesh_client.AdministrationControlKey() # AdministrationControlKey |
    administration_apply_request = amesh_client.AdministrationApplyRequest() # AdministrationApplyRequest |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Apply Administration Control
        api_response = api_instance.apply_administration_control_api_v1_admin_controls_key_put(key, administration_apply_request, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of AdministrationApi->apply_administration_control_api_v1_admin_controls_key_put:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AdministrationApi->apply_administration_control_api_v1_admin_controls_key_put: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **key** | [**AdministrationControlKey**](.md)|  |
 **administration_apply_request** | [**AdministrationApplyRequest**](AdministrationApplyRequest.md)|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

[**AdministrationControl**](AdministrationControl.md)

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

# **list_administration_audit_api_v1_admin_audit_get**
> List[AdministrationAuditEntry] list_administration_audit_api_v1_admin_audit_get(limit=limit, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

List Administration Audit

### Example


```python
import amesh_client
from amesh_client.models.administration_audit_entry import AdministrationAuditEntry
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
    api_instance = amesh_client.AdministrationApi(api_client)
    limit = 100 # int |  (optional) (default to 100)
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # List Administration Audit
        api_response = api_instance.list_administration_audit_api_v1_admin_audit_get(limit=limit, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of AdministrationApi->list_administration_audit_api_v1_admin_audit_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AdministrationApi->list_administration_audit_api_v1_admin_audit_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **limit** | **int**|  | [optional] [default to 100]
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

[**List[AdministrationAuditEntry]**](AdministrationAuditEntry.md)

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

# **list_administration_controls_api_v1_admin_controls_get**
> List[AdministrationControl] list_administration_controls_api_v1_admin_controls_get(authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

List Administration Controls

### Example


```python
import amesh_client
from amesh_client.models.administration_control import AdministrationControl
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
    api_instance = amesh_client.AdministrationApi(api_client)
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # List Administration Controls
        api_response = api_instance.list_administration_controls_api_v1_admin_controls_get(authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of AdministrationApi->list_administration_controls_api_v1_admin_controls_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AdministrationApi->list_administration_controls_api_v1_admin_controls_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

[**List[AdministrationControl]**](AdministrationControl.md)

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

# **preview_administration_control_api_v1_admin_controls_preview_post**
> AdministrationImpactPreview preview_administration_control_api_v1_admin_controls_preview_post(administration_control_draft, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Preview Administration Control

### Example


```python
import amesh_client
from amesh_client.models.administration_control_draft import AdministrationControlDraft
from amesh_client.models.administration_impact_preview import AdministrationImpactPreview
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
    api_instance = amesh_client.AdministrationApi(api_client)
    administration_control_draft = amesh_client.AdministrationControlDraft() # AdministrationControlDraft |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Preview Administration Control
        api_response = api_instance.preview_administration_control_api_v1_admin_controls_preview_post(administration_control_draft, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of AdministrationApi->preview_administration_control_api_v1_admin_controls_preview_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AdministrationApi->preview_administration_control_api_v1_admin_controls_preview_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **administration_control_draft** | [**AdministrationControlDraft**](AdministrationControlDraft.md)|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

[**AdministrationImpactPreview**](AdministrationImpactPreview.md)

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
