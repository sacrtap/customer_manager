import { createPinia, setActivePinia } from 'pinia'
import { beforeAll } from 'vitest'

beforeAll(() => {
  setActivePinia(createPinia())
})
