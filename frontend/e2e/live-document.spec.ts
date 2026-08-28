import { expect, test } from '@playwright/test'

const baseUrl = process.env.AMESH_LIVE_BASE_URL ?? ''
const executionId = process.env.AMESH_LIVE_DOCUMENT_EXECUTION_ID ?? ''
const apiToken = process.env.AMESH_LIVE_API_TOKEN ?? ''

test('inspects a deployed document pipeline result', async ({ page }, testInfo) => {
  test.skip(
    !baseUrl || !executionId || !apiToken,
    'Set AMESH_LIVE_BASE_URL, AMESH_LIVE_DOCUMENT_EXECUTION_ID, and AMESH_LIVE_API_TOKEN.',
  )

  await page.goto(baseUrl)
  await page.getByRole('button', { name: 'API token' }).click()
  await page.getByLabel('API token').fill(apiToken)
  await page.getByRole('button', { name: 'Open control room' }).click()
  await page.goto(`${baseUrl}/executions/${executionId}`)

  await expect(page.getByRole('heading', { name: 'document-pipeline-823' })).toBeVisible()
  await page.locator('summary').filter({ hasText: 'Advanced evidence' }).click()
  await page.getByRole('button', { name: 'Data', exact: true }).click()
  const extractionResults = page.getByLabel('Extraction results')
  await expect(extractionResults).toBeVisible()
  await expect(extractionResults.getByRole('code').filter({ hasText: 'nsfile:///documents/live-report.pdf?version=1&sha256=' })).toBeVisible()
  await expect(extractionResults.getByText(/amesh\.core\.document\.extract@0\.2\.0 · pypdf@6\.16\.1/)).toBeVisible()
  await expect(extractionResults.getByText(/Hello AMESH live document/).first()).toBeVisible()
  await expect(page.getByText('document-result.json', { exact: true })).toBeVisible()

  await page.screenshot({ path: testInfo.outputPath('live-document-pipeline.png'), fullPage: true })
})
