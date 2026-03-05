<!-- frontend/src/views/customer/CustomerImport.vue -->
<template>
  <div class="customer-import">
    <Card class="import-card">
      <template #title>
        <div class="card-header">
          <span class="card-title">批量导入客户</span>
          <Button @click="handleDownloadTemplate">
            <template #icon><icon-download /></template>
            下载模板
          </Button>
        </div>
      </template>

      <a-steps :current="currentStep" line-less class="import-steps">
        <a-step description="下载并填写导入模板" title="1. 下载模板" />
        <a-step description="上传填写好的 Excel 文件" title="2. 上传文件" />
        <a-step description="确认导入结果" title="3. 导入完成" />
      </a-steps>

      <div class="import-content">
        <!-- Step 1: 上传文件 -->
        <div v-show="currentStep === 0" class="step-content">
          <div class="upload-area">
            <a-upload
              ref="uploadRef"
              :auto-upload="false"
              :show-file-list="true"
              :show-cancel-button="true"
              drag
              @change="handleFileChange"
            >
              <template #upload-area>
                <div class="upload-dragger">
                  <icon-upload class="upload-icon" />
                  <div class="upload-text">
                    <p class="upload-title">将文件拖到此处，或<span class="highlight">点击上传</span></p>
                    <p class="upload-hint">支持 .xlsx 格式的 Excel 文件</p>
                  </div>
                </div>
              </template>
            </a-upload>

            <div class="template-info">
              <icon-info-circle />
              <span>请先下载导入模板，按照模板格式填写客户信息后上传</span>
            </div>
          </div>

          <div class="step-actions">
            <Button type="primary" :disabled="!selectedFile" @click="handleUpload">
              <template #icon><icon-upload /></template>
              开始导入
            </Button>
          </div>
        </div>

        <!-- Step 2: 导入中 -->
        <div v-show="currentStep === 1" class="step-content">
          <div class="uploading">
            <icon-loading class="loading-icon" />
            <p class="loading-text">正在导入，请稍候...</p>
            <p class="loading-hint">
              已上传 {{ uploadProgress }}%
            </p>
          </div>
        </div>

        <!-- Step 3: 导入结果 -->
        <div v-show="currentStep === 2" class="step-content">
          <a-result
            :status="importSuccess ? 'success' : 'warning'"
            :title="importSuccess ? '导入完成' : '部分导入成功'"
            :subtitle="`成功导入 ${successCount} 条，失败 ${failedCount} 条`"
          >
            <template #icon>
              <icon-check-circle v-if="importSuccess" class="result-icon success" />
              <icon-exclamation-circle v-else class="result-icon warning" />
            </template>
          </a-result>

          <div v-if="failedCount > 0" class="error-list">
            <div class="error-title">
              <icon-exclamation-circle />
              <span>失败详情（共 {{ failedCount }} 条）</span>
            </div>
            <a-table
              :columns="errorColumns"
              :data="importErrors"
              :pagination="{ pageSize: 5, simple: true }"
              border-cell
            />
          </div>

          <div class="step-actions">
            <Button @click="handleBackToList">
              <template #icon><icon-arrow-left /></template>
              返回列表
            </Button>
            <Button @click="handleReset">
              <template #icon><icon-refresh /></template>
              继续导入
            </Button>
          </div>
        </div>
      </div>
    </Card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { Message, UploadRef } from '@arco-design/web-vue'
import { customerApi } from '@/api/customer'

const router = useRouter()
const uploadRef = ref<UploadRef>()
const currentStep = ref(0)
const selectedFile = ref<File | null>(null)
const uploading = ref(false)
const uploadProgress = ref(0)
const importSuccess = ref(true)
const successCount = ref(0)
const failedCount = ref(0)
const importErrors = ref<any[]>([])

const errorColumns = [
  { title: '行号', dataIndex: 'row', width: 80 },
  { title: '客户名称', dataIndex: 'name', width: 200 },
  { title: '错误信息', dataIndex: 'error', ellipsis: true, tooltip: true }
]

const handleDownloadTemplate = async () => {
  try {
    const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/customers/import-template`, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    })
    
    if (!response.ok) {
      throw new Error('下载失败')
    }
    
    const blob = await response.blob()
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = '客户导入模板.xlsx'
    link.click()
    window.URL.revokeObjectURL(url)
    
    Message.success('模板下载成功')
  } catch (error) {
    Message.error('下载模板失败')
  }
}

const handleFileChange = (fileList: any[]) => {
  if (fileList.length > 0) {
    selectedFile.value = fileList[0].file
  } else {
    selectedFile.value = null
  }
}

const handleUpload = async () => {
  if (!selectedFile.value) {
    Message.warning('请先选择文件')
    return
  }
  
  uploading.value = true
  currentStep.value = 1
  uploadProgress.value = 0
  
  // 模拟进度
  const progressInterval = setInterval(() => {
    uploadProgress.value = Math.min(uploadProgress.value + 10, 90)
  }, 200)
  
  try {
    const formData = new FormData()
    formData.append('file', selectedFile.value)
    
    const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/customers/import`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      },
      body: formData
    })
    
    clearInterval(progressInterval)
    uploadProgress.value = 100
    
    if (!response.ok) {
      throw new Error('导入失败')
    }
    
    const result = await response.json()
    const data = result.data
    
    successCount.value = data.imported_count || 0
    failedCount.value = data.failed_count || 0
    importErrors.value = data.errors || []
    importSuccess.value = failedCount.value === 0
    
    setTimeout(() => {
      currentStep.value = 2
    }, 500)
    
    if (importSuccess.value) {
      Message.success(`成功导入 ${successCount.value} 条客户数据`)
    } else {
      Message.warning(`导入完成，成功 ${successCount.value} 条，失败 ${failedCount.value} 条`)
    }
  } catch (error) {
    Message.error('导入失败，请重试')
    currentStep.value = 0
  } finally {
    uploading.value = false
  }
}

const handleBackToList = () => {
  router.push('/customers')
}

const handleReset = () => {
  currentStep.value = 0
  selectedFile.value = null
  uploadProgress.value = 0
  importSuccess.value = true
  successCount.value = 0
  failedCount.value = 0
  importErrors.value = []
  uploadRef.value?.clear()
}
</script>

<style scoped lang="scss">
.customer-import {
  padding: 24px;
}

.import-card {
  :deep(.arco-card-header) {
    border-bottom: 1px solid var(--color-border-2);
    padding: 16px 20px;
  }
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-title {
  font-size: 16px;
  font-weight: 500;
  color: var(--color-text-1);
}

.import-steps {
  margin-bottom: 32px;
  padding: 0 20px;
}

.import-content {
  padding: 0 20px 20px;
}

.step-content {
  min-height: 300px;
}

.upload-area {
  margin-bottom: 24px;
}

.upload-dragger {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
  text-align: center;
}

.upload-icon {
  font-size: 48px;
  color: var(--color-text-4);
  margin-bottom: 16px;
}

.upload-text {
  color: var(--color-text-2);
}

.upload-title {
  margin: 0;
  font-size: 14px;
  
  .highlight {
    color: var(--color-primary-light-4);
    font-weight: 500;
  }
}

.upload-hint {
  margin: 8px 0 0;
  font-size: 12px;
  color: var(--color-text-4);
}

.template-info {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px;
  margin-top: 16px;
  background: var(--color-bg-2);
  border-radius: 4px;
  color: var(--color-text-2);
  font-size: 13px;
}

.step-actions {
  display: flex;
  justify-content: center;
  gap: 16px;
  margin-top: 32px;
}

.uploading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 300px;
}

.loading-icon {
  font-size: 48px;
  color: var(--color-primary-light-4);
  margin-bottom: 16px;
}

.loading-text {
  font-size: 14px;
  color: var(--color-text-2);
  margin: 0;
}

.loading-hint {
  font-size: 12px;
  color: var(--color-text-4);
  margin: 8px 0 0;
}

.error-list {
  margin-top: 24px;
  border: 1px solid var(--color-border-3);
  border-radius: 4px;
  padding: 16px;
  background: var(--color-bg-2);
}

.error-title {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
  font-size: 14px;
  font-weight: 500;
  color: var(--color-warning);
}

.result-icon {
  font-size: 48px;
  
  &.success {
    color: var(--color-success);
  }
  
  &.warning {
    color: var(--color-warning);
  }
}
</style>
