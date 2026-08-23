# amesh_client.AssetsApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**declare_asset_lineage_api_v1_assets_lineage_post**](AssetsApi.md#declare_asset_lineage_api_v1_assets_lineage_post) | **POST** /api/v1/assets/lineage | Declare Asset Lineage
[**export_asset_catalog_api_v1_assets_export_openlineage_get**](AssetsApi.md#export_asset_catalog_api_v1_assets_export_openlineage_get) | **GET** /api/v1/assets/export/openlineage | Export Asset Catalog
[**get_asset_catalog_entry_api_v1_assets_asset_id_get**](AssetsApi.md#get_asset_catalog_entry_api_v1_assets_asset_id_get) | **GET** /api/v1/assets/{asset_id} | Get Asset Catalog Entry
[**list_assets_api_v1_assets_get**](AssetsApi.md#list_assets_api_v1_assets_get) | **GET** /api/v1/assets | List Assets
[**record_asset_observation_api_v1_assets_observations_post**](AssetsApi.md#record_asset_observation_api_v1_assets_observations_post) | **POST** /api/v1/assets/observations | Record Asset Observation
[**register_asset_api_v1_assets_post**](AssetsApi.md#register_asset_api_v1_assets_post) | **POST** /api/v1/assets | Register Asset


# **declare_asset_lineage_api_v1_assets_lineage_post**
> AssetLineageEdge declare_asset_lineage_api_v1_assets_lineage_post(asset_lineage_declaration, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Declare Asset Lineage

### Example


```python
import amesh_client
from amesh_client.models.asset_lineage_declaration import AssetLineageDeclaration
from amesh_client.models.asset_lineage_edge import AssetLineageEdge
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
    api_instance = amesh_client.AssetsApi(api_client)
    asset_lineage_declaration = amesh_client.AssetLineageDeclaration() # AssetLineageDeclaration |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Declare Asset Lineage
        api_response = api_instance.declare_asset_lineage_api_v1_assets_lineage_post(asset_lineage_declaration, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of AssetsApi->declare_asset_lineage_api_v1_assets_lineage_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AssetsApi->declare_asset_lineage_api_v1_assets_lineage_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **asset_lineage_declaration** | [**AssetLineageDeclaration**](AssetLineageDeclaration.md)|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

[**AssetLineageEdge**](AssetLineageEdge.md)

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

# **export_asset_catalog_api_v1_assets_export_openlineage_get**
> AssetCatalogExport export_asset_catalog_api_v1_assets_export_openlineage_get(namespace=namespace, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Export Asset Catalog

### Example


```python
import amesh_client
from amesh_client.models.asset_catalog_export import AssetCatalogExport
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
    api_instance = amesh_client.AssetsApi(api_client)
    namespace = 'namespace_example' # str |  (optional)
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Export Asset Catalog
        api_response = api_instance.export_asset_catalog_api_v1_assets_export_openlineage_get(namespace=namespace, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of AssetsApi->export_asset_catalog_api_v1_assets_export_openlineage_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AssetsApi->export_asset_catalog_api_v1_assets_export_openlineage_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **namespace** | **str**|  | [optional]
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

[**AssetCatalogExport**](AssetCatalogExport.md)

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

# **get_asset_catalog_entry_api_v1_assets_asset_id_get**
> AssetCatalogEntry get_asset_catalog_entry_api_v1_assets_asset_id_get(asset_id, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Get Asset Catalog Entry

### Example


```python
import amesh_client
from amesh_client.models.asset_catalog_entry import AssetCatalogEntry
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
    api_instance = amesh_client.AssetsApi(api_client)
    asset_id = UUID('38400000-8cf0-11bd-b23e-10b96e4ef00d') # UUID |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Get Asset Catalog Entry
        api_response = api_instance.get_asset_catalog_entry_api_v1_assets_asset_id_get(asset_id, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of AssetsApi->get_asset_catalog_entry_api_v1_assets_asset_id_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AssetsApi->get_asset_catalog_entry_api_v1_assets_asset_id_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **asset_id** | **UUID**|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

[**AssetCatalogEntry**](AssetCatalogEntry.md)

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

# **list_assets_api_v1_assets_get**
> List[PersistedAsset] list_assets_api_v1_assets_get(namespace=namespace, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

List Assets

### Example


```python
import amesh_client
from amesh_client.models.persisted_asset import PersistedAsset
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
    api_instance = amesh_client.AssetsApi(api_client)
    namespace = 'namespace_example' # str |  (optional)
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # List Assets
        api_response = api_instance.list_assets_api_v1_assets_get(namespace=namespace, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of AssetsApi->list_assets_api_v1_assets_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AssetsApi->list_assets_api_v1_assets_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **namespace** | **str**|  | [optional]
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

[**List[PersistedAsset]**](PersistedAsset.md)

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

# **record_asset_observation_api_v1_assets_observations_post**
> AssetObservation record_asset_observation_api_v1_assets_observations_post(asset_observation_create, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Record Asset Observation

### Example


```python
import amesh_client
from amesh_client.models.asset_observation import AssetObservation
from amesh_client.models.asset_observation_create import AssetObservationCreate
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
    api_instance = amesh_client.AssetsApi(api_client)
    asset_observation_create = amesh_client.AssetObservationCreate() # AssetObservationCreate |
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Record Asset Observation
        api_response = api_instance.record_asset_observation_api_v1_assets_observations_post(asset_observation_create, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of AssetsApi->record_asset_observation_api_v1_assets_observations_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AssetsApi->record_asset_observation_api_v1_assets_observations_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **asset_observation_create** | [**AssetObservationCreate**](AssetObservationCreate.md)|  |
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

[**AssetObservation**](AssetObservation.md)

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

# **register_asset_api_v1_assets_post**
> PersistedAsset register_asset_api_v1_assets_post(asset_metadata, expected_version=expected_version, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)

Register Asset

### Example


```python
import amesh_client
from amesh_client.models.asset_metadata import AssetMetadata
from amesh_client.models.persisted_asset import PersistedAsset
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
    api_instance = amesh_client.AssetsApi(api_client)
    asset_metadata = amesh_client.AssetMetadata() # AssetMetadata |
    expected_version = 56 # int |  (optional)
    authorization = 'authorization_example' # str |  (optional)
    x_amesh_csrf = 'x_amesh_csrf_example' # str |  (optional)
    x_amesh_tenant = 'x_amesh_tenant_example' # str |  (optional)

    try:
        # Register Asset
        api_response = api_instance.register_asset_api_v1_assets_post(asset_metadata, expected_version=expected_version, authorization=authorization, x_amesh_csrf=x_amesh_csrf, x_amesh_tenant=x_amesh_tenant)
        print("The response of AssetsApi->register_asset_api_v1_assets_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AssetsApi->register_asset_api_v1_assets_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **asset_metadata** | [**AssetMetadata**](AssetMetadata.md)|  |
 **expected_version** | **int**|  | [optional]
 **authorization** | **str**|  | [optional]
 **x_amesh_csrf** | **str**|  | [optional]
 **x_amesh_tenant** | **str**|  | [optional]

### Return type

[**PersistedAsset**](PersistedAsset.md)

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
