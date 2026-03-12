<template>
  <div class="page">
    <div class="container">
      <h1>AI 数学辅导老师</h1>
      <div class="student-bar">
  <select
    v-model="currentStudentId"
    class="student-select"
    @change="handleStudentChange"
  >
    <option v-for="item in studentList" :key="item.id" :value="item.id">
      {{ item.name }}
    </option>
  </select>

  <input
    v-model="newStudentName"
    class="student-input"
    placeholder="输入新学生姓名"
  />

  <button class="retry-btn" @click="handleCreateStudent">
    新增学生
  </button>

  <button class="wrong-btn" @click="handleExportReport">
  导出练习单
</button>
</div>

      <div class="tabs">
        <button
          :class="['tab-btn', activeTab === 'solve' ? 'active' : '']"
          @click="activeTab = 'solve'"
        >
          题目解析
        </button>
        <button
          :class="['tab-btn', activeTab === 'history' ? 'active' : '']"
          @click="switchToHistory"
        >
          历史记录
        </button>
        <button
          :class="['tab-btn', activeTab === 'wrong' ? 'active' : '']"
          @click="switchToWrong"
        >
          错题本
        </button>
        <button
        :class="['tab-btn', activeTab === 'report' ? 'active' : '']"
        @click="switchToReport"
        >
        学习报告
        </button>
        <button
        :class="['tab-btn', activeTab === 'suggestion' ? 'active' : '']"
        @click="switchToSuggestion"
        >
        学习建议
</button>
      </div>

      <template v-if="activeTab === 'solve'">
        <div class="upload-area">
        <label class="upload-btn">
            {{ imageLoading ? '识别中...' : '上传题目图片' }}
            <input
            type="file"
            accept="image/*"
            class="file-input"
            :disabled="imageLoading"
            @change="handleImageChange"
            />
        </label>
        </div>
        <textarea
          v-model="question"
          class="question-input"
          placeholder="请输入一道数学题，例如：解方程 3x + 5 = 11"
        />

        <button class="submit-btn" @click="handleSubmit" :disabled="loading">
          {{ loading ? '解析中...' : '开始解析' }}
        </button>

       <div v-if="result" class="result-card">
        <div class="card-header">
            <h2>本次解析结果</h2>

            <div class="card-actions">
            <button
                class="retry-btn"
                @click="handleRegenerateQuestion(result.id)"
            >
                {{ regenerateLoadingMap[result.id] ? '生成中...' : '再练一题' }}
            </button>

            <button
                class="wrong-btn"
                @click="toggleWrong(result)"
            >
                {{ result.is_wrong ? '取消错题' : '加入错题本' }}
            </button>
            </div>
        </div>

        <h3>题目</h3>
        <p>{{ result.question }}</p>

        <h3>答案</h3>
        <p>{{ result.answer }}</p>

        <h3>步骤解析</h3>
        <ol>
            <li v-for="(step, index) in result.steps" :key="index">
            {{ step }}
            </li>
        </ol>

        <h3>知识点</h3>
        <ul>
            <li v-for="(kp, index) in result.knowledge_points" :key="index">
            {{ kp }}
            </li>
        </ul>

        <h3>相似题</h3>
        <p>{{ result.similar_question }}</p>

        <div
            v-if="regeneratedMap[result.id]"
            class="regenerated-box"
        >
            <h3>再练一题</h3>
            <p>{{ regeneratedMap[result.id].question }}</p>

            <h3>答案</h3>
            <p>{{ regeneratedMap[result.id].answer }}</p>

            <h3>步骤解析</h3>
            <ol>
            <li
                v-for="(step, idx) in regeneratedMap[result.id].steps"
                :key="idx"
            >
                {{ step }}
            </li>
            </ol>
        </div>
        </div>

        <div class="practice-panel">
        <h2>按知识点生成练习题</h2>
        <div class="practice-form">
            <input
            v-model="practiceKnowledge"
            class="practice-input"
            placeholder="请输入知识点，例如：一元一次方程"
            />
            <button class="submit-btn" @click="handleGeneratePractice" :disabled="practiceLoading">
            {{ practiceLoading ? '生成中...' : '生成练习题' }}
            </button>
        </div>

  <div v-if="practiceList.length" class="practice-list">
    <div v-for="(item, index) in practiceList" :key="index" class="result-card">
      <h3>练习题 {{ index + 1 }}</h3>
      <p>{{ item.question }}</p>

      <h3>答案</h3>
      <p>{{ item.answer }}</p>

      <h3>步骤解析</h3>
      <ol>
        <li v-for="(step, idx) in item.steps" :key="idx">{{ step }}</li>
      </ol>
    </div>
  </div>
</div>
      </template>

      <template v-else-if="activeTab === 'history'">
        <div v-if="historyList.length === 0" class="empty">暂无历史记录</div>

        <div v-for="item in historyList" :key="item.id" class="result-card">
            <div class="card-header">
                <h2>记录 #{{ item.id }}</h2>
                <div class="card-actions">
                <button class="retry-btn" @click="handleRegenerateQuestion(item.id)">
                    {{ regenerateLoadingMap[item.id] ? '生成中...' : '再练一题' }}
                </button>
                <button class="wrong-btn" @click="toggleWrong(item)">
                    {{ item.is_wrong ? '取消错题' : '加入错题本' }}
                </button>
                </div>
            </div>

            <h3>题目</h3>
            <p>{{ item.question }}</p>

            <h3>答案</h3>
            <p>{{ item.answer }}</p>

            <h3>步骤解析</h3>
            <ol>
                <li v-for="(step, idx) in item.steps" :key="idx">{{ step }}</li>
            </ol>

            <h3>知识点</h3>
            <ul>
                <li v-for="(kp, idx) in item.knowledge_points" :key="idx">{{ kp }}</li>
            </ul>

            <h3>相似题</h3>
            <p>{{ item.similar_question }}</p>

            <div v-if="regeneratedMap[item.id]" class="regenerated-box">
                <h3>再练一题</h3>
                <p>{{ regeneratedMap[item.id].question }}</p>

                <h3>答案</h3>
                <p>{{ regeneratedMap[item.id].answer }}</p>

                <h3>步骤解析</h3>
                <ol>
                <li v-for="(step, idx) in regeneratedMap[item.id].steps" :key="idx">
                    {{ step }}
                </li>
                </ol>
            </div>
            </div>
      </template>

      <template v-else-if="activeTab === 'wrong'">
        <div v-if="wrongList.length === 0" class="empty">暂无错题</div>

        <div v-for="item in wrongList" :key="item.id" class="result-card">
          <div class="card-header">
            <h2>错题 #{{ item.id }}</h2>
            <button class="wrong-btn" @click="toggleWrong(item)">
              取消错题
            </button>
          </div>

          <h3>题目</h3>
          <p>{{ item.question }}</p>

          <h3>答案</h3>
          <p>{{ item.answer }}</p>

          <h3>步骤解析</h3>
          <ol>
            <li v-for="(step, idx) in item.steps" :key="idx">{{ step }}</li>
          </ol>

          <h3>知识点</h3>
          <ul>
            <li v-for="(kp, idx) in item.knowledge_points" :key="idx">{{ kp }}</li>
          </ul>

          <h3>相似题</h3>
          <p>{{ item.similar_question }}</p>
        </div>
      </template>

      <template  v-else-if="activeTab === 'report'">
  <div v-if="reportLoading" class="empty">学习报告加载中...</div>

  <div v-else-if="learningReport" class="report-panel">
    <div class="report-summary">
      <div class="summary-card">
        <div class="summary-label">总题数</div>
        <div class="summary-value">{{ learningReport.total_count }}</div>
      </div>

      <div class="summary-card">
        <div class="summary-label">错题数</div>
        <div class="summary-value">{{ learningReport.wrong_count }}</div>
      </div>

      <div class="summary-card">
        <div class="summary-label">正确数</div>
        <div class="summary-value">{{ learningReport.correct_count }}</div>
      </div>

      <div class="summary-card">
        <div class="summary-label">错题率</div>
        <div class="summary-value">{{ learningReport.wrong_rate }}%</div>
      </div>
    </div>

    <div class="result-card">
      <h2>高频知识点 Top 5</h2>
      <div v-if="learningReport.top_knowledge_points.length === 0" class="empty">
        暂无知识点统计
      </div>
      <ul v-else class="stat-list">
        <li
          v-for="(item, index) in learningReport.top_knowledge_points"
          :key="index"
          class="stat-item"
        >
          <span>{{ item.name }}</span>
          <strong>{{ item.count }}</strong>
        </li>
      </ul>
    </div>

    <div class="result-card">
      <h2>最近练习</h2>
      <div v-if="learningReport.recent_records.length === 0" class="empty">
        暂无记录
      </div>

      <div
        v-for="item in learningReport.recent_records"
        :key="item.id"
        class="recent-item"
      >
        <div class="recent-header">
          <span>题目 #{{ item.id }}</span>
          <span :class="['status-tag', item.is_wrong ? 'wrong' : 'correct']">
            {{ item.is_wrong ? '错题' : '正常' }}
          </span>
        </div>

        <div class="recent-question">{{ item.question }}</div>

        <div class="recent-kp">
          <span
            v-for="(kp, idx) in item.knowledge_points"
            :key="idx"
            class="kp-tag"
          >
            {{ kp }}
          </span>
        </div>
      </div>
    </div>
  </div>
        </template>

        <template v-else>
  <div v-if="suggestionLoading" class="empty">学习建议加载中...</div>

  <div v-else-if="studySuggestion" class="report-panel">
    <div class="result-card">
      <h2>整体学习建议</h2>
      <p>{{ studySuggestion.overall_suggestion }}</p>
    </div>

    <div class="result-card">
      <h2>薄弱知识点分析</h2>

      <div v-if="studySuggestion.weak_knowledge_points.length === 0" class="empty">
        暂无薄弱知识点
      </div>

      <div
        v-for="(item, index) in studySuggestion.weak_knowledge_points"
        :key="index"
        class="weak-item"
      >
        <div class="weak-header">
          <strong>{{ item.name }}</strong>
          <span class="weak-rate">错误率 {{ item.wrong_rate }}%</span>
        </div>

        <div class="weak-meta">
          错误 {{ item.wrong_count }} 次 / 共出现 {{ item.total_count }} 次
        </div>

        <div class="weak-suggestion">
          {{ item.suggestion }}
        </div>

        <button
          class="retry-btn"
          @click="
            practiceKnowledge = item.name;
            activeTab = 'solve';
            handleGeneratePractice();
          "
        >
          生成该知识点练习题
        </button>
      </div>
    </div>
  </div>
</template>
    </div>
  </div>
</template>
<script setup lang="ts">
import { ref, onMounted } from 'vue'
import {
  solveMathQuestion,
  solveMathImage,
  getHistoryList,
  getWrongQuestionList,
  markWrongQuestion,
  generatePracticeByKnowledge,
  regenerateQuestion,
  getLearningReport,
  getStudySuggestion,
  getStudentList,
  createStudent,
  getExportReportUrl,
  type SolveResponse,
  type HistoryItem,
  type PracticeQuestionItem,
  type LearningReportResponse,
  type StudySuggestionResponse,
  type StudentItem,
} from './api/math'
const question = ref('')
const loading = ref(false)
const result = ref<(SolveResponse & { question: string }) | null>(null)

const activeTab = ref<'solve' | 'history' | 'wrong' | 'report' | 'suggestion'>('solve')
const historyList = ref<HistoryItem[]>([])
const wrongList = ref<HistoryItem[]>([])
const imageLoading = ref(false)
const practiceKnowledge = ref('')
const practiceLoading = ref(false)
const practiceList = ref<PracticeQuestionItem[]>([])

const regenerateLoadingMap = ref<Record<number, boolean>>({})
const regeneratedMap = ref<Record<number, PracticeQuestionItem>>({})
const reportLoading = ref(false)
const learningReport = ref<LearningReportResponse | null>(null)

const studentList = ref<StudentItem[]>([])
const currentStudentId = ref(1)
const newStudentName = ref('')

const suggestionLoading = ref(false)
const studySuggestion = ref<StudySuggestionResponse | null>(null)

const loadHistory = async () => {
  const { data } = await getHistoryList(currentStudentId.value)
  historyList.value = data
}

const loadWrongList = async () => {
  const { data } = await getWrongQuestionList(currentStudentId.value)
  wrongList.value = data
}

const handleSubmit = async () => {
  if (!question.value.trim()) return

  loading.value = true
  try {
    const currentQuestion = question.value.trim()
    const { data } = await solveMathQuestion(
  { question: currentQuestion },
  currentStudentId.value
)

    console.log('solve result:', data)

    result.value = {
      ...data,
      question: currentQuestion,
    }

    activeTab.value = 'solve'

    // 历史记录 / 错题本刷新失败，不影响主结果展示
    const refreshResults = await Promise.allSettled([
      loadHistory(),
      loadWrongList(),
    ])

    refreshResults.forEach((item) => {
      if (item.status === 'rejected') {
        console.error('刷新列表失败:', item.reason)
      }
    })

      await loadReport()
    await loadStudySuggestion()
  } catch (error: any) {
    console.error('解析失败:', error)
    alert(error?.response?.data?.detail || '解析失败，请检查后端日志')
  } finally {
    loading.value = false
  }
}

const toggleWrong = async (item: HistoryItem | (SolveResponse & { question: string })) => {
  try {
    const { data } = await markWrongQuestion(item.id, !item.is_wrong)

    if (result.value && result.value.id === item.id) {
      result.value = {
        ...result.value,
        is_wrong: data.is_wrong,
      }
    }

    await loadHistory()
    await loadWrongList()
      await loadReport()
    await loadStudySuggestion()
  } catch (error) {
    console.error(error)
    alert('更新错题状态失败')
  }
}

const switchToHistory = async () => {
  activeTab.value = 'history'
  await loadHistory()
}

const switchToWrong = async () => {
  activeTab.value = 'wrong'
  await loadWrongList()
}

const handleImageChange = async (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (!file) return

  imageLoading.value = true
  try {
    const { data } = await solveMathImage(file, currentStudentId.value)

    result.value = {
      ...data,
      question: data.question,
    }

    activeTab.value = 'solve'

    const refreshResults = await Promise.allSettled([
      loadHistory(),
      loadWrongList(),
    ])

    refreshResults.forEach((item) => {
      if (item.status === 'rejected') {
        console.error('刷新列表失败:', item.reason)
      }
    })

      await loadReport()
    await loadStudySuggestion()
  } catch (error: any) {
    console.error('图片解析失败:', error)
    alert(error?.response?.data?.detail || '图片解析失败，请检查后端日志')
  } finally {
    imageLoading.value = false
    target.value = ''
  }
}

const handleGeneratePractice = async () => {
  if (!practiceKnowledge.value.trim()) return

  practiceLoading.value = true
  try {
    const { data } = await generatePracticeByKnowledge(practiceKnowledge.value, 3)
    practiceList.value = data.questions
  } catch (error: any) {
    console.error('生成练习题失败:', error)
    alert(error?.response?.data?.detail || '生成练习题失败')
  } finally {
    practiceLoading.value = false
  }
}

const handleRegenerateQuestion = async (id: number) => {
  regenerateLoadingMap.value[id] = true
  try {
    const { data } = await regenerateQuestion(id)
    regeneratedMap.value[id] = {
      question: data.question,
      answer: data.answer,
      steps: data.steps,
    }
  } catch (error: any) {
    console.error('再练一题失败:', error)
    alert(error?.response?.data?.detail || '再练一题失败')
  } finally {
    regenerateLoadingMap.value[id] = false
  }
}

const loadReport = async () => {
  reportLoading.value = true
  try {
    const { data } = await getLearningReport(currentStudentId.value)
    learningReport.value = data
  } catch (error: any) {
    console.error('加载学习报告失败:', error)
    alert(error?.response?.data?.detail || '加载学习报告失败')
  } finally {
    reportLoading.value = false
  }
}

const switchToReport = async () => {
  activeTab.value = 'report'
  await loadReport()
}

const loadStudents = async () => {
  const { data } = await getStudentList()
  studentList.value = data
  if (!data.find(item => item.id === currentStudentId.value) && data.length) {
    currentStudentId.value = data[0].id
  }
}

const handleCreateStudent = async () => {
  const name = newStudentName.value.trim()
  if (!name) return

  try {
    const { data } = await createStudent(name)
    newStudentName.value = ''
    await loadStudents()
    currentStudentId.value = data.id
    await refreshAllStudentData()
  } catch (error: any) {
    console.error('创建学生失败:', error)
    alert(error?.response?.data?.detail || '创建学生失败')
  }
}

const refreshAllStudentData = async () => {
  await Promise.all([
    loadHistory(),
    loadWrongList(),
    loadReport(),
    loadStudySuggestion(),
  ])
}

const handleStudentChange = async () => {
  result.value = null
  practiceList.value = []
  regeneratedMap.value = {}
  await refreshAllStudentData()
}

const loadStudySuggestion = async () => {
  suggestionLoading.value = true
  try {
    const { data } = await getStudySuggestion(currentStudentId.value)
    studySuggestion.value = data
  } catch (error: any) {
    console.error('加载学习建议失败:', error)
    alert(error?.response?.data?.detail || '加载学习建议失败')
  } finally {
    suggestionLoading.value = false
  }
}

const switchToSuggestion = async () => {
  activeTab.value = 'suggestion'
  await loadStudySuggestion()
}

const handleExportReport = () => {
  const url = getExportReportUrl(currentStudentId.value)
  window.open(url, '_blank')
}

onMounted(async () => {
await loadStudents()
  await refreshAllStudentData()
  await loadHistory()
  await loadWrongList()
  await loadReport()
  await loadStudySuggestion()
})
</script>

<style scoped>
.page {
  min-height: 100vh;
  background: #f5f7fa;
  padding: 40px 16px;
}
.container {
  max-width: 900px;
  margin: 0 auto;
  background: #fff;
  padding: 24px;
  border-radius: 12px;
}
.tabs {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
}
.tab-btn {
  padding: 8px 16px;
  border: 1px solid #ddd;
  background: #fff;
  border-radius: 8px;
  cursor: pointer;
}
.tab-btn.active {
  background: #18a058;
  color: #fff;
  border-color: #18a058;
}
.question-input {
  width: 100%;
  min-height: 140px;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 8px;
  resize: vertical;
  font-size: 16px;
  box-sizing: border-box;
}
.submit-btn {
  margin-top: 16px;
  padding: 10px 18px;
  border: none;
  background: #18a058;
  color: #fff;
  border-radius: 8px;
  cursor: pointer;
}
.result-card {
  margin-top: 24px;
  padding: 20px;
  background: #fafafa;
  border-radius: 8px;
}
.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}
.wrong-btn {
  padding: 8px 14px;
  border: none;
  background: #f0a020;
  color: #fff;
  border-radius: 8px;
  cursor: pointer;
}
.empty {
  padding: 32px 0;
  text-align: center;
  color: #999;
}
.upload-area {
  margin-bottom: 16px;
}

.upload-btn {
  display: inline-flex;
  align-items: center;
  padding: 10px 16px;
  background: #2080f0;
  color: #fff;
  border-radius: 8px;
  cursor: pointer;
}

.file-input {
  display: none;
}
.card-actions {
  display: flex;
  gap: 8px;
}

.retry-btn {
  padding: 8px 14px;
  border: none;
  background: #2080f0;
  color: #fff;
  border-radius: 8px;
  cursor: pointer;
}

.practice-panel {
  margin-top: 32px;
}

.practice-form {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
}

.practice-input {
  flex: 1;
  height: 40px;
  padding: 0 12px;
  border: 1px solid #ddd;
  border-radius: 8px;
  outline: none;
}

.practice-list {
  margin-top: 16px;
}

.regenerated-box {
  margin-top: 16px;
  padding: 16px;
  background: #f0f7ff;
  border-radius: 8px;
}
.report-panel {
  margin-top: 24px;
}

.report-summary {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.summary-card {
  padding: 20px;
  background: #fafafa;
  border-radius: 12px;
  text-align: center;
}

.summary-label {
  color: #666;
  font-size: 14px;
  margin-bottom: 8px;
}

.summary-value {
  font-size: 28px;
  font-weight: 700;
  color: #18a058;
}

.stat-list {
  padding: 0;
  margin: 0;
  list-style: none;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  padding: 12px 0;
  border-bottom: 1px solid #eee;
}

.recent-item {
  padding: 16px 0;
  border-bottom: 1px solid #eee;
}

.recent-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.recent-question {
  margin-bottom: 10px;
  color: #333;
}

.recent-kp {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.kp-tag {
  display: inline-block;
  padding: 4px 10px;
  background: #f3f3f3;
  border-radius: 999px;
  font-size: 12px;
}

.status-tag {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 12px;
  color: #fff;
}

.status-tag.wrong {
  background: #d03050;
}

.status-tag.correct {
  background: #18a058;
}

.weak-item {
  padding: 16px 0;
  border-bottom: 1px solid #eee;
}

.weak-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.weak-rate {
  color: #d03050;
  font-weight: 600;
}

.weak-meta {
  color: #666;
  font-size: 14px;
  margin-bottom: 8px;
}

.weak-suggestion {
  margin-bottom: 12px;
  color: #333;
  line-height: 1.7;
}

.student-bar {
  display: flex;
  gap: 12px;
  align-items: center;
  margin-bottom: 20px;
}

.student-select,
.student-input {
  height: 40px;
  padding: 0 12px;
  border: 1px solid #ddd;
  border-radius: 8px;
  background: #fff;
  outline: none;
}
</style>