# OperationsApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**activateOperationalControlApiV1OperationalControlsPost**](OperationsApi.md#activateOperationalControlApiV1OperationalControlsPost) | **POST** /api/v1/operational-controls | Activate Operational Control |
| [**activateOperationalControlApiV1OperationalControlsPostWithHttpInfo**](OperationsApi.md#activateOperationalControlApiV1OperationalControlsPostWithHttpInfo) | **POST** /api/v1/operational-controls | Activate Operational Control |
| [**changeOperationalControlApiV1OperationalControlsControlIdActionsPost**](OperationsApi.md#changeOperationalControlApiV1OperationalControlsControlIdActionsPost) | **POST** /api/v1/operational-controls/{control_id}/actions | Change Operational Control |
| [**changeOperationalControlApiV1OperationalControlsControlIdActionsPostWithHttpInfo**](OperationsApi.md#changeOperationalControlApiV1OperationalControlsControlIdActionsPostWithHttpInfo) | **POST** /api/v1/operational-controls/{control_id}/actions | Change Operational Control |
| [**deactivateAnnouncementApiV1AnnouncementsAnnouncementIdDelete**](OperationsApi.md#deactivateAnnouncementApiV1AnnouncementsAnnouncementIdDelete) | **DELETE** /api/v1/announcements/{announcement_id} | Deactivate Announcement |
| [**deactivateAnnouncementApiV1AnnouncementsAnnouncementIdDeleteWithHttpInfo**](OperationsApi.md#deactivateAnnouncementApiV1AnnouncementsAnnouncementIdDeleteWithHttpInfo) | **DELETE** /api/v1/announcements/{announcement_id} | Deactivate Announcement |
| [**drainServiceInstanceApiV1OperationsServicesInstanceIdDrainPost**](OperationsApi.md#drainServiceInstanceApiV1OperationsServicesInstanceIdDrainPost) | **POST** /api/v1/operations/services/{instance_id}/drain | Drain Service Instance |
| [**drainServiceInstanceApiV1OperationsServicesInstanceIdDrainPostWithHttpInfo**](OperationsApi.md#drainServiceInstanceApiV1OperationsServicesInstanceIdDrainPostWithHttpInfo) | **POST** /api/v1/operations/services/{instance_id}/drain | Drain Service Instance |
| [**getAdmissionDiagnosticsApiV1AdmissionsDiagnosticsGet**](OperationsApi.md#getAdmissionDiagnosticsApiV1AdmissionsDiagnosticsGet) | **GET** /api/v1/admissions/diagnostics | Get Admission Diagnostics |
| [**getAdmissionDiagnosticsApiV1AdmissionsDiagnosticsGetWithHttpInfo**](OperationsApi.md#getAdmissionDiagnosticsApiV1AdmissionsDiagnosticsGetWithHttpInfo) | **GET** /api/v1/admissions/diagnostics | Get Admission Diagnostics |
| [**getNetworkDiagnosticsApiV1OperationsNetworkDiagnosticsGet**](OperationsApi.md#getNetworkDiagnosticsApiV1OperationsNetworkDiagnosticsGet) | **GET** /api/v1/operations/network-diagnostics | Get Network Diagnostics |
| [**getNetworkDiagnosticsApiV1OperationsNetworkDiagnosticsGetWithHttpInfo**](OperationsApi.md#getNetworkDiagnosticsApiV1OperationsNetworkDiagnosticsGetWithHttpInfo) | **GET** /api/v1/operations/network-diagnostics | Get Network Diagnostics |
| [**getReconciliationApiV1ReconciliationsRunIdGet**](OperationsApi.md#getReconciliationApiV1ReconciliationsRunIdGet) | **GET** /api/v1/reconciliations/{run_id} | Get Reconciliation |
| [**getReconciliationApiV1ReconciliationsRunIdGetWithHttpInfo**](OperationsApi.md#getReconciliationApiV1ReconciliationsRunIdGetWithHttpInfo) | **GET** /api/v1/reconciliations/{run_id} | Get Reconciliation |
| [**getServiceTopologyApiV1OperationsTopologyGet**](OperationsApi.md#getServiceTopologyApiV1OperationsTopologyGet) | **GET** /api/v1/operations/topology | Get Service Topology |
| [**getServiceTopologyApiV1OperationsTopologyGetWithHttpInfo**](OperationsApi.md#getServiceTopologyApiV1OperationsTopologyGetWithHttpInfo) | **GET** /api/v1/operations/topology | Get Service Topology |
| [**listAnnouncementsApiV1AnnouncementsGet**](OperationsApi.md#listAnnouncementsApiV1AnnouncementsGet) | **GET** /api/v1/announcements | List Announcements |
| [**listAnnouncementsApiV1AnnouncementsGetWithHttpInfo**](OperationsApi.md#listAnnouncementsApiV1AnnouncementsGetWithHttpInfo) | **GET** /api/v1/announcements | List Announcements |
| [**listOperationalControlEventsApiV1OperationalControlEventsGet**](OperationsApi.md#listOperationalControlEventsApiV1OperationalControlEventsGet) | **GET** /api/v1/operational-control-events | List Operational Control Events |
| [**listOperationalControlEventsApiV1OperationalControlEventsGetWithHttpInfo**](OperationsApi.md#listOperationalControlEventsApiV1OperationalControlEventsGetWithHttpInfo) | **GET** /api/v1/operational-control-events | List Operational Control Events |
| [**listOperationalControlsApiV1OperationalControlsGet**](OperationsApi.md#listOperationalControlsApiV1OperationalControlsGet) | **GET** /api/v1/operational-controls | List Operational Controls |
| [**listOperationalControlsApiV1OperationalControlsGetWithHttpInfo**](OperationsApi.md#listOperationalControlsApiV1OperationalControlsGetWithHttpInfo) | **GET** /api/v1/operational-controls | List Operational Controls |
| [**listReconciliationsApiV1ReconciliationsGet**](OperationsApi.md#listReconciliationsApiV1ReconciliationsGet) | **GET** /api/v1/reconciliations | List Reconciliations |
| [**listReconciliationsApiV1ReconciliationsGetWithHttpInfo**](OperationsApi.md#listReconciliationsApiV1ReconciliationsGetWithHttpInfo) | **GET** /api/v1/reconciliations | List Reconciliations |
| [**publishAnnouncementApiV1AnnouncementsPost**](OperationsApi.md#publishAnnouncementApiV1AnnouncementsPost) | **POST** /api/v1/announcements | Publish Announcement |
| [**publishAnnouncementApiV1AnnouncementsPostWithHttpInfo**](OperationsApi.md#publishAnnouncementApiV1AnnouncementsPostWithHttpInfo) | **POST** /api/v1/announcements | Publish Announcement |
| [**reconcileAdmissionsApiV1AdmissionsReconcilePost**](OperationsApi.md#reconcileAdmissionsApiV1AdmissionsReconcilePost) | **POST** /api/v1/admissions/reconcile | Reconcile Admissions |
| [**reconcileAdmissionsApiV1AdmissionsReconcilePostWithHttpInfo**](OperationsApi.md#reconcileAdmissionsApiV1AdmissionsReconcilePostWithHttpInfo) | **POST** /api/v1/admissions/reconcile | Reconcile Admissions |
| [**runReconciliationApiV1ReconciliationsPost**](OperationsApi.md#runReconciliationApiV1ReconciliationsPost) | **POST** /api/v1/reconciliations | Run Reconciliation |
| [**runReconciliationApiV1ReconciliationsPostWithHttpInfo**](OperationsApi.md#runReconciliationApiV1ReconciliationsPostWithHttpInfo) | **POST** /api/v1/reconciliations | Run Reconciliation |



## activateOperationalControlApiV1OperationalControlsPost

> OperationalControl activateOperationalControlApiV1OperationalControlsPost(operationalControlCreateRequest, authorization, xAmeshCSRF, xAmeshTenant)

Activate Operational Control

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
        OperationalControlCreateRequest operationalControlCreateRequest = new OperationalControlCreateRequest(); // OperationalControlCreateRequest |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            OperationalControl result = apiInstance.activateOperationalControlApiV1OperationalControlsPost(operationalControlCreateRequest, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling OperationsApi#activateOperationalControlApiV1OperationalControlsPost");
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
| **operationalControlCreateRequest** | [**OperationalControlCreateRequest**](OperationalControlCreateRequest.md)|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

[**OperationalControl**](OperationalControl.md)


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

## activateOperationalControlApiV1OperationalControlsPostWithHttpInfo

> ApiResponse<OperationalControl> activateOperationalControlApiV1OperationalControlsPostWithHttpInfo(operationalControlCreateRequest, authorization, xAmeshCSRF, xAmeshTenant)

Activate Operational Control

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
        OperationalControlCreateRequest operationalControlCreateRequest = new OperationalControlCreateRequest(); // OperationalControlCreateRequest |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<OperationalControl> response = apiInstance.activateOperationalControlApiV1OperationalControlsPostWithHttpInfo(operationalControlCreateRequest, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling OperationsApi#activateOperationalControlApiV1OperationalControlsPost");
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
| **operationalControlCreateRequest** | [**OperationalControlCreateRequest**](OperationalControlCreateRequest.md)|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<[**OperationalControl**](OperationalControl.md)>


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


## changeOperationalControlApiV1OperationalControlsControlIdActionsPost

> OperationalControl changeOperationalControlApiV1OperationalControlsControlIdActionsPost(controlId, operationalControlActionRequest, authorization, xAmeshCSRF, xAmeshTenant)

Change Operational Control

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
        UUID controlId = UUID.randomUUID(); // UUID |
        OperationalControlActionRequest operationalControlActionRequest = new OperationalControlActionRequest(); // OperationalControlActionRequest |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            OperationalControl result = apiInstance.changeOperationalControlApiV1OperationalControlsControlIdActionsPost(controlId, operationalControlActionRequest, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling OperationsApi#changeOperationalControlApiV1OperationalControlsControlIdActionsPost");
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
| **controlId** | **UUID**|  | |
| **operationalControlActionRequest** | [**OperationalControlActionRequest**](OperationalControlActionRequest.md)|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

[**OperationalControl**](OperationalControl.md)


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

## changeOperationalControlApiV1OperationalControlsControlIdActionsPostWithHttpInfo

> ApiResponse<OperationalControl> changeOperationalControlApiV1OperationalControlsControlIdActionsPostWithHttpInfo(controlId, operationalControlActionRequest, authorization, xAmeshCSRF, xAmeshTenant)

Change Operational Control

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
        UUID controlId = UUID.randomUUID(); // UUID |
        OperationalControlActionRequest operationalControlActionRequest = new OperationalControlActionRequest(); // OperationalControlActionRequest |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<OperationalControl> response = apiInstance.changeOperationalControlApiV1OperationalControlsControlIdActionsPostWithHttpInfo(controlId, operationalControlActionRequest, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling OperationsApi#changeOperationalControlApiV1OperationalControlsControlIdActionsPost");
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
| **controlId** | **UUID**|  | |
| **operationalControlActionRequest** | [**OperationalControlActionRequest**](OperationalControlActionRequest.md)|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<[**OperationalControl**](OperationalControl.md)>


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


## deactivateAnnouncementApiV1AnnouncementsAnnouncementIdDelete

> Announcement deactivateAnnouncementApiV1AnnouncementsAnnouncementIdDelete(announcementId, expectedVersion, authorization, xAmeshCSRF, xAmeshTenant)

Deactivate Announcement

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
        UUID announcementId = UUID.randomUUID(); // UUID |
        Integer expectedVersion = 56; // Integer |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            Announcement result = apiInstance.deactivateAnnouncementApiV1AnnouncementsAnnouncementIdDelete(announcementId, expectedVersion, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling OperationsApi#deactivateAnnouncementApiV1AnnouncementsAnnouncementIdDelete");
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
| **announcementId** | **UUID**|  | |
| **expectedVersion** | **Integer**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

[**Announcement**](Announcement.md)


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

## deactivateAnnouncementApiV1AnnouncementsAnnouncementIdDeleteWithHttpInfo

> ApiResponse<Announcement> deactivateAnnouncementApiV1AnnouncementsAnnouncementIdDeleteWithHttpInfo(announcementId, expectedVersion, authorization, xAmeshCSRF, xAmeshTenant)

Deactivate Announcement

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
        UUID announcementId = UUID.randomUUID(); // UUID |
        Integer expectedVersion = 56; // Integer |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<Announcement> response = apiInstance.deactivateAnnouncementApiV1AnnouncementsAnnouncementIdDeleteWithHttpInfo(announcementId, expectedVersion, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling OperationsApi#deactivateAnnouncementApiV1AnnouncementsAnnouncementIdDelete");
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
| **announcementId** | **UUID**|  | |
| **expectedVersion** | **Integer**|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<[**Announcement**](Announcement.md)>


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


## getNetworkDiagnosticsApiV1OperationsNetworkDiagnosticsGet

> NetworkDiagnosticBundle getNetworkDiagnosticsApiV1OperationsNetworkDiagnosticsGet(authorization, xAmeshCSRF, xAmeshTenant)

Get Network Diagnostics

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
            NetworkDiagnosticBundle result = apiInstance.getNetworkDiagnosticsApiV1OperationsNetworkDiagnosticsGet(authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling OperationsApi#getNetworkDiagnosticsApiV1OperationsNetworkDiagnosticsGet");
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

[**NetworkDiagnosticBundle**](NetworkDiagnosticBundle.md)


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

## getNetworkDiagnosticsApiV1OperationsNetworkDiagnosticsGetWithHttpInfo

> ApiResponse<NetworkDiagnosticBundle> getNetworkDiagnosticsApiV1OperationsNetworkDiagnosticsGetWithHttpInfo(authorization, xAmeshCSRF, xAmeshTenant)

Get Network Diagnostics

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
            ApiResponse<NetworkDiagnosticBundle> response = apiInstance.getNetworkDiagnosticsApiV1OperationsNetworkDiagnosticsGetWithHttpInfo(authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling OperationsApi#getNetworkDiagnosticsApiV1OperationsNetworkDiagnosticsGet");
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

ApiResponse<[**NetworkDiagnosticBundle**](NetworkDiagnosticBundle.md)>


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


## listAnnouncementsApiV1AnnouncementsGet

> List<Announcement> listAnnouncementsApiV1AnnouncementsGet(namespace, includeInactive, authorization, xAmeshCSRF, xAmeshTenant)

List Announcements

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
        String namespace = "namespace_example"; // String |
        Boolean includeInactive = false; // Boolean |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            List<Announcement> result = apiInstance.listAnnouncementsApiV1AnnouncementsGet(namespace, includeInactive, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling OperationsApi#listAnnouncementsApiV1AnnouncementsGet");
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
| **namespace** | **String**|  | [optional] |
| **includeInactive** | **Boolean**|  | [optional] [default to false] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

[**List&lt;Announcement&gt;**](Announcement.md)


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

## listAnnouncementsApiV1AnnouncementsGetWithHttpInfo

> ApiResponse<List<Announcement>> listAnnouncementsApiV1AnnouncementsGetWithHttpInfo(namespace, includeInactive, authorization, xAmeshCSRF, xAmeshTenant)

List Announcements

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
        String namespace = "namespace_example"; // String |
        Boolean includeInactive = false; // Boolean |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<List<Announcement>> response = apiInstance.listAnnouncementsApiV1AnnouncementsGetWithHttpInfo(namespace, includeInactive, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling OperationsApi#listAnnouncementsApiV1AnnouncementsGet");
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
| **namespace** | **String**|  | [optional] |
| **includeInactive** | **Boolean**|  | [optional] [default to false] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<[**List&lt;Announcement&gt;**](Announcement.md)>


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


## listOperationalControlEventsApiV1OperationalControlEventsGet

> List<OperationalControlEvent> listOperationalControlEventsApiV1OperationalControlEventsGet(limit, authorization, xAmeshCSRF, xAmeshTenant)

List Operational Control Events

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
        Integer limit = 200; // Integer |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            List<OperationalControlEvent> result = apiInstance.listOperationalControlEventsApiV1OperationalControlEventsGet(limit, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling OperationsApi#listOperationalControlEventsApiV1OperationalControlEventsGet");
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
| **limit** | **Integer**|  | [optional] [default to 200] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

[**List&lt;OperationalControlEvent&gt;**](OperationalControlEvent.md)


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

## listOperationalControlEventsApiV1OperationalControlEventsGetWithHttpInfo

> ApiResponse<List<OperationalControlEvent>> listOperationalControlEventsApiV1OperationalControlEventsGetWithHttpInfo(limit, authorization, xAmeshCSRF, xAmeshTenant)

List Operational Control Events

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
        Integer limit = 200; // Integer |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<List<OperationalControlEvent>> response = apiInstance.listOperationalControlEventsApiV1OperationalControlEventsGetWithHttpInfo(limit, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling OperationsApi#listOperationalControlEventsApiV1OperationalControlEventsGet");
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
| **limit** | **Integer**|  | [optional] [default to 200] |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<[**List&lt;OperationalControlEvent&gt;**](OperationalControlEvent.md)>


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


## listOperationalControlsApiV1OperationalControlsGet

> List<OperationalControl> listOperationalControlsApiV1OperationalControlsGet(authorization, xAmeshCSRF, xAmeshTenant)

List Operational Controls

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
            List<OperationalControl> result = apiInstance.listOperationalControlsApiV1OperationalControlsGet(authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling OperationsApi#listOperationalControlsApiV1OperationalControlsGet");
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

[**List&lt;OperationalControl&gt;**](OperationalControl.md)


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

## listOperationalControlsApiV1OperationalControlsGetWithHttpInfo

> ApiResponse<List<OperationalControl>> listOperationalControlsApiV1OperationalControlsGetWithHttpInfo(authorization, xAmeshCSRF, xAmeshTenant)

List Operational Controls

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
            ApiResponse<List<OperationalControl>> response = apiInstance.listOperationalControlsApiV1OperationalControlsGetWithHttpInfo(authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling OperationsApi#listOperationalControlsApiV1OperationalControlsGet");
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

ApiResponse<[**List&lt;OperationalControl&gt;**](OperationalControl.md)>


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


## publishAnnouncementApiV1AnnouncementsPost

> Announcement publishAnnouncementApiV1AnnouncementsPost(announcementCreateRequest, authorization, xAmeshCSRF, xAmeshTenant)

Publish Announcement

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
        AnnouncementCreateRequest announcementCreateRequest = new AnnouncementCreateRequest(); // AnnouncementCreateRequest |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            Announcement result = apiInstance.publishAnnouncementApiV1AnnouncementsPost(announcementCreateRequest, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println(result);
        } catch (ApiException e) {
            System.err.println("Exception when calling OperationsApi#publishAnnouncementApiV1AnnouncementsPost");
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
| **announcementCreateRequest** | [**AnnouncementCreateRequest**](AnnouncementCreateRequest.md)|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

[**Announcement**](Announcement.md)


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

## publishAnnouncementApiV1AnnouncementsPostWithHttpInfo

> ApiResponse<Announcement> publishAnnouncementApiV1AnnouncementsPostWithHttpInfo(announcementCreateRequest, authorization, xAmeshCSRF, xAmeshTenant)

Publish Announcement

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
        AnnouncementCreateRequest announcementCreateRequest = new AnnouncementCreateRequest(); // AnnouncementCreateRequest |
        String authorization = "authorization_example"; // String |
        String xAmeshCSRF = "xAmeshCSRF_example"; // String |
        String xAmeshTenant = "xAmeshTenant_example"; // String |
        try {
            ApiResponse<Announcement> response = apiInstance.publishAnnouncementApiV1AnnouncementsPostWithHttpInfo(announcementCreateRequest, authorization, xAmeshCSRF, xAmeshTenant);
            System.out.println("Status code: " + response.getStatusCode());
            System.out.println("Response headers: " + response.getHeaders());
            System.out.println("Response body: " + response.getData());
        } catch (ApiException e) {
            System.err.println("Exception when calling OperationsApi#publishAnnouncementApiV1AnnouncementsPost");
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
| **announcementCreateRequest** | [**AnnouncementCreateRequest**](AnnouncementCreateRequest.md)|  | |
| **authorization** | **String**|  | [optional] |
| **xAmeshCSRF** | **String**|  | [optional] |
| **xAmeshTenant** | **String**|  | [optional] |

### Return type

ApiResponse<[**Announcement**](Announcement.md)>


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
