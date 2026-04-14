<template>
  <div v-if="diagram" class="diagram-card">
    <div class="diagram-header">
      <strong>{{ diagram.title }}</strong>
      <div class="diagram-labels">
        <span v-for="label in diagram.labels" :key="label" class="diagram-tag">
          {{ label }}
        </span>
      </div>
    </div>

    <svg
      v-if="diagram.type === 'circle'"
      viewBox="0 0 220 150"
      class="diagram-svg"
      aria-label="圆形示意图"
    >
      <circle cx="110" cy="78" r="46" class="shape-fill" />
      <line x1="110" y1="78" x2="156" y2="78" class="shape-line dashed" />
      <line x1="64" y1="78" x2="156" y2="78" class="shape-line" />
      <text x="162" y="83" class="shape-text">r</text>
      <text x="104" y="64" class="shape-text">O</text>
    </svg>

    <svg
      v-else-if="diagram.type === 'rectangle'"
      viewBox="0 0 220 150"
      class="diagram-svg"
      aria-label="矩形示意图"
    >
      <rect x="48" y="36" width="124" height="76" rx="8" class="shape-fill" />
      <line x1="48" y1="120" x2="172" y2="120" class="shape-line" />
      <line x1="180" y1="36" x2="180" y2="112" class="shape-line" />
      <text x="104" y="138" class="shape-text">长</text>
      <text x="186" y="80" class="shape-text">宽</text>
    </svg>

    <svg
      v-else
      viewBox="0 0 220 150"
      class="diagram-svg"
      aria-label="三角形示意图"
    >
      <polygon points="110,24 40,116 180,116" class="shape-fill" />
      <line x1="110" y1="24" x2="40" y2="116" class="shape-line" />
      <line x1="110" y1="24" x2="180" y2="116" class="shape-line" />
      <line x1="40" y1="116" x2="180" y2="116" class="shape-line" />
      <text x="108" y="18" class="shape-text">A</text>
      <text x="28" y="128" class="shape-text">B</text>
      <text x="184" y="128" class="shape-text">C</text>
    </svg>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { getDiagramData } from "../utils/mathDiagram";

const props = defineProps<{
  question: string;
}>();

const diagram = computed(() => getDiagramData(props.question));
</script>

<style scoped>
.diagram-card {
  margin: 12px 0 18px;
  padding: 14px;
  border-radius: 14px;
  background: linear-gradient(180deg, #f8fbff 0%, #eef6ff 100%);
  border: 1px solid #dbe8f6;
}

.diagram-header {
  display: flex;
  gap: 10px;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
}

.diagram-labels {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.diagram-tag {
  padding: 4px 10px;
  border-radius: 999px;
  background: #fff;
  color: #36506b;
  font-size: 12px;
}

.diagram-svg {
  width: 100%;
  max-width: 320px;
  height: auto;
  display: block;
  margin-top: 12px;
}

.shape-fill {
  fill: rgba(32, 128, 240, 0.1);
  stroke: #2080f0;
  stroke-width: 3;
}

.shape-line {
  stroke: #f08c00;
  stroke-width: 3;
}

.shape-line.dashed {
  stroke-dasharray: 5 4;
}

.shape-text {
  fill: #22354a;
  font-size: 14px;
  font-weight: 700;
}
</style>
