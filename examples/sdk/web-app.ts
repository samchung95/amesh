import { ExecutionClient } from '@amesh/client';

const client = new ExecutionClient({
  endpoint: process.env.AMESH_ENDPOINT!,
  token: process.env.AMESH_TOKEN!,
  tenant: process.env.AMESH_TENANT ?? 'default',
});

export async function postRun(request: Request): Promise<Response> {
  const { name = 'SDK web app' } = await request.json() as { name?: string };
  const execution = await client.launch('examples.getting_started', 'hello_world', { name });
  return Response.json(
    { executionId: execution.execution.executionId },
    { status: 202 },
  );
}
