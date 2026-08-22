# OperationsApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**drainServiceInstanceApiV1OperationsServicesInstanceIdDrainPost**](OperationsApi.md#drainServiceInstanceApiV1OperationsServicesInstanceIdDrainPost) | **POST** /api/v1/operations/services/{instance_id}/drain | Drain Service Instance |
| [**drainServiceInstanceApiV1OperationsServicesInstanceIdDrainPostWithHttpInfo**](OperationsApi.md#drainServiceInstanceApiV1OperationsServicesInstanceIdDrainPostWithHttpInfo) | **POST** /api/v1/operations/services/{instance_id}/drain | Drain Service Instance |
| [**getAdmissionDiagnosticsApiV1AdmissionsDiagnosticsGet**](OperationsApi.md#getAdmissionDiagnosticsApiV1AdmissionsDiagnosticsGet) | **GET** /api/v1/admissions/diagnostics | Get Admission Diagnostics |
| [**getAdmissionDiagnosticsApiV1AdmissionsDiagnosticsGetWithHttpInfo**](OperationsApi.md#getAdmissionDiagnosticsApiV1AdmissionsDiagnosticsGetWithHttpInfo) | **GET** /api/v1/admissions/diagnostics | Get Admission Diagnostics |
| [**getReconciliationApiV1ReconciliationsRunIdGet**](OperationsApi.md#getReconciliationApiV1ReconciliationsRunIdGet) | **GET** /api/v1/reconciliations/{run_id} | Get Reconciliation |
| [**getReconciliationApiV1ReconciliationsRunIdGetWithHttpInfo**](OperationsApi.md#getReconciliationApiV1ReconciliationsRunIdGetWithHttpInfo) | **GET** /api/v1/reconciliations/{run_id} | Get Reconciliation |
| [**getServiceTopologyApiV1OperationsTopologyGet**](OperationsApi.md#getServiceTopologyApiV1OperationsTopologyGet) | **GET** /api/v1/operations/topology | Get Service Topology |
| [**getServiceTopologyApiV1OperationsTopologyGetWithHttpInfo**](OperationsApi.md#getServiceTopologyApiV1OperationsTopologyGetWithHttpInfo) | **GET** /api/v1/operations/topology | Get Service Topology |
| [**listReconciliationsApiV1ReconciliationsGet**](OperationsApi.md#listReconciliationsApiV1ReconciliationsGet) | **GET** /api/v1/reconciliations | List Reconciliations |
| [**listReconciliationsApiV1ReconciliationsGetWithHttpInfo**](OperationsApi.md#listReconciliationsApiV1ReconciliationsGetWithHttpInfo) | **GET** /api/v1/reconciliations | List Reconciliations |
| [**reconcileAdmissionsApiV1AdmissionsReconcilePost**](OperationsApi.md#reconcileAdmissionsApiV1AdmissionsReconcilePost) | **POST** /api/v1/admissions/reconcile | Reconcile Admissions |
| [**reconcileAdmissionsApiV1AdmissionsReconcilePostWithHttpInfo**](OperationsApi.md#reconcileAdmissionsApiV1AdmissionsReconcilePostWithHttpInfo) | **POST** /api/v1/admissions/reconcile | Reconcile Admissions |
| [**runReconciliationApiV1ReconciliationsPost**](OperationsApi.md#runReconciliationApiV1ReconciliationsPost) | **POST** /api/v1/reconciliations | Run Reconciliation |
| [**runReconciliationApiV1ReconciliationsPostWithHttpInfo**](OperationsApi.md#runReconciliationApiV1ReconciliationsPostWithHttpInfo) | **POST** /api/v1/reconciliations | Run Reconciliation |



## drainServiceInstanceApiV1OperationsServicesInstanceIdDrainPost

> ServiceInstance drainServiceInstanceApiV1OperationsServicesInstanceIdDrainPost(instanceId, serviceDrainRequest, authorization, xAmeshCSRF)

Drain Service Instance

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.OperationsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        OperationsApi apiInstance = new OperationsApi(defaultClient);
        UUID instanceId = UUID.randomUUID(); // UUID |
        ServiceDrainRequest serviceDrainRequest = new ServiceDrainRequest(); // ServiceDrainRequest |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        try {
            ServiceInstance result = apiInstance.drainServiceInstanceApiV1OperationsServicesInstanceIdDrainPost(instanceId, serviceDrainRequest, authorization, xAmeshCSRF);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling OperationsApi#drainServiceInstanceApiV1OperationsServicesInstanceIdDrainPost");
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
| **instanceId** | **UUID**|  | |
| **serviceDrainRequest** | [**ServiceDrainRequest**](ServiceDrainRequest.md)|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |

### Return type

[**ServiceInstance**](ServiceInstance.md)


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

## drainServiceInstanceApiV1OperationsServicesInstanceIdDrainPostWithHttpInfo

> ApiResponse<ServiceInstance> drainServiceInstanceApiV1OperationsServicesInstanceIdDrainPostWithHttpInfo(instanceId, serviceDrainRequest, authorization, xAmeshCSRF)

Drain Service Instance

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.OperationsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        OperationsApi apiInstance = new OperationsApi(defaultClient);
        UUID instanceId = UUID.randomUUID(); // UUID |
        ServiceDrainRequest serviceDrainRequest = new ServiceDrainRequest(); // ServiceDrainRequest |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        try {
            ApiResponse<ServiceInstance> response = apiInstance.drainServiceInstanceApiV1OperationsServicesInstanceIdDrainPostWithHttpInfo(instanceId, serviceDrainRequest, authorization, xAmeshCSRF);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling OperationsApi#drainServiceInstanceApiV1OperationsServicesInstanceIdDrainPost");
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
| **instanceId** | **UUID**|  | |
| **serviceDrainRequest** | [**ServiceDrainRequest**](ServiceDrainRequest.md)|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |

### Return type

ApiResponse<[**ServiceInstance**](ServiceInstance.md)>


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


## getAdmissionDiagnosticsApiV1AdmissionsDiagnosticsGet

> AdmissionDiagnostics getAdmissionDiagnosticsApiV1AdmissionsDiagnosticsGet(authorization, xAmeshCSRF, xAmeshTenant)

Get Admission Diagnostics

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.OperationsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        OperationsApi apiInstance = new OperationsApi(defaultClient);
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            AdmissionDiagnostics result = apiInstance.getAdmissionDiagnosticsApiV1AdmissionsDiagnosticsGet(authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling OperationsApi#getAdmissionDiagnosticsApiV1AdmissionsDiagnosticsGet");
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
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

[**AdmissionDiagnostics**](AdmissionDiagnostics.md)


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

## getAdmissionDiagnosticsApiV1AdmissionsDiagnosticsGetWithHttpInfo

> ApiResponse<AdmissionDiagnostics> getAdmissionDiagnosticsApiV1AdmissionsDiagnosticsGetWithHttpInfo(authorization, xAmeshCSRF, xAmeshTenant)

Get Admission Diagnostics

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.OperationsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        OperationsApi apiInstance = new OperationsApi(defaultClient);
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<AdmissionDiagnostics> response = apiInstance.getAdmissionDiagnosticsApiV1AdmissionsDiagnosticsGetWithHttpInfo(authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling OperationsApi#getAdmissionDiagnosticsApiV1AdmissionsDiagnosticsGet");
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
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<[**AdmissionDiagnostics**](AdmissionDiagnostics.md)>


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |


## getReconciliationApiV1ReconciliationsRunIdGet

> ReconciliationRun getReconciliationApiV1ReconciliationsRunIdGet(runId, authorization, xAmeshCSRF, xAmeshTenant)

Get Reconciliation

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.OperationsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        OperationsApi apiInstance = new OperationsApi(defaultClient);
        UUID runId = UUID.randomUUID(); // UUID |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ReconciliationRun result = apiInstance.getReconciliationApiV1ReconciliationsRunIdGet(runId, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling OperationsApi#getReconciliationApiV1ReconciliationsRunIdGet");
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
| **runId** | **UUID**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

[**ReconciliationRun**](ReconciliationRun.md)


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

## getReconciliationApiV1ReconciliationsRunIdGetWithHttpInfo

> ApiResponse<ReconciliationRun> getReconciliationApiV1ReconciliationsRunIdGetWithHttpInfo(runId, authorization, xAmeshCSRF, xAmeshTenant)

Get Reconciliation

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.OperationsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        OperationsApi apiInstance = new OperationsApi(defaultClient);
        UUID runId = UUID.randomUUID(); // UUID |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<ReconciliationRun> response = apiInstance.getReconciliationApiV1ReconciliationsRunIdGetWithHttpInfo(runId, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling OperationsApi#getReconciliationApiV1ReconciliationsRunIdGet");
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
| **runId** | **UUID**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<[**ReconciliationRun**](ReconciliationRun.md)>


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |


## getServiceTopologyApiV1OperationsTopologyGet

> ServiceTopology getServiceTopologyApiV1OperationsTopologyGet(authorization, xAmeshCSRF)

Get Service Topology

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.OperationsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        OperationsApi apiInstance = new OperationsApi(defaultClient);
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        try {
            ServiceTopology result = apiInstance.getServiceTopologyApiV1OperationsTopologyGet(authorization, xAmeshCSRF);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling OperationsApi#getServiceTopologyApiV1OperationsTopologyGet");
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
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |

### Return type

[**ServiceTopology**](ServiceTopology.md)


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

## getServiceTopologyApiV1OperationsTopologyGetWithHttpInfo

> ApiResponse<ServiceTopology> getServiceTopologyApiV1OperationsTopologyGetWithHttpInfo(authorization, xAmeshCSRF)

Get Service Topology

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.OperationsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        OperationsApi apiInstance = new OperationsApi(defaultClient);
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        try {
            ApiResponse<ServiceTopology> response = apiInstance.getServiceTopologyApiV1OperationsTopologyGetWithHttpInfo(authorization, xAmeshCSRF);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling OperationsApi#getServiceTopologyApiV1OperationsTopologyGet");
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
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |

### Return type

ApiResponse<[**ServiceTopology**](ServiceTopology.md)>


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |


## listReconciliationsApiV1ReconciliationsGet

> List<ReconciliationRun> listReconciliationsApiV1ReconciliationsGet(limit, authorization, xAmeshCSRF, xAmeshTenant)

List Reconciliations

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.OperationsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        OperationsApi apiInstance = new OperationsApi(defaultClient);
        Integer limit = 50; // Integer |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            List<ReconciliationRun> result = apiInstance.listReconciliationsApiV1ReconciliationsGet(limit, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling OperationsApi#listReconciliationsApiV1ReconciliationsGet");
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
| **limit** | **Integer**|  | [optional] [default to 50] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

[**List&lt;ReconciliationRun&gt;**](ReconciliationRun.md)


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

## listReconciliationsApiV1ReconciliationsGetWithHttpInfo

> ApiResponse<List<ReconciliationRun>> listReconciliationsApiV1ReconciliationsGetWithHttpInfo(limit, authorization, xAmeshCSRF, xAmeshTenant)

List Reconciliations

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.OperationsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        OperationsApi apiInstance = new OperationsApi(defaultClient);
        Integer limit = 50; // Integer |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<List<ReconciliationRun>> response = apiInstance.listReconciliationsApiV1ReconciliationsGetWithHttpInfo(limit, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling OperationsApi#listReconciliationsApiV1ReconciliationsGet");
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
| **limit** | **Integer**|  | [optional] [default to 50] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<[**List&lt;ReconciliationRun&gt;**](ReconciliationRun.md)>


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |


## reconcileAdmissionsApiV1AdmissionsReconcilePost

> Map<String, Integer> reconcileAdmissionsApiV1AdmissionsReconcilePost(limit, authorization, xAmeshCSRF, xAmeshTenant)

Reconcile Admissions

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.OperationsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        OperationsApi apiInstance = new OperationsApi(defaultClient);
        Integer limit = 100; // Integer |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            Map<String, Integer> result = apiInstance.reconcileAdmissionsApiV1AdmissionsReconcilePost(limit, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling OperationsApi#reconcileAdmissionsApiV1AdmissionsReconcilePost");
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
| **limit** | **Integer**|  | [optional] [default to 100] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

**Map&lt;String, Integer&gt;**


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |

## reconcileAdmissionsApiV1AdmissionsReconcilePostWithHttpInfo

> ApiResponse<Map<String, Integer>> reconcileAdmissionsApiV1AdmissionsReconcilePostWithHttpInfo(limit, authorization, xAmeshCSRF, xAmeshTenant)

Reconcile Admissions

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.OperationsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        OperationsApi apiInstance = new OperationsApi(defaultClient);
        Integer limit = 100; // Integer |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<Map<String, Integer>> response = apiInstance.reconcileAdmissionsApiV1AdmissionsReconcilePostWithHttpInfo(limit, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling OperationsApi#reconcileAdmissionsApiV1AdmissionsReconcilePost");
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
| **limit** | **Integer**|  | [optional] [default to 100] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<**Map&lt;String, Integer&gt;**>


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **200** | Successful Response |  -  |
| **422** | Validation Error |  -  |


## runReconciliationApiV1ReconciliationsPost

> ReconciliationRun runReconciliationApiV1ReconciliationsPost(reconciliationRequest, authorization, xAmeshCSRF, xAmeshTenant)

Run Reconciliation

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.OperationsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        OperationsApi apiInstance = new OperationsApi(defaultClient);
        ReconciliationRequest reconciliationRequest = new ReconciliationRequest(); // ReconciliationRequest |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ReconciliationRun result = apiInstance.runReconciliationApiV1ReconciliationsPost(reconciliationRequest, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling OperationsApi#runReconciliationApiV1ReconciliationsPost");
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
| **reconciliationRequest** | [**ReconciliationRequest**](ReconciliationRequest.md)|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

[**ReconciliationRun**](ReconciliationRun.md)


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **201** | Successful Response |  -  |
| **422** | Validation Error |  -  |

## runReconciliationApiV1ReconciliationsPostWithHttpInfo

> ApiResponse<ReconciliationRun> runReconciliationApiV1ReconciliationsPostWithHttpInfo(reconciliationRequest, authorization, xAmeshCSRF, xAmeshTenant)

Run Reconciliation

### Example

```java
// Import classes:
import io.amesh.client.ApiClient;
import io.amesh.client.ApiException;
import io.amesh.client.ApiResponse;
import io.amesh.client.Configuration;
import io.amesh.client.models.*;
import io.amesh.client.api.OperationsApi;

public class Example {
    public static void main(String[] args) {
        ApiClient defaultClient = Configuration.getDefaultApiClient();
        defaultClient.setBasePath("http://localhost");

        OperationsApi apiInstance = new OperationsApi(defaultClient);
        ReconciliationRequest reconciliationRequest = new ReconciliationRequest(); // ReconciliationRequest |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<ReconciliationRun> response = apiInstance.runReconciliationApiV1ReconciliationsPostWithHttpInfo(reconciliationRequest, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling OperationsApi#runReconciliationApiV1ReconciliationsPost");
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
| **reconciliationRequest** | [**ReconciliationRequest**](ReconciliationRequest.md)|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<[**ReconciliationRun**](ReconciliationRun.md)>


### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: application/json
- **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **201** | Successful Response |  -  |
| **422** | Validation Error |  -  |
