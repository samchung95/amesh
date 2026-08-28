# SimulationsApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**compareFlowSimulationsApiV1FlowsNamespaceFlowIdSimulationsComparePost**](SimulationsApi.md#compareFlowSimulationsApiV1FlowsNamespaceFlowIdSimulationsComparePost) | **POST** /api/v1/flows/{namespace}/{flow_id}/simulations/compare | Compare Flow Simulations |
| [**compareFlowSimulationsApiV1FlowsNamespaceFlowIdSimulationsComparePostWithHttpInfo**](SimulationsApi.md#compareFlowSimulationsApiV1FlowsNamespaceFlowIdSimulationsComparePostWithHttpInfo) | **POST** /api/v1/flows/{namespace}/{flow_id}/simulations/compare | Compare Flow Simulations |
| [**simulateFlowRevisionApiV1FlowsNamespaceFlowIdRevisionsRevisionSimulatePost**](SimulationsApi.md#simulateFlowRevisionApiV1FlowsNamespaceFlowIdRevisionsRevisionSimulatePost) | **POST** /api/v1/flows/{namespace}/{flow_id}/revisions/{revision}/simulate | Simulate Flow Revision |
| [**simulateFlowRevisionApiV1FlowsNamespaceFlowIdRevisionsRevisionSimulatePostWithHttpInfo**](SimulationsApi.md#simulateFlowRevisionApiV1FlowsNamespaceFlowIdRevisionsRevisionSimulatePostWithHttpInfo) | **POST** /api/v1/flows/{namespace}/{flow_id}/revisions/{revision}/simulate | Simulate Flow Revision |



## compareFlowSimulationsApiV1FlowsNamespaceFlowIdSimulationsComparePost

> SimulationComparison compareFlowSimulationsApiV1FlowsNamespaceFlowIdSimulationsComparePost(namespace, flowId, from, to, simulationRequest, authorization, xAmeshCSRF, xAmeshTenant)

Compare Flow Simulations

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.SimulationsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        SimulationsApi apiInstance = new SimulationsApi(defaultClient);
        String namespace = "namespace_example"; // String |
        String flowId = "flowId_example"; // String |
        Integer from = 56; // Integer |
        Integer to = 56; // Integer |
        SimulationRequest simulationRequest = new SimulationRequest(); // SimulationRequest |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            SimulationComparison result = apiInstance.compareFlowSimulationsApiV1FlowsNamespaceFlowIdSimulationsComparePost(namespace, flowId, from, to, simulationRequest, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling SimulationsApi#compareFlowSimulationsApiV1FlowsNamespaceFlowIdSimulationsComparePost");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Reason: " + e.getResponseBody());
            System.err.println("Response headers: " + e.getResponseHeaders());
            e.printStackTrace();
        }
    }
}
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **namespace** | **String**|  | |
| **flowId** | **String**|  | |
| **from** | **Integer**|  | |
| **to** | **Integer**|  | |
| **simulationRequest** | **SimulationRequest**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

**SimulationComparison**


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

## compareFlowSimulationsApiV1FlowsNamespaceFlowIdSimulationsComparePostWithHttpInfo

> ApiResponse<SimulationComparison> compareFlowSimulationsApiV1FlowsNamespaceFlowIdSimulationsComparePostWithHttpInfo(namespace, flowId, from, to, simulationRequest, authorization, xAmeshCSRF, xAmeshTenant)

Compare Flow Simulations

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.SimulationsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        SimulationsApi apiInstance = new SimulationsApi(defaultClient);
        String namespace = "namespace_example"; // String |
        String flowId = "flowId_example"; // String |
        Integer from = 56; // Integer |
        Integer to = 56; // Integer |
        SimulationRequest simulationRequest = new SimulationRequest(); // SimulationRequest |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<SimulationComparison> response = apiInstance.compareFlowSimulationsApiV1FlowsNamespaceFlowIdSimulationsComparePostWithHttpInfo(namespace, flowId, from, to, simulationRequest, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling SimulationsApi#compareFlowSimulationsApiV1FlowsNamespaceFlowIdSimulationsComparePost");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Response headers: " + e.getResponseHeaders());
            System.err.println("Reason: " + e.getResponseBody());
            e.printStackTrace();
        }
    }
}
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **namespace** | **String**|  | |
| **flowId** | **String**|  | |
| **from** | **Integer**|  | |
| **to** | **Integer**|  | |
| **simulationRequest** | **SimulationRequest**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<**SimulationComparison**>


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |


## simulateFlowRevisionApiV1FlowsNamespaceFlowIdRevisionsRevisionSimulatePost

> SimulationPlan simulateFlowRevisionApiV1FlowsNamespaceFlowIdRevisionsRevisionSimulatePost(namespace, flowId, revision, simulationRequest, authorization, xAmeshCSRF, xAmeshTenant)

Simulate Flow Revision

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.SimulationsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        SimulationsApi apiInstance = new SimulationsApi(defaultClient);
        String namespace = "namespace_example"; // String |
        String flowId = "flowId_example"; // String |
        Integer revision = 56; // Integer |
        SimulationRequest simulationRequest = new SimulationRequest(); // SimulationRequest |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            SimulationPlan result = apiInstance.simulateFlowRevisionApiV1FlowsNamespaceFlowIdRevisionsRevisionSimulatePost(namespace, flowId, revision, simulationRequest, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling SimulationsApi#simulateFlowRevisionApiV1FlowsNamespaceFlowIdRevisionsRevisionSimulatePost");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Reason: " + e.getResponseBody());
            System.err.println("Response headers: " + e.getResponseHeaders());
            e.printStackTrace();
        }
    }
}
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **namespace** | **String**|  | |
| **flowId** | **String**|  | |
| **revision** | **Integer**|  | |
| **simulationRequest** | **SimulationRequest**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

**SimulationPlan**


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

## simulateFlowRevisionApiV1FlowsNamespaceFlowIdRevisionsRevisionSimulatePostWithHttpInfo

> ApiResponse<SimulationPlan> simulateFlowRevisionApiV1FlowsNamespaceFlowIdRevisionsRevisionSimulatePostWithHttpInfo(namespace, flowId, revision, simulationRequest, authorization, xAmeshCSRF, xAmeshTenant)

Simulate Flow Revision

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.SimulationsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        SimulationsApi apiInstance = new SimulationsApi(defaultClient);
        String namespace = "namespace_example"; // String |
        String flowId = "flowId_example"; // String |
        Integer revision = 56; // Integer |
        SimulationRequest simulationRequest = new SimulationRequest(); // SimulationRequest |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<SimulationPlan> response = apiInstance.simulateFlowRevisionApiV1FlowsNamespaceFlowIdRevisionsRevisionSimulatePostWithHttpInfo(namespace, flowId, revision, simulationRequest, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling SimulationsApi#simulateFlowRevisionApiV1FlowsNamespaceFlowIdRevisionsRevisionSimulatePost");
            System.err.println("Status code: " + e.getCode());
            System.err.println("Response headers: " + e.getResponseHeaders());
            System.err.println("Reason: " + e.getResponseBody());
            e.printStackTrace();
        }
    }
}
```

### Parameters


| Name | Type | Description  | Notes |
|------------- | ------------- | ------------- | -------------|
| **namespace** | **String**|  | |
| **flowId** | **String**|  | |
| **revision** | **Integer**|  | |
| **simulationRequest** | **SimulationRequest**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<**SimulationPlan**>


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |
