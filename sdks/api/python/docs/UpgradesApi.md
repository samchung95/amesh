# amesh_client.UpgradesApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_upgrade_policy_api_v1_upgrades_policy_get**](UpgradesApi.md#get_upgrade_policy_api_v1_upgrades_policy_get) | **GET** /api/v1/upgrades/policy | Get Upgrade Policy
[**migrate_upgrade_configuration_api_v1_upgrades_configuration_migrate_post**](UpgradesApi.md#migrate_upgrade_configuration_api_v1_upgrades_configuration_migrate_post) | **POST** /api/v1/upgrades/configuration/migrate | Migrate Upgrade Configuration
[**preview_upgrade_event_upcast_api_v1_upgrades_events_upcast_get**](UpgradesApi.md#preview_upgrade_event_upcast_api_v1_upgrades_events_upcast_get) | **GET** /api/v1/upgrades/events/upcast | Preview Upgrade Event Upcast
[**run_upgrade_event_upcast_api_v1_upgrades_events_upcast_post**](UpgradesApi.md#run_upgrade_event_upcast_api_v1_upgrades_events_upcast_post) | **POST** /api/v1/upgrades/events/upcast | Run Upgrade Event Upcast
[**run_upgrade_postflight_api_v1_upgrades_postflight_post**](UpgradesApi.md#run_upgrade_postflight_api_v1_upgrades_postflight_post) | **POST** /api/v1/upgrades/postflight | Run Upgrade Postflight
[**run_upgrade_preflight_api_v1_upgrades_preflight_post**](UpgradesApi.md#run_upgrade_preflight_api_v1_upgrades_preflight_post) | **POST** /api/v1/upgrades/preflight | Run Upgrade Preflight


# **get_upgrade_policy_api_v1_upgrades_policy_get**
> UpgradePolicy get_upgrade_policy_api_v1_upgrades_policy_get(authorization=authorization, x_amesh_csrf=x_amesh_csrf)

Get Upgrade Policy

### Example


```python
import amesh_client
from amesh_client.models.upgrade_policy import UpgradePolicy
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
    api_instance = amesh_client.UpgradesApi(api_client)
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)

    try:
        # Get Upgrade Policy
        api_response = api_instance.get_upgrade_policy_api_v1_upgrades_policy_get(authorization=authorization, x_amesh_csrf=x_amesh_csrf)
        print("The response of UpgradesApi->get_upgrade_policy_api_v1_upgrades_policy_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling UpgradesApi->get_upgrade_policy_api_v1_upgrades_policy_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]

### Return type

[**UpgradePolicy**](UpgradePolicy.md)

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

# **migrate_upgrade_configuration_api_v1_upgrades_configuration_migrate_post**
> ConfigurationMigration migrate_upgrade_configuration_api_v1_upgrades_configuration_migrate_post(configuration_migration_request, authorization=authorization, x_amesh_csrf=x_amesh_csrf)

Migrate Upgrade Configuration

### Example


```python
import amesh_client
from amesh_client.models.configuration_migration import ConfigurationMigration
from amesh_client.models.configuration_migration_request import ConfigurationMigrationRequest
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
    api_instance = amesh_client.UpgradesApi(api_client)
    configuration_migration_request = amesh_client.ConfigurationMigrationRequest() # ConfigurationMigrationRequest |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)

    try:
        # Migrate Upgrade Configuration
        api_response = api_instance.migrate_upgrade_configuration_api_v1_upgrades_configuration_migrate_post(configuration_migration_request, authorization=authorization, x_amesh_csrf=x_amesh_csrf)
        print("The response of UpgradesApi->migrate_upgrade_configuration_api_v1_upgrades_configuration_migrate_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling UpgradesApi->migrate_upgrade_configuration_api_v1_upgrades_configuration_migrate_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **configuration_migration_request** | [**ConfigurationMigrationRequest**](ConfigurationMigrationRequest.md)|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]

### Return type

[**ConfigurationMigration**](ConfigurationMigration.md)

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

# **preview_upgrade_event_upcast_api_v1_upgrades_events_upcast_get**
> PersistedEventMigration preview_upgrade_event_upcast_api_v1_upgrades_events_upcast_get(authorization=authorization, x_amesh_csrf=x_amesh_csrf)

Preview Upgrade Event Upcast

### Example


```python
import amesh_client
from amesh_client.models.persisted_event_migration import PersistedEventMigration
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
    api_instance = amesh_client.UpgradesApi(api_client)
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)

    try:
        # Preview Upgrade Event Upcast
        api_response = api_instance.preview_upgrade_event_upcast_api_v1_upgrades_events_upcast_get(authorization=authorization, x_amesh_csrf=x_amesh_csrf)
        print("The response of UpgradesApi->preview_upgrade_event_upcast_api_v1_upgrades_events_upcast_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling UpgradesApi->preview_upgrade_event_upcast_api_v1_upgrades_events_upcast_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]

### Return type

[**PersistedEventMigration**](PersistedEventMigration.md)

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

# **run_upgrade_event_upcast_api_v1_upgrades_events_upcast_post**
> PersistedEventMigration run_upgrade_event_upcast_api_v1_upgrades_events_upcast_post(persisted_event_migration_request, authorization=authorization, x_amesh_csrf=x_amesh_csrf)

Run Upgrade Event Upcast

### Example


```python
import amesh_client
from amesh_client.models.persisted_event_migration import PersistedEventMigration
from amesh_client.models.persisted_event_migration_request import PersistedEventMigrationRequest
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
    api_instance = amesh_client.UpgradesApi(api_client)
    persisted_event_migration_request = amesh_client.PersistedEventMigrationRequest() # PersistedEventMigrationRequest |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)

    try:
        # Run Upgrade Event Upcast
        api_response = api_instance.run_upgrade_event_upcast_api_v1_upgrades_events_upcast_post(persisted_event_migration_request, authorization=authorization, x_amesh_csrf=x_amesh_csrf)
        print("The response of UpgradesApi->run_upgrade_event_upcast_api_v1_upgrades_events_upcast_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling UpgradesApi->run_upgrade_event_upcast_api_v1_upgrades_events_upcast_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **persisted_event_migration_request** | [**PersistedEventMigrationRequest**](PersistedEventMigrationRequest.md)|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]

### Return type

[**PersistedEventMigration**](PersistedEventMigration.md)

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

# **run_upgrade_postflight_api_v1_upgrades_postflight_post**
> UpgradeReport run_upgrade_postflight_api_v1_upgrades_postflight_post(upgrade_report_request, authorization=authorization, x_amesh_csrf=x_amesh_csrf)

Run Upgrade Postflight

### Example


```python
import amesh_client
from amesh_client.models.upgrade_report import UpgradeReport
from amesh_client.models.upgrade_report_request import UpgradeReportRequest
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
    api_instance = amesh_client.UpgradesApi(api_client)
    upgrade_report_request = amesh_client.UpgradeReportRequest() # UpgradeReportRequest |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)

    try:
        # Run Upgrade Postflight
        api_response = api_instance.run_upgrade_postflight_api_v1_upgrades_postflight_post(upgrade_report_request, authorization=authorization, x_amesh_csrf=x_amesh_csrf)
        print("The response of UpgradesApi->run_upgrade_postflight_api_v1_upgrades_postflight_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling UpgradesApi->run_upgrade_postflight_api_v1_upgrades_postflight_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **upgrade_report_request** | [**UpgradeReportRequest**](UpgradeReportRequest.md)|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]

### Return type

[**UpgradeReport**](UpgradeReport.md)

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

# **run_upgrade_preflight_api_v1_upgrades_preflight_post**
> UpgradeReport run_upgrade_preflight_api_v1_upgrades_preflight_post(upgrade_report_request, authorization=authorization, x_amesh_csrf=x_amesh_csrf)

Run Upgrade Preflight

### Example


```python
import amesh_client
from amesh_client.models.upgrade_report import UpgradeReport
from amesh_client.models.upgrade_report_request import UpgradeReportRequest
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
    api_instance = amesh_client.UpgradesApi(api_client)
    upgrade_report_request = amesh_client.UpgradeReportRequest() # UpgradeReportRequest |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)

    try:
        # Run Upgrade Preflight
        api_response = api_instance.run_upgrade_preflight_api_v1_upgrades_preflight_post(upgrade_report_request, authorization=authorization, x_amesh_csrf=x_amesh_csrf)
        print("The response of UpgradesApi->run_upgrade_preflight_api_v1_upgrades_preflight_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling UpgradesApi->run_upgrade_preflight_api_v1_upgrades_preflight_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **upgrade_report_request** | [**UpgradeReportRequest**](UpgradeReportRequest.md)|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]

### Return type

[**UpgradeReport**](UpgradeReport.md)

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
