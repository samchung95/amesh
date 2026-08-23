import type { ExecutionArtifact } from './models/ExecutionArtifact';
import { ExecutionArtifactFromJSON } from './models/ExecutionArtifact';
import type { ExecutionDetail } from './models/ExecutionDetail';
import { ExecutionDetailFromJSON } from './models/ExecutionDetail';
import type { TaskLog } from './models/TaskLog';
import { TaskLogFromJSON } from './models/TaskLog';

const terminalStates = new Set(['CANCELLED', 'SUCCESS', 'FAILED', 'WARNING']);
const retryableStatus = new Set([408, 429, 502, 503, 504]);

export interface RetryPolicy {
  maxAttempts?: number;
  initialDelayMs?: number;
  maximumDelayMs?: number;
}

export interface ExecutionClientOptions {
  endpoint: string;
  token: string;
  tenant?: string;
  fetchApi?: typeof fetch;
  retryPolicy?: RetryPolicy;
  timeoutMs?: number;
  sleep?: (milliseconds: number) => Promise<void>;
}

export class AmeshError extends Error {
  readonly name = 'AmeshError';

  constructor(
    message: string,
    readonly status: number,
    readonly code = 'request_failed',
    readonly requestId = '',
    readonly retryable = false,
  ) {
    super(message);
    Object.setPrototypeOf(this, new.target.prototype);
  }
}

interface RequestOptions {
  body?: unknown;
  idempotencyKey?: string;
  retryable?: boolean;
  accept?: string;
}

export class ExecutionClient {
  private readonly endpoint: string;
  private readonly tenant: string;
  private readonly fetchApi: typeof fetch;
  private readonly retry: Required<RetryPolicy>;
  private readonly timeoutMs: number;
  private readonly sleep: (milliseconds: number) => Promise<void>;

  constructor(private readonly options: ExecutionClientOptions) {
    if (!options.endpoint || !options.token) {
      throw new Error('endpoint and token are required');
    }
    this.endpoint = options.endpoint.replace(/\/+$/, '');
    this.tenant = options.tenant ?? 'default';
    this.fetchApi = options.fetchApi ?? fetch;
    this.retry = {
      maxAttempts: options.retryPolicy?.maxAttempts ?? 3,
      initialDelayMs: options.retryPolicy?.initialDelayMs ?? 250,
      maximumDelayMs: options.retryPolicy?.maximumDelayMs ?? 2000,
    };
    if (this.retry.maxAttempts < 1) {
      throw new Error('maxAttempts must be at least one');
    }
    this.timeoutMs = options.timeoutMs ?? 30000;
    this.sleep = options.sleep ?? ((milliseconds) => new Promise((resolve) => setTimeout(resolve, milliseconds)));
  }

  async launch(
    namespace: string,
    flowId: string,
    inputs: Record<string, unknown> = {},
    runner = 'local',
    idempotencyKey = randomIdempotencyKey(),
  ): Promise<ExecutionDetail> {
    const value = await this.json('POST', '/api/v1/executions', {
      body: { namespace, flowId, inputs, runner, idempotencyKey },
      idempotencyKey,
      retryable: true,
    });
    return ExecutionDetailFromJSON(value);
  }

  async get(executionId: string): Promise<ExecutionDetail> {
    return ExecutionDetailFromJSON(
      await this.json('GET', `/api/v1/executions/${encodeURIComponent(executionId)}`),
    );
  }

  async waitForTerminal(
    executionId: string,
    timeoutMs = 300000,
    pollMs = 1000,
  ): Promise<ExecutionDetail> {
    const deadline = Date.now() + timeoutMs;
    for (;;) {
      const detail = await this.get(executionId);
      if (terminalStates.has(detail.execution.state)) return detail;
      const remaining = deadline - Date.now();
      if (remaining <= 0) throw new Error(`execution ${executionId} did not reach a terminal state`);
      await this.sleep(Math.min(pollMs, remaining));
    }
  }

  async cancel(
    executionId: string,
    reason = 'cancelled by SDK client',
    graceSeconds = 30,
  ): Promise<ExecutionDetail> {
    const current = await this.get(executionId);
    return ExecutionDetailFromJSON(
      await this.json(
        'POST',
        `/api/v1/executions/${encodeURIComponent(executionId)}/interventions`,
        {
          body: {
            action: 'REQUEST_CANCEL',
            expectedVersion: current.execution.version,
            expectedEpoch: current.execution.epoch,
            reason,
            graceSeconds,
          },
        },
      ),
    );
  }

  async logs(executionId: string): Promise<TaskLog[]> {
    const value = await this.json(
      'GET',
      `/api/v1/executions/${encodeURIComponent(executionId)}/logs`,
    );
    if (!Array.isArray(value)) throw new AmeshError('AMESH returned an invalid log collection', 502);
    return value.map(TaskLogFromJSON);
  }

  async artifacts(executionId: string): Promise<ExecutionArtifact[]> {
    const value = await this.json(
      'GET',
      `/api/v1/executions/${encodeURIComponent(executionId)}/files`,
    );
    if (!Array.isArray(value)) throw new AmeshError('AMESH returned an invalid artifact collection', 502);
    return value.map(ExecutionArtifactFromJSON);
  }

  async downloadArtifact(executionId: string, artifactId: string): Promise<Uint8Array> {
    const response = await this.request(
      'GET',
      `/api/v1/executions/${encodeURIComponent(executionId)}/files/${encodeURIComponent(artifactId)}`,
    );
    return new Uint8Array(await response.arrayBuffer());
  }

  async *streamLogs(executionId: string): AsyncGenerator<Record<string, unknown>> {
    const response = await this.request(
      'GET',
      `/api/v1/executions/${encodeURIComponent(executionId)}/logs/stream`,
      { accept: 'application/x-ndjson' },
    );
    for (const line of (await response.text()).split(/\r?\n/)) {
      if (line.trim()) yield JSON.parse(line) as Record<string, unknown>;
    }
  }

  private async json(method: string, path: string, options: RequestOptions = {}): Promise<unknown> {
    const response = await this.request(method, path, options);
    try {
      return await response.json();
    } catch (error) {
      throw new AmeshError('AMESH returned invalid JSON', 502, 'invalid_response', '', false);
    }
  }

  private async request(method: string, path: string, options: RequestOptions = {}): Promise<Response> {
    const headers: Record<string, string> = {
      Accept: options.accept ?? 'application/json',
      Authorization: `Bearer ${this.options.token}`,
      'X-Amesh-Tenant': this.tenant,
    };
    let body: string | undefined;
    if (options.body !== undefined) {
      headers['Content-Type'] = 'application/json';
      body = JSON.stringify(options.body);
    }
    if (options.idempotencyKey) headers['Idempotency-Key'] = options.idempotencyKey;
    const canRetry = options.retryable ?? method === 'GET';
    let delay = this.retry.initialDelayMs;
    let lastError: AmeshError | undefined;
    for (let attempt = 0; attempt < this.retry.maxAttempts; attempt += 1) {
      const controller = new AbortController();
      const timeout = setTimeout(() => controller.abort(), this.timeoutMs);
      try {
        const response = await this.fetchApi(this.endpoint + path, {
          method,
          headers,
          body,
          signal: controller.signal,
        });
        if (response.ok) return response;
        lastError = await responseError(response);
        if (!canRetry || !lastError.retryable || attempt + 1 >= this.retry.maxAttempts) {
          throw lastError;
        }
        delay = retryAfter(response.headers, delay);
      } catch (error) {
        if (error instanceof AmeshError) {
          if (!canRetry || !error.retryable || attempt + 1 >= this.retry.maxAttempts) throw error;
          lastError = error;
        } else {
          lastError = new AmeshError('AMESH transport failed', 0, 'transport_error', '', true);
          if (!canRetry || attempt + 1 >= this.retry.maxAttempts) throw lastError;
        }
      } finally {
        clearTimeout(timeout);
      }
      await this.sleep(delay);
      delay = Math.min(Math.max(delay * 2, this.retry.initialDelayMs), this.retry.maximumDelayMs);
    }
    throw lastError ?? new AmeshError('AMESH request failed', 0);
  }
}

export async function verifyWebhook(
  secret: string,
  timestamp: number,
  deliveryId: string,
  body: Uint8Array,
  signature: string,
  nowSeconds = Math.floor(Date.now() / 1000),
  toleranceSeconds = 300,
): Promise<boolean> {
  if (toleranceSeconds < 0 || Math.abs(nowSeconds - timestamp) > toleranceSeconds) return false;
  const prefix = new TextEncoder().encode(`${timestamp}.${deliveryId}.`);
  const signed = new Uint8Array(prefix.length + body.length);
  signed.set(prefix);
  signed.set(body, prefix.length);
  const key = await crypto.subtle.importKey(
    'raw',
    new TextEncoder().encode(secret),
    { name: 'HMAC', hash: 'SHA-256' },
    false,
    ['sign'],
  );
  const digest = new Uint8Array(await crypto.subtle.sign('HMAC', key, signed));
  const expected = `v1=${Array.from(digest, (value) => value.toString(16).padStart(2, '0')).join('')}`;
  return constantTimeEqual(expected, signature);
}

function randomIdempotencyKey(): string {
  const bytes = new Uint8Array(16);
  crypto.getRandomValues(bytes);
  return Array.from(bytes, (value) => value.toString(16).padStart(2, '0')).join('');
}

async function responseError(response: Response): Promise<AmeshError> {
  let message = `AMESH request failed with HTTP ${response.status}`;
  let code = 'request_failed';
  try {
    const value = await response.clone().json() as Record<string, unknown>;
    if (typeof value.detail === 'string' && value.detail.length <= 512) message = value.detail;
    if (typeof value.code === 'string') code = value.code;
  } catch (_) {
    // Error helpers intentionally avoid copying an arbitrary response body.
  }
  return new AmeshError(
    message,
    response.status,
    code,
    response.headers.get('x-request-id') ?? '',
    retryableStatus.has(response.status),
  );
}

function retryAfter(headers: Headers, fallback: number): number {
  const seconds = Number(headers.get('retry-after'));
  return Number.isFinite(seconds) && seconds >= 0 ? seconds * 1000 : fallback;
}

function constantTimeEqual(left: string, right: string): boolean {
  let difference = left.length ^ right.length;
  const length = Math.max(left.length, right.length);
  for (let index = 0; index < length; index += 1) {
    const leftCode = index < left.length ? left.charCodeAt(index) : 0;
    const rightCode = index < right.length ? right.charCodeAt(index) : 0;
    difference |= leftCode ^ rightCode;
  }
  return difference === 0;
}
