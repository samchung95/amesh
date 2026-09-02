import { createTransport, type ApiConnection } from './transport'
import { createAdministrationResource } from './resources/administration'
import { createGeneralResource } from './resources/general'
import { createNamespaceResource } from './resources/namespace'
import { createOperationsResource } from './resources/operations'
import { createSessionsResource } from './resources/sessions'
import { createSystemResource } from './resources/system'
import { createRuntimeResource } from './resources/runtime'
import { createWorkflowsResource } from './resources/workflows'

export type { ApiConnection } from './transport'
export { ApiError } from './transport'

export function createApiClient(connection: ApiConnection) {
  const transport = createTransport(connection)
  return {
    ...createSystemResource(transport),
    ...createGeneralResource(transport),
    ...createAdministrationResource(transport),
    ...createWorkflowsResource(transport),
    ...createOperationsResource(transport),
    ...createNamespaceResource(transport),
    ...createSessionsResource(transport),
    ...createRuntimeResource(transport),
  }
}
