import type { components, paths } from './generated/openapi'

type HttpMethod = 'get' | 'put' | 'post' | 'delete' | 'patch'
type SuccessStatus = 200 | 201 | 202 | 203 | 204 | 205 | 206 | 207 | 208 | 226
const operationBrand: unique symbol = Symbol('ApiOperation')

export type OpenApiPath = keyof paths

export type OpenApiMethod<Path extends OpenApiPath> = {
  [Method in HttpMethod]: Exclude<paths[Path][Method], undefined> extends never
    ? never
    : Method
}[HttpMethod]

export interface ApiOperation<
  Path extends OpenApiPath,
  Method extends OpenApiMethod<Path>,
> {
  readonly template: Path
  readonly method: Method
  readonly url: string
  readonly [operationBrand]: (path: Path, method: Method) => readonly [Path, Method]
}

type OperationFor<
  Path extends OpenApiPath,
  Method extends OpenApiMethod<Path>,
> = Exclude<paths[Path][Method], undefined>

type RequestBodyFor<Operation> = Operation extends { requestBody?: infer Body }
  ? Exclude<Body, undefined>
  : never

type JsonBodyFor<Operation> = RequestBodyFor<Operation> extends {
  content: infer Content
}
  ? Content extends { 'application/json': infer Body }
    ? Body
    : never
  : never

type ResponsesFor<Operation> = Operation extends { responses: infer Responses }
  ? Responses
  : never

type SuccessfulResponseFor<Operation> = ResponsesFor<Operation> extends infer Responses
  ? Responses extends object
    ? Responses[Extract<keyof Responses, SuccessStatus>]
    : never
  : never

type JsonContentFor<Response> = Response extends unknown
  ? Response extends { content: infer Content }
    ? Content extends { 'application/json': infer Body }
      ? Body
      : never
    : undefined
  : never

export type ApiJsonRequestBody<
  Path extends OpenApiPath,
  Method extends OpenApiMethod<Path>,
> = JsonBodyFor<OperationFor<Path, Method>>

export type ApiJsonResponse<
  Path extends OpenApiPath,
  Method extends OpenApiMethod<Path>,
> = JsonContentFor<SuccessfulResponseFor<OperationFor<Path, Method>>>

type RawBodyOverride<
  Path extends OpenApiPath,
  Method extends OpenApiMethod<Path>,
> = Path extends
  | '/api/v1/flows/validate'
  | '/api/v1/policies/flows/validate'
  | '/api/v1/flows/format'
  | '/api/v1/flows/{namespace}/{flow_id}/revisions/{revision}/diff-draft'
  ? Method extends 'post'
    ? string
    : never
  : Path extends '/api/v1/flows'
    ? Method extends 'put'
      ? string
      : never
    : Path extends
      | '/api/v1/namespaces/{namespace}/files/{path}'
      | '/api/v1/namespaces/{namespace}/images/{path}'
      ? Method extends 'put'
        ? File
        : never
      : never

type RequestBodyOptions<
  Path extends OpenApiPath,
  Method extends OpenApiMethod<Path>,
> = [ApiJsonRequestBody<Path, Method>] extends [never]
  ? [RawBodyOverride<Path, Method>] extends [never]
    ? { json?: never; rawBody?: never }
    : { json?: never; rawBody: RawBodyOverride<Path, Method> }
  : OperationFor<Path, Method> extends { requestBody: unknown }
    ? { json: ApiJsonRequestBody<Path, Method>; rawBody?: never }
    : { json?: ApiJsonRequestBody<Path, Method>; rawBody?: never }

export type ApiRequestOptions<
  Path extends OpenApiPath,
  Method extends OpenApiMethod<Path>,
> = Omit<RequestInit, 'body' | 'method'> & RequestBodyOptions<Path, Method>

export type ApiRequestArguments<
  Path extends OpenApiPath,
  Method extends OpenApiMethod<Path>,
> = RequestBodyOptions<Path, Method> extends { json: unknown } | { rawBody: unknown }
  ? [options: ApiRequestOptions<Path, Method>]
  : [options?: ApiRequestOptions<Path, Method>]

export type BlobOpenApiPath =
  | '/api/v1/assets/export/openlineage'
  | '/api/v1/dashboards/{dashboard_id}/export'
  | '/api/v1/executions/{execution_id}/files/{artifact_id}'
  | '/api/v1/namespaces/{namespace}/files/{path}'

export type NdjsonOpenApiPath =
  | '/api/v1/executions/{execution_id}/evidence/stream'
  | '/api/v1/agent-sessions/{service_session_id}/progress/stream'

export type BlobApiOperation<Path extends BlobOpenApiPath> = ApiOperation<
  Path,
  Extract<'get', OpenApiMethod<Path>>
>
export type NdjsonApiOperation<Path extends NdjsonOpenApiPath> = ApiOperation<
  Path,
  Extract<'get', OpenApiMethod<Path>>
>

type ExecutionEvidenceStreamItem = components['schemas']['ExecutionEvidenceEvent'] & {
  nextCursor: string
}

type AgentProgressHeartbeat = {
  type: 'heartbeat'
  sessionId: string
  cursor: string
}

export type ApiNdjsonItem<Path extends NdjsonOpenApiPath> =
  Path extends '/api/v1/executions/{execution_id}/evidence/stream'
    ? ExecutionEvidenceStreamItem
    : components['schemas']['AgentProgressEvent'] | AgentProgressHeartbeat

function canonicalPathPattern(template: string): RegExp {
  const escapedParts = template
    .split(/(\{[^/{}]+\})/u)
    .map((part) => part.startsWith('{') && part.endsWith('}')
      ? '(.+?)'
      : part.replace(/[.*+?^${}()|[\]\\]/gu, '\\$&'))
  return new RegExp(`^${escapedParts.join('')}$`, 'u')
}

function assertRuntimePathMatches(template: OpenApiPath, url: string): void {
  const baseUrl = new URL('http://amesh.local')
  const candidate = url.trim()
  if (/^[a-z][a-z\d+.-]*:/iu.test(candidate) || candidate.startsWith('//')) {
    throw new Error(`Runtime API URL must be same-origin and relative: "${url}"`)
  }
  const resolvedUrl = new URL(candidate, baseUrl)
  if (resolvedUrl.origin !== baseUrl.origin) {
    throw new Error(`Runtime API URL must be same-origin and relative: "${url}"`)
  }
  const pathname = resolvedUrl.pathname
  if (!canonicalPathPattern(template).test(pathname)) {
    throw new Error(`Runtime API pathname "${pathname}" does not match canonical template "${template}"`)
  }
}

export function apiOperation<
  Path extends OpenApiPath,
  Method extends OpenApiMethod<Path>,
>(template: Path, method: Method, url: string = template): ApiOperation<Path, Method> {
  assertRuntimePathMatches(template, url)
  return {
    template,
    method,
    url,
    [operationBrand]: (path, operationMethod) => [path, operationMethod],
  }
}
