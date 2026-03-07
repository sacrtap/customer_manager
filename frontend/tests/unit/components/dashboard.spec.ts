import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import Dashboard from '@/views/Dashboard.vue'

describe('Dashboard', () => {
  it('renders dashboard content', () => {
    const wrapper = mount(Dashboard, {
      global: {
        stubs: {
          'a-layout': true,
          'a-layout-content': true,
          'a-card': true,
          'a-row': true,
          'a-col': true,
          'a-statistic': true,
          'echarts': true,
        },
      },
    })
    expect(wrapper.text()).toContain('客户总数')
  })
})
