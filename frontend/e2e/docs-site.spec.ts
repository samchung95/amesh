import AxeBuilder from '@axe-core/playwright'
import { expect, test } from '@playwright/test'

const journeys = [
  { name: 'home', path: '/', heading: 'AMESH documentation' },
  { name: 'getting started', path: '/getting-started/', heading: 'Getting started' },
  { name: 'workflow guide', path: '/workflows/', heading: 'Build workflows' },
  { name: 'agent-session guide', path: '/agents/', heading: 'Build and run agents' },
] as const

for (const journey of journeys) {
  test(`${journey.name} renders, exposes local search, and passes axe`, async ({ page }, testInfo) => {
    const response = await page.goto(journey.path)

    expect(response?.ok()).toBe(true)
    await expect(page.locator('main h1').first()).toContainText(journey.heading)

    const searchInput = page.locator('[data-md-component="search-query"]')
    await expect(searchInput).toBeAttached()
    if (journey.name === 'home' && testInfo.project.name === 'desktop') {
      if (!(await searchInput.isVisible())) {
        await page.locator('label.md-header__button[for="__search"]').click()
      }
      await expect(searchInput).toBeVisible()
      await searchInput.fill('capability envelope')

      const result = page
        .locator('[data-md-component="search-result"] a')
        .filter({ hasText: /capability envelope/i })
        .first()
      await expect(result).toBeVisible()
      await expect(result).toHaveAttribute('href', /define-agent-capability-envelope/)
    }

    const accessibility = await new AxeBuilder({ page })
      .withTags(['wcag2a', 'wcag2aa', 'wcag22aa'])
      .analyze()
    const seriousViolations = accessibility.violations.filter(
      ({ impact }) => impact === 'critical' || impact === 'serious',
    )

    expect(seriousViolations, JSON.stringify(seriousViolations, null, 2)).toEqual([])
  })
}
