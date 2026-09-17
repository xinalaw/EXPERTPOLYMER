import { expect, test, type Page } from '@playwright/test'
import AxeBuilder from '@axe-core/playwright'

const browserErrors = new WeakMap<Page, string[]>()
test.afterEach(async ({ context }) => {
  for (const page of context.pages()) expect(browserErrors.get(page) || []).toEqual([])
})

const user = {
  id: 1,
  username: 'Анна Исследователь',
  first_name: 'Анна',
  email: 'anna@example.com',
  role: 'researcher',
}
const result = {
  id: 1,
  user_id: 1,
  original_filename: 'sample.png',
  result: 'Анализ завершён',
  confidence: 0.93,
  width: 640,
  height: 480,
  created_at: '2026-09-10T10:00:00Z',
  image_path: '/static/uploads/sample.png',
  processed_image_path: '/static/processed/sample.png',
  result_data: { particles_detected: 12, expert: { verdict: 'conditional', score: 70 } },
}
const png = Buffer.from(
  'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAusB9Wl6H9sAAAAASUVORK5CYII=',
  'base64',
)

test.beforeEach(async ({ page, context }) => {
  function trackErrors(tab: Page) {
    const errors: string[] = []
    browserErrors.set(tab, errors)
    tab.on('pageerror', (error) => errors.push(error.message))
  }
  trackErrors(page)
  context.on('page', trackErrors)
  let rows = Array.from({ length: 21 }, (_, i) => ({
    ...result,
    id: i + 1,
    original_filename: `sample-${i + 1}.png`,
  }))
  await context.route('http://127.0.0.1:5173/api/**', async (route) => {
    const request = route.request()
    const url = new URL(request.url())
    const isPublic = ['/api/auth/login', '/api/auth/register'].includes(url.pathname)
    if (!isPublic && request.headers().authorization !== 'Bearer test-token') {
      await route.fulfill({ status: 401, json: { detail: 'Войдите в систему' } })
      return
    }
    if (url.pathname === '/api/auth/me') {
      await route.fulfill({ json: user })
    } else if (url.pathname === '/api/auth/login' && request.method() === 'POST') {
      await route.fulfill({ json: { access_token: 'test-token', token_type: 'bearer' } })
    } else if (url.pathname === '/api/auth/register') {
      await route.fulfill({ json: user })
    } else if (url.pathname === '/api/history') {
      const offset = Number(url.searchParams.get('offset') || 0)
      const limit = Number(url.searchParams.get('limit') || 20)
      const filtered = url.searchParams.get('date') ? rows.slice(0, 1) : rows
      await route.fulfill({ json: filtered.slice(offset, offset + limit) })
    } else if (url.pathname === '/api/analyze') {
      await route.fulfill({ json: result })
    } else if (/^\/api\/results\/\d+$/.test(url.pathname) && request.method() === 'DELETE') {
      rows = rows.filter((row) => row.id !== Number(url.pathname.split('/').pop()))
      await route.fulfill({ json: { message: 'Удалено' } })
    } else {
      await route.fulfill({
        status: 404,
        json: { detail: `Unknown test endpoint: ${request.method()} ${url.pathname}` },
      })
    }
  })
  await context.route('**/static/**', (route) =>
    route.fulfill({ contentType: 'image/png', body: png }),
  )
})

async function navigate(page: Page, text: string) {
  const navigation = page.getByRole('navigation', { name: 'Основная навигация' })
  const link = navigation.getByRole('link', { name: text, exact: true })
  if (!(await link.isVisible())) {
    await navigation.getByRole('button', { name: 'Меню', exact: true }).click()
  }
  await link.click()
}

async function login(page: Page, target = '/analysis', remember = false) {
  await page.goto('/#' + target)
  await expect(page.getByRole('heading', { name: 'Войти в систему' })).toBeVisible()
  await page.getByLabel('Email', { exact: true }).fill(user.email)
  await page.getByLabel('Пароль', { exact: true }).fill('test12345')
  if (remember) await page.getByLabel('Запомнить меня на этом устройстве').check()
  await page.getByRole('button', { name: 'Войти', exact: true }).click()
  await expect(page).toHaveURL(new RegExp('/#' + target))
  await expect(page.locator('main h1')).toBeVisible()
}

async function logout(page: Page) {
  const navigation = page.getByRole('navigation', { name: 'Основная навигация' })
  const userButton = navigation.getByRole('button', { name: user.username })
  if (!(await userButton.isVisible()))
    await navigation.getByRole('button', { name: 'Меню', exact: true }).click()
  await userButton.click()
  await navigation.getByRole('button', { name: 'Выйти', exact: true }).click()
  await expect(page.getByRole('heading', { name: /Экспертная система анализа/ })).toBeVisible()
}

test('navigation, browser back and refresh preserve URLs and avoid horizontal overflow', async ({
  page,
}) => {
  await page.goto('/')
  await expect(page.getByRole('heading', { name: /Экспертная система анализа/ })).toBeVisible()
  await page.screenshot({ path: test.info().outputPath('home.png'), fullPage: true })
  await page.getByRole('link', { name: 'Узнать больше' }).click()
  await expect(page.getByRole('heading', { name: 'О системе Expert Polymer' })).toBeVisible()
  await page.goBack()
  await expect(page.getByRole('heading', { name: /Экспертная система анализа/ })).toBeVisible()
  await page.goForward()
  await page.reload()
  await expect(page).toHaveURL(/#\/about$/)
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(
    true,
  )
  await navigate(page, 'Контакты')
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(
    true,
  )
  await page.getByLabel('Ваше имя').fill('Анна')
  await page.getByLabel('Email для ответа').fill(user.email)
  await page.getByLabel('Тема', { exact: true }).fill('Консультация')
  await page
    .getByLabel('Сообщение', { exact: true })
    .fill('Помогите разобраться с анализом образца.')
  await page.getByRole('button', { name: 'Подготовить письмо', exact: true }).click()
  await expect(page.getByRole('link', { name: 'Открыть почтовую программу' })).toHaveAttribute(
    'href',
    /^mailto:info@expertpolymer.ru\?subject=/,
  )
  await expect(page.getByText('Сообщение успешно отправлено')).toHaveCount(0)
})

test('analysis validates files, downloads JSON and survives page navigation', async ({ page }) => {
  await login(page)
  await page
    .locator('input[type=file]')
    .setInputFiles({ name: 'bad.png', mimeType: 'image/png', buffer: Buffer.from('not an image') })
  await expect(page.getByRole('alert')).toContainText('не соответствует')
  await page
    .locator('input[type=file]')
    .setInputFiles({ name: 'sample.png', mimeType: 'image/png', buffer: png })
  await page.getByRole('button', { name: 'Начать анализ', exact: true }).click()
  await expect(page.getByRole('heading', { name: 'Результаты анализа' })).toBeVisible()
  await page.screenshot({ path: test.info().outputPath('analysis.png'), fullPage: true })
  const downloaded = page.waitForEvent('download')
  await page.getByRole('button', { name: 'Скачать отчёт (JSON)' }).click()
  expect((await downloaded).suggestedFilename()).toBe('analysis-report-1.json')
  await navigate(page, 'О системе')
  await page.getByRole('main').getByRole('link', { name: 'Попробовать анализ' }).click()
  await expect(page.getByRole('heading', { name: 'Результаты анализа' })).toBeVisible()
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(
    true,
  )
})

test('history paginates, resets date offset and confirms deletion with keyboard focus', async ({
  page,
}) => {
  await login(page, '/history')
  await expect(page.locator('article.history-card')).toHaveCount(20)
  await page.getByRole('button', { name: 'Вперёд', exact: true }).click()
  await expect(page.locator('article.history-card')).toHaveCount(1)
  await expect(page.getByRole('button', { name: 'Вперёд', exact: true })).toBeDisabled()
  await page.getByLabel('Фильтр по дате').fill('2026-09-10')
  await expect(page).not.toHaveURL(/page=2/)
  await expect(page.locator('article.history-card')).toHaveCount(1)
  await page.getByRole('button', { name: 'sample-1.png' }).click()
  const remove = page.getByRole('button', { name: 'Удалить анализ', exact: true })
  await remove.click()
  const dialog = page.getByRole('dialog', { name: 'Удалить анализ?' })
  await expect(dialog).toBeVisible()
  await expect(dialog.getByRole('button', { name: 'Отмена' })).toBeFocused()
  await page.keyboard.press('Escape')
  await expect(dialog).not.toBeVisible()
  await expect(remove).toBeFocused()
  await remove.click()
  await dialog.getByRole('button', { name: 'Удалить', exact: true }).click()
  await expect(page.getByRole('status')).toContainText('Анализ удалён')
})

test('profile, settings and expired-session redirect are usable', async ({ page }) => {
  await login(page, '/profile')
  await expect(page.getByRole('heading', { name: user.username })).toBeVisible()
  await page
    .getByRole('navigation', { name: 'Дополнительная навигация' })
    .getByRole('link', { name: 'Настройки' })
    .click()
  await page.getByLabel('Уменьшить анимацию').check()
  await page.getByLabel('Анализов на странице истории').selectOption('10')
  await page.getByRole('button', { name: 'Сохранить настройки' }).click()
  await page.reload()
  await expect(page.getByLabel('Уменьшить анимацию')).toBeChecked()
  await expect(page.getByLabel('Анализов на странице истории')).toHaveValue('10')
  await page.route('**/api/history*', (route) =>
    route.fulfill({ status: 401, json: { detail: 'Expired' } }),
  )
  await navigate(page, 'История')
  await expect(page).toHaveURL(/#\/login\?redirect=/)
  await expect(page.getByRole('heading', { name: 'Войти в систему' })).toBeVisible()
})

test('pages and forms pass automated accessibility checks', async ({ page }) => {
  for (const path of ['/', '/register', '/contacts', '/settings']) {
    await page.goto('/#' + path)
    await expect(page.locator('main h1')).toBeVisible()
    const report = await new AxeBuilder({ page })
      .withTags(['wcag2a', 'wcag2aa', 'wcag21aa'])
      .analyze()
    expect(report.violations, path).toEqual([])
  }
})

test('remembered logout synchronizes across two tabs and survives reload', async ({
  page,
  context,
}) => {
  await login(page, '/profile', true)
  const second = await context.newPage()
  await second.goto('/#/profile')
  await expect(second.getByRole('heading', { name: user.username })).toBeVisible()
  await logout(page)
  await expect(second).toHaveURL(/#\/login\?redirect=/)
  await expect(second.getByRole('heading', { name: 'Войти в систему' })).toBeVisible()
  expect(await second.evaluate(() => localStorage.getItem('expert-polymer-session'))).toBeNull()
  await second.reload()
  await expect(second.getByRole('heading', { name: 'Войти в систему' })).toBeVisible()
})

test('an expired restored session is removed instead of retried on every reload', async ({
  page,
}) => {
  await login(page, '/profile', true)
  let profileRequests = 0
  await page.route('**/api/auth/me', (route) => {
    profileRequests++
    return route.fulfill({ status: 401, json: { detail: 'Expired' } })
  })
  await page.reload()
  await expect(page.getByRole('heading', { name: 'Войти в систему' })).toBeVisible()
  expect(await page.evaluate(() => localStorage.getItem('expert-polymer-session'))).toBeNull()
  const requestsAfterExpiry = profileRequests
  await page.reload()
  await expect(page.getByRole('heading', { name: 'Войти в систему' })).toBeVisible()
  expect(profileRequests).toBe(requestsAfterExpiry)
})

test('failed profile loading leaves the login form usable without persisting a token', async ({
  page,
}) => {
  await page.route('**/api/auth/me', (route) =>
    route.fulfill({ status: 503, json: { detail: 'Профиль временно недоступен' } }),
  )
  await page.goto('/#/login?redirect=/profile')
  await page.getByLabel('Email', { exact: true }).fill(user.email)
  await page.getByLabel('Пароль', { exact: true }).fill('test12345')
  await page.getByRole('button', { name: 'Войти', exact: true }).click()
  await expect(page.getByRole('alert')).toContainText('Профиль временно недоступен')
  expect(
    await page.evaluate(() => [
      localStorage.getItem('expert-polymer-session'),
      sessionStorage.getItem('expert-polymer-session'),
    ]),
  ).toEqual([null, null])
  await page.unroute('**/api/auth/me')
  await page.getByRole('button', { name: 'Войти', exact: true }).click()
  await expect(page.getByRole('heading', { name: user.username })).toBeVisible()
})

test('login, focus refresh and logout work when the browser blocks storage', async ({
  page,
  context,
}) => {
  await context.addInitScript(() => {
    for (const name of ['localStorage', 'sessionStorage']) {
      Object.defineProperty(window, name, {
        configurable: true,
        get() {
          throw new DOMException('Storage blocked for test', 'SecurityError')
        },
      })
    }
  })
  await login(page, '/profile')
  const refreshed = page.waitForResponse('**/api/auth/me')
  await page.evaluate(() => window.dispatchEvent(new Event('focus')))
  await refreshed
  await expect(page.getByRole('heading', { name: user.username })).toBeVisible()
  await logout(page)
})

test('registration submits matching passwords and completes authenticated navigation', async ({
  page,
}) => {
  await page.goto('/#/register')
  await page.getByLabel('Имя', { exact: true }).fill('Анна')
  await page.getByLabel('Фамилия', { exact: true }).fill('Исследователь')
  await page.getByLabel('Email', { exact: true }).fill(user.email)
  await page.getByLabel('Пароль', { exact: true }).fill('test12345')
  await page.getByLabel('Подтвердите пароль', { exact: true }).fill('test12345')
  const registration = page.waitForRequest('**/api/auth/register')
  await page.getByRole('button', { name: 'Зарегистрироваться', exact: true }).click()
  expect((await registration).postDataJSON()).toMatchObject({
    first_name: 'Анна',
    last_name: 'Исследователь',
    email: user.email,
    password: 'test12345',
    password_confirm: 'test12345',
  })
  await expect(page).toHaveURL(/#\/analysis$/)
  await expect(
    page.getByRole('heading', { name: 'Анализ композитных материалов', exact: true }),
  ).toBeVisible()
})
