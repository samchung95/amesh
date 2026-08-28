# CredentialsApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**exchangeWorkloadCredentialApiV1CredentialsExchangePost**](CredentialsApi.md#exchangeworkloadcredentialapiv1credentialsexchangepost) | **POST** /api/v1/credentials/exchange | Exchange Workload Credential |
| [**issueCredentialApiV1AdminPrincipalsPrincipalIdCredentialsPost**](CredentialsApi.md#issuecredentialapiv1adminprincipalsprincipalidcredentialspost) | **POST** /api/v1/admin/principals/{principal_id}/credentials | Issue Credential |
| [**listCredentialsApiV1AdminPrincipalsPrincipalIdCredentialsGet**](CredentialsApi.md#listcredentialsapiv1adminprincipalsprincipalidcredentialsget) | **GET** /api/v1/admin/principals/{principal_id}/credentials | List Credentials |
| [**revokeAllCredentialsApiV1AdminPrincipalsPrincipalIdCredentialsDelete**](CredentialsApi.md#revokeallcredentialsapiv1adminprincipalsprincipalidcredentialsdelete) | **DELETE** /api/v1/admin/principals/{principal_id}/credentials | Revoke All Credentials |
| [**revokeCredentialApiV1AdminCredentialsCredentialIdDelete**](CredentialsApi.md#revokecredentialapiv1admincredentialscredentialiddelete) | **DELETE** /api/v1/admin/credentials/{credential_id} | Revoke Credential |
| [**rotateCredentialApiV1AdminCredentialsCredentialIdRotatePost**](CredentialsApi.md#rotatecredentialapiv1admincredentialscredentialidrotatepost) | **POST** /api/v1/admin/credentials/{credential_id}/rotate | Rotate Credential |



## exchangeWorkloadCredentialApiV1CredentialsExchangePost

> IssuedCredentialResponse exchangeWorkloadCredentialApiV1CredentialsExchangePost(exchangeCredentialRequest, authorization, xAmeshCSRF)

Exchange Workload Credential

### Example

```ts
import {
  Configuration,
  CredentialsApi,
} from '@amesh/client';
import type { ExchangeWorkloadCredentialApiV1CredentialsExchangePostRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new CredentialsApi();

  const body = {
    // ExchangeCredentialRequest
    exchangeCredentialRequest: ...,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
  } satisfies ExchangeWorkloadCredentialApiV1CredentialsExchangePostRequest;

  try {
    const data = await api.exchangeWorkloadCredentialApiV1CredentialsExchangePost(body);
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
| **exchangeCredentialRequest** | ExchangeCredentialRequest |  | |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

**IssuedCredentialResponse**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **201** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## issueCredentialApiV1AdminPrincipalsPrincipalIdCredentialsPost

> IssuedCredentialResponse issueCredentialApiV1AdminPrincipalsPrincipalIdCredentialsPost(principalId, issueCredentialRequest, authorization, xAmeshCSRF)

Issue Credential

### Example

```ts
import {
  Configuration,
  CredentialsApi,
} from '@amesh/client';
import type { IssueCredentialApiV1AdminPrincipalsPrincipalIdCredentialsPostRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new CredentialsApi();

  const body = {
    // string
    principalId: 38400000-8cf0-11bd-b23e-10b96e4ef00d,
    // IssueCredentialRequest
    issueCredentialRequest: ...,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
  } satisfies IssueCredentialApiV1AdminPrincipalsPrincipalIdCredentialsPostRequest;

  try {
    const data = await api.issueCredentialApiV1AdminPrincipalsPrincipalIdCredentialsPost(body);
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
| **principalId** | `string` |  | [Defaults to `undefined`] |
| **issueCredentialRequest** | IssueCredentialRequest |  | |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

**IssuedCredentialResponse**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **201** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## listCredentialsApiV1AdminPrincipalsPrincipalIdCredentialsGet

> Array&lt;CredentialMetadata&gt; listCredentialsApiV1AdminPrincipalsPrincipalIdCredentialsGet(principalId, cursor, limit, filter, sort, fields, authorization, xAmeshCSRF)

List Credentials

### Example

```ts
import {
  Configuration,
  CredentialsApi,
} from '@amesh/client';
import type { ListCredentialsApiV1AdminPrincipalsPrincipalIdCredentialsGetRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new CredentialsApi();

  const body = {
    // string
    principalId: 38400000-8cf0-11bd-b23e-10b96e4ef00d,
    // string | Opaque cursor from the prior page (optional)
    cursor: cursor_example,
    // number (optional)
    limit: 56,
    // Array<string> | Repeatable top-level equality filter in field=value form (optional)
    filter: ...,
    // string | Comma-separated top-level fields; prefix descending fields with - (optional)
    sort: sort_example,
    // string | Comma-separated top-level response fields (optional)
    fields: fields_example,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
  } satisfies ListCredentialsApiV1AdminPrincipalsPrincipalIdCredentialsGetRequest;

  try {
    const data = await api.listCredentialsApiV1AdminPrincipalsPrincipalIdCredentialsGet(body);
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
| **principalId** | `string` |  | [Defaults to `undefined`] |
| **cursor** | `string` | Opaque cursor from the prior page | [Optional] [Defaults to `undefined`] |
| **limit** | `number` |  | [Optional] [Defaults to `undefined`] |
| **filter** | `Array<string>` | Repeatable top-level equality filter in field&#x3D;value form | [Optional] |
| **sort** | `string` | Comma-separated top-level fields; prefix descending fields with - | [Optional] [Defaults to `undefined`] |
| **fields** | `string` | Comma-separated top-level response fields | [Optional] [Defaults to `undefined`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

**Array&lt;CredentialMetadata&gt;**

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


## revokeAllCredentialsApiV1AdminPrincipalsPrincipalIdCredentialsDelete

> RevokedCredentialsResponse revokeAllCredentialsApiV1AdminPrincipalsPrincipalIdCredentialsDelete(principalId, authorization, xAmeshCSRF)

Revoke All Credentials

### Example

```ts
import {
  Configuration,
  CredentialsApi,
} from '@amesh/client';
import type { RevokeAllCredentialsApiV1AdminPrincipalsPrincipalIdCredentialsDeleteRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new CredentialsApi();

  const body = {
    // string
    principalId: 38400000-8cf0-11bd-b23e-10b96e4ef00d,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
  } satisfies RevokeAllCredentialsApiV1AdminPrincipalsPrincipalIdCredentialsDeleteRequest;

  try {
    const data = await api.revokeAllCredentialsApiV1AdminPrincipalsPrincipalIdCredentialsDelete(body);
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
| **principalId** | `string` |  | [Defaults to `undefined`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

**RevokedCredentialsResponse**

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


## revokeCredentialApiV1AdminCredentialsCredentialIdDelete

> RevokedCredentialsResponse revokeCredentialApiV1AdminCredentialsCredentialIdDelete(credentialId, authorization, xAmeshCSRF)

Revoke Credential

### Example

```ts
import {
  Configuration,
  CredentialsApi,
} from '@amesh/client';
import type { RevokeCredentialApiV1AdminCredentialsCredentialIdDeleteRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new CredentialsApi();

  const body = {
    // string
    credentialId: 38400000-8cf0-11bd-b23e-10b96e4ef00d,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
  } satisfies RevokeCredentialApiV1AdminCredentialsCredentialIdDeleteRequest;

  try {
    const data = await api.revokeCredentialApiV1AdminCredentialsCredentialIdDelete(body);
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
| **credentialId** | `string` |  | [Defaults to `undefined`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

**RevokedCredentialsResponse**

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


## rotateCredentialApiV1AdminCredentialsCredentialIdRotatePost

> IssuedCredentialResponse rotateCredentialApiV1AdminCredentialsCredentialIdRotatePost(credentialId, rotateCredentialRequest, authorization, xAmeshCSRF)

Rotate Credential

### Example

```ts
import {
  Configuration,
  CredentialsApi,
} from '@amesh/client';
import type { RotateCredentialApiV1AdminCredentialsCredentialIdRotatePostRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new CredentialsApi();

  const body = {
    // string
    credentialId: 38400000-8cf0-11bd-b23e-10b96e4ef00d,
    // RotateCredentialRequest
    rotateCredentialRequest: ...,
    // string (optional)
    authorization: authorization_example,
    // string (optional)
    xAmeshCSRF: xAmeshCSRF_example,
  } satisfies RotateCredentialApiV1AdminCredentialsCredentialIdRotatePostRequest;

  try {
    const data = await api.rotateCredentialApiV1AdminCredentialsCredentialIdRotatePost(body);
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
| **credentialId** | `string` |  | [Defaults to `undefined`] |
| **rotateCredentialRequest** | RotateCredentialRequest |  | |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |
| **xAmeshCSRF** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

**IssuedCredentialResponse**

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: `application/json`
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **201** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)
