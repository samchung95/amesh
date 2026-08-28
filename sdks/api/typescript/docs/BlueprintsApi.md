# BlueprintsApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**getBlueprintVersionApiV1BlueprintsBlueprintIdVersionGet**](BlueprintsApi.md#getblueprintversionapiv1blueprintsblueprintidversionget) | **GET** /api/v1/blueprints/{blueprint_id}/{version} | Get Blueprint Version |
| [**getBlueprintsApiV1BlueprintsGet**](BlueprintsApi.md#getblueprintsapiv1blueprintsget) | **GET** /api/v1/blueprints | Get Blueprints |
| [**instantiateBlueprintDraftApiV1BlueprintsBlueprintIdVersionInstantiatePost**](BlueprintsApi.md#instantiateblueprintdraftapiv1blueprintsblueprintidversioninstantiatepost) | **POST** /api/v1/blueprints/{blueprint_id}/{version}/instantiate | Instantiate Blueprint Draft |
| [**simulatePlaygroundApiV1PlaygroundSimulatePost**](BlueprintsApi.md#simulateplaygroundapiv1playgroundsimulatepost) | **POST** /api/v1/playground/simulate | Simulate Playground |



## getBlueprintVersionApiV1BlueprintsBlueprintIdVersionGet

> BlueprintDefinition getBlueprintVersionApiV1BlueprintsBlueprintIdVersionGet(blueprintId, version, authorization, xAmeshCSRF, xAmeshTenant)

Get Blueprint Version

### Example

```ts
import {
  Configuration,
  BlueprintsApi,
} from '@amesh/client';
import type { GetBlueprintVersionApiV1BlueprintsBlueprintIdVersionGetRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new BlueprintsApi();

  const body = {
    // string
    blueprintId: blueprintId_example,
    // string
    version: version_example,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies GetBlueprintVersionApiV1BlueprintsBlueprintIdVersionGetRequest;

  try {
    const data = await api.getBlueprintVersionApiV1BlueprintsBlueprintIdVersionGet(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **blueprintId** | `string` |  | [Defaults to `undefined`] |
| **version** | `string` |  | [Defaults to `undefined`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

**BlueprintDefinition**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## getBlueprintsApiV1BlueprintsGet

> Array&lt;BlueprintSummary&gt; getBlueprintsApiV1BlueprintsGet(q, source, authorization, xAmeshCSRF, xAmeshTenant)

Get Blueprints

### Example

```ts
import {
  Configuration,
  BlueprintsApi,
} from '@amesh/client';
import type { GetBlueprintsApiV1BlueprintsGetRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new BlueprintsApi();

  const body = {
    // string (optional)
    q: q_example,
    // BlueprintCatalogSource (optional)
    source: ...,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies GetBlueprintsApiV1BlueprintsGetRequest;

  try {
    const data = await api.getBlueprintsApiV1BlueprintsGet(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **q** | `string` |  | [Optional] [Defaults to `undefined`] |
| **source** | `BlueprintCatalogSource` |  | [Optional] [Defaults to `undefined`] [Enum: BUILTIN, ORGANIZATION, COMMUNITY] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

**Array&lt;BlueprintSummary&gt;**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## instantiateBlueprintDraftApiV1BlueprintsBlueprintIdVersionInstantiatePost

> BlueprintDraftResponse instantiateBlueprintDraftApiV1BlueprintsBlueprintIdVersionInstantiatePost(blueprintId, version, blueprintInstantiationRequest, authorization, xAmeshCSRF, xAmeshTenant)

Instantiate Blueprint Draft

### Example

```ts
import {
  Configuration,
  BlueprintsApi,
} from '@amesh/client';
import type { InstantiateBlueprintDraftApiV1BlueprintsBlueprintIdVersionInstantiatePostRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new BlueprintsApi();

  const body = {
    // string
    blueprintId: blueprintId_example,
    // string
    version: version_example,
    // BlueprintInstantiationRequest
    blueprintInstantiationRequest: ...,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies InstantiateBlueprintDraftApiV1BlueprintsBlueprintIdVersionInstantiatePostRequest;

  try {
    const data = await api.instantiateBlueprintDraftApiV1BlueprintsBlueprintIdVersionInstantiatePost(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **blueprintId** | `string` |  | [Defaults to `undefined`] |
| **version** | `string` |  | [Defaults to `undefined`] |
| **blueprintInstantiationRequest** | BlueprintInstantiationRequest |  | |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

**BlueprintDraftResponse**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## simulatePlaygroundApiV1PlaygroundSimulatePost

> PlaygroundSimulationResponse simulatePlaygroundApiV1PlaygroundSimulatePost(playgroundSimulationRequest, authorization, xAmeshCSRF, xAmeshTenant)

Simulate Playground

### Example

```ts
import {
  Configuration,
  BlueprintsApi,
} from '@amesh/client';
import type { SimulatePlaygroundApiV1PlaygroundSimulatePostRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new BlueprintsApi();

  const body = {
    // PlaygroundSimulationRequest
    playgroundSimulationRequest: ...,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
    // string (optional)
    xAmeshTenant: xAmeshTenant_example,
  } satisfies SimulatePlaygroundApiV1PlaygroundSimulatePostRequest;

  try {
    const data = await api.simulatePlaygroundApiV1PlaygroundSimulatePost(body);
    console.log(data);
  } catch (error) {
    console.error(error);
  }
}

// Run the test
example().catch(console.error);
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **playgroundSimulationRequest** | PlaygroundSimulationRequest |  | |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshTenant** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

**PlaygroundSimulationResponse**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)
