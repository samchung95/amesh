# ScimApi

All URIs are relative to *http://localhost*

| Method | HTTP request | Description |
|------------- | ------------- | -------------|
| [**createScimGroupScimV2GroupsPost**](ScimApi.md#createscimgroupscimv2groupspost) | **POST** /scim/v2/Groups | Create Scim Group |
| [**createScimUserScimV2UsersPost**](ScimApi.md#createscimuserscimv2userspost) | **POST** /scim/v2/Users | Create Scim User |
| [**deleteScimGroupScimV2GroupsGroupIdDelete**](ScimApi.md#deletescimgroupscimv2groupsgroupiddelete) | **DELETE** /scim/v2/Groups/{group_id} | Delete Scim Group |
| [**deleteScimUserScimV2UsersUserIdDelete**](ScimApi.md#deletescimuserscimv2usersuseriddelete) | **DELETE** /scim/v2/Users/{user_id} | Delete Scim User |
| [**getScimGroupScimV2GroupsGroupIdGet**](ScimApi.md#getscimgroupscimv2groupsgroupidget) | **GET** /scim/v2/Groups/{group_id} | Get Scim Group |
| [**getScimUserScimV2UsersUserIdGet**](ScimApi.md#getscimuserscimv2usersuseridget) | **GET** /scim/v2/Users/{user_id} | Get Scim User |
| [**listScimGroupsScimV2GroupsGet**](ScimApi.md#listscimgroupsscimv2groupsget) | **GET** /scim/v2/Groups | List Scim Groups |
| [**listScimUsersScimV2UsersGet**](ScimApi.md#listscimusersscimv2usersget) | **GET** /scim/v2/Users | List Scim Users |
| [**patchScimGroupScimV2GroupsGroupIdPatch**](ScimApi.md#patchscimgroupscimv2groupsgroupidpatch) | **PATCH** /scim/v2/Groups/{group_id} | Patch Scim Group |
| [**patchScimUserScimV2UsersUserIdPatch**](ScimApi.md#patchscimuserscimv2usersuseridpatch) | **PATCH** /scim/v2/Users/{user_id} | Patch Scim User |
| [**scimServiceProviderConfigScimV2ServiceProviderConfigGet**](ScimApi.md#scimserviceproviderconfigscimv2serviceproviderconfigget) | **GET** /scim/v2/ServiceProviderConfig | Scim Service Provider Config |



## createScimGroupScimV2GroupsPost

> ScimGroupResource createScimGroupScimV2GroupsPost(scimGroupRequest, authorization)

Create Scim Group

### Example

```ts
import {
  Configuration,
  ScimApi,
} from '@amesh/client';
import type { CreateScimGroupScimV2GroupsPostRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new ScimApi();

  const body = {
    // ScimGroupRequest
    scimGroupRequest: ...,
    // string (optional)
    authorization: authorization_example,
  } satisfies CreateScimGroupScimV2GroupsPostRequest;

  try {
    const data = await api.createScimGroupScimV2GroupsPost(body);
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
| **scimGroupRequest** | [ScimGroupRequest](ScimGroupRequest.md) |  | |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**ScimGroupResource**](ScimGroupResource.md)

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


## createScimUserScimV2UsersPost

> ScimUserResource createScimUserScimV2UsersPost(scimUserRequest, authorization)

Create Scim User

### Example

```ts
import {
  Configuration,
  ScimApi,
} from '@amesh/client';
import type { CreateScimUserScimV2UsersPostRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new ScimApi();

  const body = {
    // ScimUserRequest
    scimUserRequest: ...,
    // string (optional)
    authorization: authorization_example,
  } satisfies CreateScimUserScimV2UsersPostRequest;

  try {
    const data = await api.createScimUserScimV2UsersPost(body);
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
| **scimUserRequest** | [ScimUserRequest](ScimUserRequest.md) |  | |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**ScimUserResource**](ScimUserResource.md)

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


## deleteScimGroupScimV2GroupsGroupIdDelete

> deleteScimGroupScimV2GroupsGroupIdDelete(groupId, authorization)

Delete Scim Group

### Example

```ts
import {
  Configuration,
  ScimApi,
} from '@amesh/client';
import type { DeleteScimGroupScimV2GroupsGroupIdDeleteRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new ScimApi();

  const body = {
    // string
    groupId: 38400000-8cf0-11bd-b23e-10b96e4ef00d,
    // string (optional)
    authorization: authorization_example,
  } satisfies DeleteScimGroupScimV2GroupsGroupIdDeleteRequest;

  try {
    const data = await api.deleteScimGroupScimV2GroupsGroupIdDelete(body);
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
| **groupId** | `string` |  | [Defaults to `undefined`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

`void` (Empty response body)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **204** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## deleteScimUserScimV2UsersUserIdDelete

> deleteScimUserScimV2UsersUserIdDelete(userId, authorization)

Delete Scim User

### Example

```ts
import {
  Configuration,
  ScimApi,
} from '@amesh/client';
import type { DeleteScimUserScimV2UsersUserIdDeleteRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new ScimApi();

  const body = {
    // string
    userId: 38400000-8cf0-11bd-b23e-10b96e4ef00d,
    // string (optional)
    authorization: authorization_example,
  } satisfies DeleteScimUserScimV2UsersUserIdDeleteRequest;

  try {
    const data = await api.deleteScimUserScimV2UsersUserIdDelete(body);
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
| **userId** | `string` |  | [Defaults to `undefined`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

`void` (Empty response body)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: `application/json`


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
| **204** | Successful Response |  -  |
| **422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#api-endpoints) [[Back to Model list]](../README.md#models) [[Back to README]](../README.md)


## getScimGroupScimV2GroupsGroupIdGet

> ScimGroupResource getScimGroupScimV2GroupsGroupIdGet(groupId, authorization)

Get Scim Group

### Example

```ts
import {
  Configuration,
  ScimApi,
} from '@amesh/client';
import type { GetScimGroupScimV2GroupsGroupIdGetRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new ScimApi();

  const body = {
    // string
    groupId: 38400000-8cf0-11bd-b23e-10b96e4ef00d,
    // string (optional)
    authorization: authorization_example,
  } satisfies GetScimGroupScimV2GroupsGroupIdGetRequest;

  try {
    const data = await api.getScimGroupScimV2GroupsGroupIdGet(body);
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
| **groupId** | `string` |  | [Defaults to `undefined`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**ScimGroupResource**](ScimGroupResource.md)

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


## getScimUserScimV2UsersUserIdGet

> ScimUserResource getScimUserScimV2UsersUserIdGet(userId, authorization)

Get Scim User

### Example

```ts
import {
  Configuration,
  ScimApi,
} from '@amesh/client';
import type { GetScimUserScimV2UsersUserIdGetRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new ScimApi();

  const body = {
    // string
    userId: 38400000-8cf0-11bd-b23e-10b96e4ef00d,
    // string (optional)
    authorization: authorization_example,
  } satisfies GetScimUserScimV2UsersUserIdGetRequest;

  try {
    const data = await api.getScimUserScimV2UsersUserIdGet(body);
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
| **userId** | `string` |  | [Defaults to `undefined`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**ScimUserResource**](ScimUserResource.md)

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


## listScimGroupsScimV2GroupsGet

> ScimListResponse listScimGroupsScimV2GroupsGet(filter, startIndex, count, authorization)

List Scim Groups

### Example

```ts
import {
  Configuration,
  ScimApi,
} from '@amesh/client';
import type { ListScimGroupsScimV2GroupsGetRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new ScimApi();

  const body = {
    // string (optional)
    filter: filter_example,
    // number (optional)
    startIndex: 56,
    // number (optional)
    count: 56,
    // string (optional)
    authorization: authorization_example,
  } satisfies ListScimGroupsScimV2GroupsGetRequest;

  try {
    const data = await api.listScimGroupsScimV2GroupsGet(body);
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
| **filter** | `string` |  | [Optional] [Defaults to `undefined`] |
| **startIndex** | `number` |  | [Optional] [Defaults to `1`] |
| **count** | `number` |  | [Optional] [Defaults to `100`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**ScimListResponse**](ScimListResponse.md)

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


## listScimUsersScimV2UsersGet

> ScimListResponse listScimUsersScimV2UsersGet(filter, startIndex, count, authorization)

List Scim Users

### Example

```ts
import {
  Configuration,
  ScimApi,
} from '@amesh/client';
import type { ListScimUsersScimV2UsersGetRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new ScimApi();

  const body = {
    // string (optional)
    filter: filter_example,
    // number (optional)
    startIndex: 56,
    // number (optional)
    count: 56,
    // string (optional)
    authorization: authorization_example,
  } satisfies ListScimUsersScimV2UsersGetRequest;

  try {
    const data = await api.listScimUsersScimV2UsersGet(body);
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
| **filter** | `string` |  | [Optional] [Defaults to `undefined`] |
| **startIndex** | `number` |  | [Optional] [Defaults to `1`] |
| **count** | `number` |  | [Optional] [Defaults to `100`] |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**ScimListResponse**](ScimListResponse.md)

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


## patchScimGroupScimV2GroupsGroupIdPatch

> ScimGroupResource patchScimGroupScimV2GroupsGroupIdPatch(groupId, scimPatchRequest, authorization)

Patch Scim Group

### Example

```ts
import {
  Configuration,
  ScimApi,
} from '@amesh/client';
import type { PatchScimGroupScimV2GroupsGroupIdPatchRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new ScimApi();

  const body = {
    // string
    groupId: 38400000-8cf0-11bd-b23e-10b96e4ef00d,
    // ScimPatchRequest
    scimPatchRequest: ...,
    // string (optional)
    authorization: authorization_example,
  } satisfies PatchScimGroupScimV2GroupsGroupIdPatchRequest;

  try {
    const data = await api.patchScimGroupScimV2GroupsGroupIdPatch(body);
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
| **groupId** | `string` |  | [Defaults to `undefined`] |
| **scimPatchRequest** | [ScimPatchRequest](ScimPatchRequest.md) |  | |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**ScimGroupResource**](ScimGroupResource.md)

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


## patchScimUserScimV2UsersUserIdPatch

> ScimUserResource patchScimUserScimV2UsersUserIdPatch(userId, scimPatchRequest, authorization)

Patch Scim User

### Example

```ts
import {
  Configuration,
  ScimApi,
} from '@amesh/client';
import type { PatchScimUserScimV2UsersUserIdPatchRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new ScimApi();

  const body = {
    // string
    userId: 38400000-8cf0-11bd-b23e-10b96e4ef00d,
    // ScimPatchRequest
    scimPatchRequest: ...,
    // string (optional)
    authorization: authorization_example,
  } satisfies PatchScimUserScimV2UsersUserIdPatchRequest;

  try {
    const data = await api.patchScimUserScimV2UsersUserIdPatch(body);
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
| **userId** | `string` |  | [Defaults to `undefined`] |
| **scimPatchRequest** | [ScimPatchRequest](ScimPatchRequest.md) |  | |
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

[**ScimUserResource**](ScimUserResource.md)

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


## scimServiceProviderConfigScimV2ServiceProviderConfigGet

> { [key: string]: any | null; } scimServiceProviderConfigScimV2ServiceProviderConfigGet(authorization)

Scim Service Provider Config

### Example

```ts
import {
  Configuration,
  ScimApi,
} from '@amesh/client';
import type { ScimServiceProviderConfigScimV2ServiceProviderConfigGetRequest } from '@amesh/client';

async function example() {
  console.log("🚀 Testing @amesh/client SDK...");
  const api = new ScimApi();

  const body = {
    // string (optional)
    authorization: authorization_example,
  } satisfies ScimServiceProviderConfigScimV2ServiceProviderConfigGetRequest;

  try {
    const data = await api.scimServiceProviderConfigScimV2ServiceProviderConfigGet(body);
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
| **authorization** | `string` |  | [Optional] [Defaults to `undefined`] |

### Return type

**{ [key: string]: any | null; }**

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
