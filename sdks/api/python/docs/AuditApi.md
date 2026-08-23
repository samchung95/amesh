# amesh_client.AuditApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_audit_legal_hold_api_v1_audit_legal_holds_post**](AuditApi.md#create_audit_legal_hold_api_v1_audit_legal_holds_post) | **POST** /api/v1/audit-legal-holds | Create Audit Legal Hold
[**create_compliance_evidence_api_v1_compliance_evidence_post**](AuditApi.md#create_compliance_evidence_api_v1_compliance_evidence_post) | **POST** /api/v1/compliance-evidence | Create Compliance Evidence
[**create_object_audit_export_api_v1_audit_exports_post**](AuditApi.md#create_object_audit_export_api_v1_audit_exports_post) | **POST** /api/v1/audit-exports | Create Object Audit Export
[**create_object_compliance_package_api_v1_compliance_packages_post**](AuditApi.md#create_object_compliance_package_api_v1_compliance_packages_post) | **POST** /api/v1/compliance-packages | Create Object Compliance Package
[**download_audit_export_api_v1_audit_events_export_get**](AuditApi.md#download_audit_export_api_v1_audit_events_export_get) | **GET** /api/v1/audit-events/export | Download Audit Export
[**download_compliance_package_api_v1_compliance_packages_export_get**](AuditApi.md#download_compliance_package_api_v1_compliance_packages_export_get) | **GET** /api/v1/compliance-packages/export | Download Compliance Package
[**get_audit_policy_api_v1_audit_policy_get**](AuditApi.md#get_audit_policy_api_v1_audit_policy_get) | **GET** /api/v1/audit-policy | Get Audit Policy
[**list_audit_events_api_v1_audit_events_get**](AuditApi.md#list_audit_events_api_v1_audit_events_get) | **GET** /api/v1/audit-events | List Audit Events
[**list_audit_legal_holds_api_v1_audit_legal_holds_get**](AuditApi.md#list_audit_legal_holds_api_v1_audit_legal_holds_get) | **GET** /api/v1/audit-legal-holds | List Audit Legal Holds
[**list_compliance_evidence_api_v1_compliance_evidence_get**](AuditApi.md#list_compliance_evidence_api_v1_compliance_evidence_get) | **GET** /api/v1/compliance-evidence | List Compliance Evidence
[**purge_audit_retention_api_v1_audit_retention_purge_post**](AuditApi.md#purge_audit_retention_api_v1_audit_retention_purge_post) | **POST** /api/v1/audit-retention/purge | Purge Audit Retention
[**release_audit_legal_hold_api_v1_audit_legal_holds_hold_id_delete**](AuditApi.md#release_audit_legal_hold_api_v1_audit_legal_holds_hold_id_delete) | **DELETE** /api/v1/audit-legal-holds/{hold_id} | Release Audit Legal Hold
[**update_audit_policy_api_v1_audit_policy_put**](AuditApi.md#update_audit_policy_api_v1_audit_policy_put) | **PUT** /api/v1/audit-policy | Update Audit Policy
[**verify_audit_integrity_api_v1_audit_events_integrity_get**](AuditApi.md#verify_audit_integrity_api_v1_audit_events_integrity_get) | **GET** /api/v1/audit-events/integrity | Verify Audit Integrity


# **create_audit_legal_hold_api_v1_audit_legal_holds_post**
> AuditLegalHold create_audit_legal_hold_api_v1_audit_legal_holds_post(audit_legal_hold_create, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Create Audit Legal Hold

### Example


```python
import amesh_client
from amesh_client.models.audit_legal_hold import AuditLegalHold
from amesh_client.models.audit_legal_hold_create import AuditLegalHoldCreate
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
    api_instance = amesh_client.AuditApi(api_client)
    audit_legal_hold_create = amesh_client.AuditLegalHoldCreate() # AuditLegalHoldCreate |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Create Audit Legal Hold
        api_response = api_instance.create_audit_legal_hold_api_v1_audit_legal_holds_post(audit_legal_hold_create, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of AuditApi->create_audit_legal_hold_api_v1_audit_legal_holds_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AuditApi->create_audit_legal_hold_api_v1_audit_legal_holds_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **audit_legal_hold_create** | [**AuditLegalHoldCreate**](AuditLegalHoldCreate.md)|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

[**AuditLegalHold**](AuditLegalHold.md)

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

# **create_compliance_evidence_api_v1_compliance_evidence_post**
> ComplianceEvidenceRecord create_compliance_evidence_api_v1_compliance_evidence_post(compliance_evidence_create, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Create Compliance Evidence

### Example


```python
import amesh_client
from amesh_client.models.compliance_evidence_create import ComplianceEvidenceCreate
from amesh_client.models.compliance_evidence_record import ComplianceEvidenceRecord
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
    api_instance = amesh_client.AuditApi(api_client)
    compliance_evidence_create = amesh_client.ComplianceEvidenceCreate() # ComplianceEvidenceCreate |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Create Compliance Evidence
        api_response = api_instance.create_compliance_evidence_api_v1_compliance_evidence_post(compliance_evidence_create, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of AuditApi->create_compliance_evidence_api_v1_compliance_evidence_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AuditApi->create_compliance_evidence_api_v1_compliance_evidence_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **compliance_evidence_create** | [**ComplianceEvidenceCreate**](ComplianceEvidenceCreate.md)|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

[**ComplianceEvidenceRecord**](ComplianceEvidenceRecord.md)

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

# **create_object_audit_export_api_v1_audit_exports_post**
> AuditExportReceipt create_object_audit_export_api_v1_audit_exports_post(audit_export_request, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Create Object Audit Export

### Example


```python
import amesh_client
from amesh_client.models.audit_export_receipt import AuditExportReceipt
from amesh_client.models.audit_export_request import AuditExportRequest
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
    api_instance = amesh_client.AuditApi(api_client)
    audit_export_request = amesh_client.AuditExportRequest() # AuditExportRequest |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Create Object Audit Export
        api_response = api_instance.create_object_audit_export_api_v1_audit_exports_post(audit_export_request, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of AuditApi->create_object_audit_export_api_v1_audit_exports_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AuditApi->create_object_audit_export_api_v1_audit_exports_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **audit_export_request** | [**AuditExportRequest**](AuditExportRequest.md)|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

[**AuditExportReceipt**](AuditExportReceipt.md)

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

# **create_object_compliance_package_api_v1_compliance_packages_post**
> AuditExportReceipt create_object_compliance_package_api_v1_compliance_packages_post(compliance_package_request, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Create Object Compliance Package

### Example


```python
import amesh_client
from amesh_client.models.audit_export_receipt import AuditExportReceipt
from amesh_client.models.compliance_package_request import CompliancePackageRequest
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
    api_instance = amesh_client.AuditApi(api_client)
    compliance_package_request = amesh_client.CompliancePackageRequest() # CompliancePackageRequest |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Create Object Compliance Package
        api_response = api_instance.create_object_compliance_package_api_v1_compliance_packages_post(compliance_package_request, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of AuditApi->create_object_compliance_package_api_v1_compliance_packages_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AuditApi->create_object_compliance_package_api_v1_compliance_packages_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **compliance_package_request** | [**CompliancePackageRequest**](CompliancePackageRequest.md)|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

[**AuditExportReceipt**](AuditExportReceipt.md)

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

# **download_audit_export_api_v1_audit_events_export_get**
> object download_audit_export_api_v1_audit_events_export_get(format=format, limit=limit, action=action, resource_type=resource_type, outcome=outcome, occurred_from=occurred_from, occurred_to=occurred_to, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Download Audit Export

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
    api_instance = amesh_client.AuditApi(api_client)
    format = amesh_client.AuditExportFormat() # AuditExportFormat |  (optional)
    limit = 10000 # int |  (optional) (default to 10000)
    action = 'action_example' # str |  (optional)
    resource_type = 'resource_type_example' # str |  (optional)
    outcome = 'outcome_example' # str |  (optional)
    occurred_from = '2013-10-20T19:20:30+01:00' # datetime |  (optional)
    occurred_to = '2013-10-20T19:20:30+01:00' # datetime |  (optional)
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Download Audit Export
        api_response = api_instance.download_audit_export_api_v1_audit_events_export_get(format=format, limit=limit, action=action, resource_type=resource_type, outcome=outcome, occurred_from=occurred_from, occurred_to=occurred_to, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of AuditApi->download_audit_export_api_v1_audit_events_export_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AuditApi->download_audit_export_api_v1_audit_events_export_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **format** | [**AuditExportFormat**](.md)|  | [optional]
 **limit** | **int**|  | [optional] [default to 10000]
 **action** | **str**|  | [optional]
 **resource_type** | **str**|  | [optional]
 **outcome** | **str**|  | [optional]
 **occurred_from** | **datetime**|  | [optional]
 **occurred_to** | **datetime**|  | [optional]
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

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

# **download_compliance_package_api_v1_compliance_packages_export_get**
> object download_compliance_package_api_v1_compliance_packages_export_get(occurred_from=occurred_from, occurred_to=occurred_to, max_audit_events=max_audit_events, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Download Compliance Package

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
    api_instance = amesh_client.AuditApi(api_client)
    occurred_from = '2013-10-20T19:20:30+01:00' # datetime |  (optional)
    occurred_to = '2013-10-20T19:20:30+01:00' # datetime |  (optional)
    max_audit_events = 10000 # int |  (optional) (default to 10000)
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Download Compliance Package
        api_response = api_instance.download_compliance_package_api_v1_compliance_packages_export_get(occurred_from=occurred_from, occurred_to=occurred_to, max_audit_events=max_audit_events, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of AuditApi->download_compliance_package_api_v1_compliance_packages_export_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AuditApi->download_compliance_package_api_v1_compliance_packages_export_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **occurred_from** | **datetime**|  | [optional]
 **occurred_to** | **datetime**|  | [optional]
 **max_audit_events** | **int**|  | [optional] [default to 10000]
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

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

# **get_audit_policy_api_v1_audit_policy_get**
> AuditRetentionPolicy get_audit_policy_api_v1_audit_policy_get(authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Get Audit Policy

### Example


```python
import amesh_client
from amesh_client.models.audit_retention_policy import AuditRetentionPolicy
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
    api_instance = amesh_client.AuditApi(api_client)
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Get Audit Policy
        api_response = api_instance.get_audit_policy_api_v1_audit_policy_get(authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of AuditApi->get_audit_policy_api_v1_audit_policy_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AuditApi->get_audit_policy_api_v1_audit_policy_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

[**AuditRetentionPolicy**](AuditRetentionPolicy.md)

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

# **list_audit_events_api_v1_audit_events_get**
> AuditEventPage list_audit_events_api_v1_audit_events_get(cursor=cursor, limit=limit, action=action, resource_type=resource_type, outcome=outcome, occurred_from=occurred_from, occurred_to=occurred_to, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

List Audit Events

### Example


```python
import amesh_client
from amesh_client.models.audit_event_page import AuditEventPage
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
    api_instance = amesh_client.AuditApi(api_client)
    cursor = 56 # int |  (optional)
    limit = 100 # int |  (optional) (default to 100)
    action = 'action_example' # str |  (optional)
    resource_type = 'resource_type_example' # str |  (optional)
    outcome = 'outcome_example' # str |  (optional)
    occurred_from = '2013-10-20T19:20:30+01:00' # datetime |  (optional)
    occurred_to = '2013-10-20T19:20:30+01:00' # datetime |  (optional)
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # List Audit Events
        api_response = api_instance.list_audit_events_api_v1_audit_events_get(cursor=cursor, limit=limit, action=action, resource_type=resource_type, outcome=outcome, occurred_from=occurred_from, occurred_to=occurred_to, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of AuditApi->list_audit_events_api_v1_audit_events_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AuditApi->list_audit_events_api_v1_audit_events_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **cursor** | **int**|  | [optional]
 **limit** | **int**|  | [optional] [default to 100]
 **action** | **str**|  | [optional]
 **resource_type** | **str**|  | [optional]
 **outcome** | **str**|  | [optional]
 **occurred_from** | **datetime**|  | [optional]
 **occurred_to** | **datetime**|  | [optional]
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

[**AuditEventPage**](AuditEventPage.md)

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

# **list_audit_legal_holds_api_v1_audit_legal_holds_get**
> List[AuditLegalHold] list_audit_legal_holds_api_v1_audit_legal_holds_get(authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

List Audit Legal Holds

### Example


```python
import amesh_client
from amesh_client.models.audit_legal_hold import AuditLegalHold
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
    api_instance = amesh_client.AuditApi(api_client)
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # List Audit Legal Holds
        api_response = api_instance.list_audit_legal_holds_api_v1_audit_legal_holds_get(authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of AuditApi->list_audit_legal_holds_api_v1_audit_legal_holds_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AuditApi->list_audit_legal_holds_api_v1_audit_legal_holds_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

[**List[AuditLegalHold]**](AuditLegalHold.md)

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

# **list_compliance_evidence_api_v1_compliance_evidence_get**
> List[ComplianceEvidenceRecord] list_compliance_evidence_api_v1_compliance_evidence_get(authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

List Compliance Evidence

### Example


```python
import amesh_client
from amesh_client.models.compliance_evidence_record import ComplianceEvidenceRecord
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
    api_instance = amesh_client.AuditApi(api_client)
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # List Compliance Evidence
        api_response = api_instance.list_compliance_evidence_api_v1_compliance_evidence_get(authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of AuditApi->list_compliance_evidence_api_v1_compliance_evidence_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AuditApi->list_compliance_evidence_api_v1_compliance_evidence_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

[**List[ComplianceEvidenceRecord]**](ComplianceEvidenceRecord.md)

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

# **purge_audit_retention_api_v1_audit_retention_purge_post**
> AuditRetentionResult purge_audit_retention_api_v1_audit_retention_purge_post(authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Purge Audit Retention

### Example


```python
import amesh_client
from amesh_client.models.audit_retention_result import AuditRetentionResult
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
    api_instance = amesh_client.AuditApi(api_client)
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Purge Audit Retention
        api_response = api_instance.purge_audit_retention_api_v1_audit_retention_purge_post(authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of AuditApi->purge_audit_retention_api_v1_audit_retention_purge_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AuditApi->purge_audit_retention_api_v1_audit_retention_purge_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

[**AuditRetentionResult**](AuditRetentionResult.md)

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

# **release_audit_legal_hold_api_v1_audit_legal_holds_hold_id_delete**
> AuditLegalHold release_audit_legal_hold_api_v1_audit_legal_holds_hold_id_delete(hold_id, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Release Audit Legal Hold

### Example


```python
import amesh_client
from amesh_client.models.audit_legal_hold import AuditLegalHold
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
    api_instance = amesh_client.AuditApi(api_client)
    hold_id = UUID('38400000-8cf0-11bd-b23e-10b96e4ef00d') # UUID |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Release Audit Legal Hold
        api_response = api_instance.release_audit_legal_hold_api_v1_audit_legal_holds_hold_id_delete(hold_id, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of AuditApi->release_audit_legal_hold_api_v1_audit_legal_holds_hold_id_delete:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AuditApi->release_audit_legal_hold_api_v1_audit_legal_holds_hold_id_delete: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **hold_id** | **UUID**|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

[**AuditLegalHold**](AuditLegalHold.md)

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

# **update_audit_policy_api_v1_audit_policy_put**
> AuditRetentionPolicy update_audit_policy_api_v1_audit_policy_put(audit_retention_policy_update, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Update Audit Policy

### Example


```python
import amesh_client
from amesh_client.models.audit_retention_policy import AuditRetentionPolicy
from amesh_client.models.audit_retention_policy_update import AuditRetentionPolicyUpdate
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
    api_instance = amesh_client.AuditApi(api_client)
    audit_retention_policy_update = amesh_client.AuditRetentionPolicyUpdate() # AuditRetentionPolicyUpdate |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Update Audit Policy
        api_response = api_instance.update_audit_policy_api_v1_audit_policy_put(audit_retention_policy_update, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of AuditApi->update_audit_policy_api_v1_audit_policy_put:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AuditApi->update_audit_policy_api_v1_audit_policy_put: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **audit_retention_policy_update** | [**AuditRetentionPolicyUpdate**](AuditRetentionPolicyUpdate.md)|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

[**AuditRetentionPolicy**](AuditRetentionPolicy.md)

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

# **verify_audit_integrity_api_v1_audit_events_integrity_get**
> AuditIntegrityReport verify_audit_integrity_api_v1_audit_events_integrity_get(authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Verify Audit Integrity

### Example


```python
import amesh_client
from amesh_client.models.audit_integrity_report import AuditIntegrityReport
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
    api_instance = amesh_client.AuditApi(api_client)
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Verify Audit Integrity
        api_response = api_instance.verify_audit_integrity_api_v1_audit_events_integrity_get(authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of AuditApi->verify_audit_integrity_api_v1_audit_events_integrity_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AuditApi->verify_audit_integrity_api_v1_audit_events_integrity_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

[**AuditIntegrityReport**](AuditIntegrityReport.md)

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
