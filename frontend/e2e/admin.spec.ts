import { expect, test, type Page } from '@playwright/test'
import AxeBuilder from '@axe-core/playwright'

const admin = { id: 1, username: 'Администратор', email: 'admin@example.com', role: 'admin' }
const researcher = {
  id: 2,
  username: 'Исследователь',
  email: 'researcher@example.com',
  role: 'researcher',
  director_id: null,
}
const director = { id: 3, username: 'Директор', email: 'director@example.com', role: 'director' }
const stamp = '2026-10-19T10:00:00Z'

async function mockSystem(page: Page, role = 'admin', cachedRole = role) {
  const profile = { ...admin, role }
  let users = [admin, researcher, director].map((user) => ({
    ...user,
    director_id: null as number | null,
  }))
  const requests: string[] = []
  await page.addInitScript(
    ({ user }) => {
      sessionStorage.setItem(
        'expert-polymer-session',
        JSON.stringify({ user, token: 'admin-token' }),
      )
    },
    { user: { ...admin, role: cachedRole } },
  )
  await page.route('http://127.0.0.1:5173/api/**', async (route) => {
    const request = route.request()
    const url = new URL(request.url())
    requests.push(url.pathname)
    if (request.headers().authorization !== 'Bearer admin-token') {
      await route.fulfill({ status: 401, json: { detail: 'Войдите в систему' } })
      return
    }
    if (url.pathname === '/api/auth/me') {
      await route.fulfill({ json: profile })
      return
    }
    if (profile.role !== 'admin') {
      await route.fulfill({ status: 403, json: { detail: 'Нет доступа' } })
      return
    }
    const offset = Number(url.searchParams.get('offset') || 0)
    const limit = Number(url.searchParams.get('limit') || 100)
    if (url.pathname === '/api/admin/dashboard') {
      await route.fulfill({
        json: {
          users_total: 3,
          admins: 1,
          directors: 1,
          researchers: 1,
          analyses_total: 28,
          tasks_total: 27,
          tasks_pending: 14,
          tasks_processing: 0,
          tasks_success: 0,
          tasks_failure: 13,
          active_invites: 1,
        },
      })
    } else if (url.pathname === '/api/users') {
      await route.fulfill({ json: users.slice(offset, offset + limit) })
    } else if (
      /^\/api\/users\/\d+\/(role|director)$/.test(url.pathname) &&
      request.method() === 'PATCH'
    ) {
      const id = Number(url.pathname.split('/')[3])
      const updates = request.postDataJSON()
      users = users.map((user) =>
        user.id === id
          ? {
              ...user,
              ...updates,
              ...(updates.role && updates.role !== 'researcher' ? { director_id: null } : {}),
            }
          : user,
      )
      await route.fulfill({ json: users.find((user) => user.id === id) })
    } else if (url.pathname === '/api/history') {
      let rows = Array.from({ length: 28 }, (_, index) => ({
        id: index + 1,
        user_id: index + 2,
        original_filename: 'sample-' + (index + 1) + '.png',
        result: 'Анализ завершён',
        confidence: index ? 0.93 : null,
        created_at: stamp,
      }))
      const userId = url.searchParams.get('user_id')
      if (userId) rows = rows.filter((row) => row.user_id === Number(userId))
      await route.fulfill({ json: rows.slice(offset, offset + limit) })
    } else if (url.pathname === '/api/admin/tasks') {
      let rows = Array.from({ length: 27 }, (_, index) => ({
        id: index + 1,
        task_id: 'task-' + (index + 1),
        original_filename: 'sample.png',
        user_id: 2,
        status: index % 2 ? 'FAILURE' : 'PENDING',
        result_id: null,
        error_message: index % 2 ? 'Не удалось обработать' : null,
        created_at: stamp,
        updated_at: stamp,
      }))
      const status = url.searchParams.get('status')
      if (status) rows = rows.filter((row) => row.status === status)
      await route.fulfill({ json: rows.slice(offset, offset + limit) })
    } else if (url.pathname === '/api/admin/invites') {
      await route.fulfill({
        json: [
          {
            id: 1,
            code: 'invite-2026',
            director_id: 3,
            is_active: true,
            created_at: stamp,
            expires_at: '2099-01-01T00:00:00Z',
          },
        ],
      })
    } else if (url.pathname === '/api/logs') {
      await route.fulfill({
        json: [
          {
            id: 1,
            actor_id: 1,
            action: 'CHANGE_USER_ROLE',
            target_type: 'user',
            target_id: 2,
            details: { old_role: 'researcher', new_role: 'director' },
            created_at: stamp,
          },
        ],
      })
    } else {
      await route.fulfill({ status: 404, json: { detail: 'Unknown endpoint: ' + url.pathname } })
    }
  })
  return { requests }
}

test('admin tabs preserve URLs, edit users and apply server filters with pagination', async ({
  page,
}) => {
  await mockSystem(page)
  await page.goto('/#/admin')
  await expect(page.getByRole('heading', { name: 'Обзор системы' })).toBeVisible()
  await expect(page.getByText('Всего пользователей', { exact: true })).toBeVisible()
  const tabs = page.getByRole('navigation', { name: 'Разделы панели администратора' })
  await tabs.getByRole('link', { name: 'Пользователи', exact: true }).click()
  const ownRole = page.getByRole('combobox', { name: 'Роль: Администратор', exact: true })
  await expect(ownRole).toBeDisabled()
  const directorSelect = page.getByRole('combobox', {
    name: 'Директор: Исследователь',
    exact: true,
  })
  const assigning = page.waitForRequest('**/api/users/2/director')
  await directorSelect.selectOption('3')
  expect((await assigning).postDataJSON()).toEqual({ director_id: 3 })
  await expect(directorSelect).toHaveValue('3')
  const changingRole = page.waitForRequest('**/api/users/2/role')
  await page
    .getByRole('combobox', { name: 'Роль: Исследователь', exact: true })
    .selectOption('director')
  expect((await changingRole).postDataJSON()).toEqual({ role: 'director' })
  await expect(directorSelect).toBeDisabled()
  await expect(directorSelect).toHaveValue('')
  await page.getByLabel('Поиск пользователей').fill('director@example.com')
  await expect(page.getByRole('row')).toHaveCount(2)
  await page.getByLabel('Поиск пользователей').clear()

  await tabs.getByRole('link', { name: 'История анализов', exact: true }).click()
  await page.getByLabel('ID пользователя').fill('2')
  await page.getByLabel('Дата анализа', { exact: true }).fill('2026-10-19')
  const filtering = page.waitForRequest(
    (request) => request.url().includes('/api/history?') && request.url().includes('user_id=2'),
  )
  await page.getByRole('button', { name: 'Применить', exact: true }).click()
  const historyUrl = new URL((await filtering).url())
  expect(historyUrl.searchParams.get('date')).toBe('2026-10-19')
  await expect(page.getByRole('row')).toHaveCount(2)
  await expect(page.getByRole('cell', { name: 'sample-1.png', exact: true })).toBeVisible()
  await expect(page.getByRole('cell', { name: '—', exact: true })).toBeVisible()

  await tabs.getByRole('link', { name: 'Задачи', exact: true }).click()
  await page.getByRole('button', { name: 'Далее', exact: true }).click()
  await expect(page.getByText('Страница 2', { exact: true })).toBeVisible()
  await expect(page.getByRole('cell', { name: 'task-26', exact: true })).toBeVisible()
  await page.getByLabel('Статус задачи').selectOption('FAILURE')
  await page.getByRole('button', { name: 'Применить', exact: true }).click()
  await expect(page.getByText('Страница 1', { exact: true })).toBeVisible()
  await expect(page.getByRole('row')).toHaveCount(14)
  await expect(page.getByRole('button', { name: 'Далее', exact: true })).toBeDisabled()

  await tabs.getByRole('link', { name: 'Инвайты', exact: true }).click()
  await expect(page.getByRole('cell', { name: 'invite-2026', exact: true })).toBeVisible()
  await tabs.getByRole('link', { name: 'Журнал действий', exact: true }).click()
  await page.getByLabel('Имя действия').fill('CHANGE_USER_ROLE')
  await page.getByLabel('Дата действия').fill('2026-10-19')
  const logs = page.waitForRequest(
    (request) =>
      request.url().includes('/api/logs?') && request.url().includes('action=CHANGE_USER_ROLE'),
  )
  await page.getByRole('button', { name: 'Применить', exact: true }).click()
  expect(new URL((await logs).url()).searchParams.get('date')).toBe('2026-10-19')
  await expect(page.getByRole('cell', { name: 'CHANGE_USER_ROLE', exact: true })).toBeVisible()
  await page.reload()
  await expect(page.getByRole('heading', { name: 'Журнал действий', exact: true })).toBeVisible()
  await page.goBack()
  await expect(page).toHaveURL(/#\/admin\/invites$/)
})

test('verified role protects direct admin routes and hides navigation from a non-admin', async ({
  page,
}) => {
  const { requests } = await mockSystem(page, 'researcher', 'admin')
  await page.goto('/#/admin/users')
  await expect(page).toHaveURL(/#\/profile$/)
  await expect(page.getByRole('heading', { name: admin.username, exact: true })).toBeVisible()
  expect(requests.filter((path) => path.startsWith('/api/admin') || path === '/api/users')).toEqual(
    [],
  )
  const navigation = page.getByRole('navigation', { name: 'Основная навигация' })
  if (await navigation.getByRole('button', { name: 'Меню', exact: true }).isVisible())
    await navigation.getByRole('button', { name: 'Меню', exact: true }).click()
  await expect(navigation.getByRole('link', { name: 'Админ-панель', exact: true })).toHaveCount(0)
})

test('all admin sections support mobile navigation and accessibility checks', async ({ page }) => {
  const errors: string[] = []
  page.on('pageerror', (error) => errors.push(error.message))
  await mockSystem(page)
  await page.goto('/#/profile')
  await expect(page.getByRole('heading', { name: admin.username, exact: true })).toBeVisible()
  const navigation = page.getByRole('navigation', { name: 'Основная навигация' })
  const adminLink = navigation.getByRole('link', { name: 'Админ-панель', exact: true })
  if (!(await adminLink.isVisible()))
    await navigation.getByRole('button', { name: 'Меню', exact: true }).click()
  await adminLink.click()
  for (const path of ['', '/users', '/history', '/tasks', '/invites', '/logs']) {
    await page.goto('/#/admin' + path)
    await expect(
      page.getByRole('heading', { name: 'Панель администратора', exact: true }),
    ).toBeVisible()
    await expect(page.locator('section[aria-busy="false"]')).toBeVisible()
    expect(
      await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth),
    ).toBe(true)
    const report = await new AxeBuilder({ page })
      .withTags(['wcag2a', 'wcag2aa', 'wcag21aa'])
      .analyze()
    expect(report.violations, path).toEqual([])
  }
  expect(errors).toEqual([])
})

test('failed user edits keep the saved role and leave controls usable for retry', async ({
  page,
}) => {
  await mockSystem(page)
  await page.route('**/api/users/2/role', (route) =>
    route.fulfill({ status: 503, json: { detail: 'Изменение временно недоступно' } }),
  )
  await page.goto('/#/admin/users')
  const role = page.getByRole('combobox', { name: 'Роль: Исследователь', exact: true })
  await role.selectOption('director')
  await expect(page.getByRole('alert')).toHaveText('Изменение временно недоступно')
  await expect(role).toHaveValue('researcher')
  await expect(role).toBeEnabled()
  await expect(page.getByRole('button', { name: 'Обновить', exact: true })).toBeEnabled()
})

test('a guest opening an admin URL preserves the destination on the login page', async ({
  page,
}) => {
  await page.goto('/#/admin/logs')
  await expect(page).toHaveURL(/#\/login\?redirect=\/admin\/logs$/)
  await expect(page.getByRole('heading', { name: 'Войти в систему', exact: true })).toBeVisible()
})

test('refreshing a revoked admin role immediately closes the current panel', async ({ page }) => {
  await mockSystem(page)
  await page.goto('/#/admin/logs')
  await expect(page.getByRole('cell', { name: 'CHANGE_USER_ROLE', exact: true })).toBeVisible()
  await page.route('**/api/auth/me', (route) =>
    route.fulfill({ json: { ...admin, role: 'researcher' } }),
  )
  await page.evaluate(() => window.dispatchEvent(new Event('focus')))
  await expect(page).toHaveURL(/#\/profile$/)
  await expect(
    page.getByRole('heading', { name: 'Панель администратора', exact: true }),
  ).toHaveCount(0)
})
