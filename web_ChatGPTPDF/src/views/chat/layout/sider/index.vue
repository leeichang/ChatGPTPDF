<script setup lang="ts">
import type { CSSProperties } from "vue";
import { computed, ref, watch } from "vue";
import {
  NButton,
  NIcon,
  NLayoutSider,
  NSelect,
  NSpace,
  NText,
  NUpload,
  NUploadDragger,
} from "naive-ui";
import { ArchiveOutline as ArchiveIcon } from "@vicons/ionicons5";
import List from "./List.vue";
import Footer from "./Footer.vue";
import { useAppStore, useChatStore } from "@/store";
import { useBasicLayout } from "@/hooks/useBasicLayout";
import { PromptStore } from "@/components/common";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;
const UploadUrl = API_BASE_URL + "api/ChatGPTPDF/File/perform_create/";
const appStore = useAppStore();
const chatStore = useChatStore();

const { isMobile } = useBasicLayout();
const show = ref(false);

const collapsed = computed(() => appStore.siderCollapsed);

const selected_pdf_ids = ref([]);
const options = ref([
  {
    value: "30c6a550-1a81-49f8-a2e9-40de32394a99",
    label:
      "\u5408\u6D41\u5340\u584A\u93C8\u4F9B\u61C9\u93C8\u91D1\u878D\u7C21\u4ECB-v1r0-20221118 V2.pdf",
  },
  {
    value: "a73874cd-03b2-404b-beef-3206b66549a6",
    label: "\u8BBE\u8BA1\u6A21\u5F0F.pdf",
  },
  {
    value: "c979c3cf-735c-4347-a2e4-63dfb8daa27b",
    label: "\u6B63\u7F8E\u96C6\u5718\u7C21\u4ECB\u518A.pdf",
  },
  {
    value: "96a1552a-abd6-4722-8344-8d1e6f2b6e4a",
    label:
      "\u56FD\u9645\u80FD\u6E90\u7F72-\u53EF\u6301\u7EED\u7ECF\u6D4E\u5B9E\u60E0\u7684\u5236\u51B7\u6BCF\u5E74\u53EF\u633D\u6551\u6570\u4E07\u4EBA\u7684\u751F\u547D\u82F1-2023.3.pdf",
  },
]);
function handleAdd() {
  chatStore.addHistory({ title: "New Chat", uuid: Date.now(), isEdit: false });
  if (isMobile.value) appStore.setSiderCollapsed(true);
}

function handleUpdateCollapsed() {
  appStore.setSiderCollapsed(!collapsed.value);
}

const getMobileClass = computed<CSSProperties>(() => {
  if (isMobile.value) {
    return {
      position: "fixed",
      zIndex: 50,
    };
  }
  return {};
});

const mobileSafeArea = computed(() => {
  if (isMobile.value) {
    return {
      paddingBottom: "env(safe-area-inset-bottom)",
    };
  }
  return {};
});

watch(
  isMobile,
  (val) => {
    appStore.setSiderCollapsed(val);
  },
  {
    immediate: true,
    flush: "post",
  }
);
</script>

<template>
  <NLayoutSider
    :collapsed="collapsed"
    :collapsed-width="0"
    :width="260"
    :show-trigger="isMobile ? false : 'arrow-circle'"
    collapse-mode="transform"
    position="absolute"
    bordered
    :style="getMobileClass"
    @update-collapsed="handleUpdateCollapsed"
  >
    <div class="flex flex-col h-full" :style="mobileSafeArea">
      <main class="flex flex-col flex-1 min-h-0">
        <div class="p-4">
          <NButton dashed block @click="handleAdd">
            {{ $t("chat.newChatButton") }}
          </NButton>
        </div>
        <div class="flex-1 min-h-0 pb-4 overflow-hidden">
          <List />
        </div>
        <div>
          <NSpace vertical>
            <NSelect
              v-model:value="selected_pdf_ids"
              multiple
              filterable
              :options="options"
              :consistent-menu-width="false"
              placeholder="PDF to Q&A or talk to ChatGPT"
            />
            <!-- <NTooltip>
              <template #trigger> -->
            <NUpload
              multiple
              directory-dnd
              :action="UploadUrl"
              :max="5"
              style="height: 120px"
            >
              <NUploadDragger style="height: 125px">
                <div style="margin-bottom: 5px">
                  <NIcon size="36" :depth="3">
                    <ArchiveIcon />
                  </NIcon>
                </div>
                <NText style="font-size: 14px">
                  Click or drag a file to this area to upload Q&A PDF file
                </NText>
              </NUploadDragger>
            </NUpload>
            <!-- </template>
              <span
                >Uploading sensitive information is strictly prohibited. For
                example For example, customers providing production-related
                information, financial information, R&D information</span
              >
            </NTooltip> -->
          </NSpace>
        </div>
        <!-- <div class="p-4">
          <NButton block @click="show = true">
            {{ $t("store.siderButton") }}
          </NButton>
        </div> -->
      </main>
      <Footer />
    </div>
  </NLayoutSider>
  <template v-if="isMobile">
    <div
      v-show="!collapsed"
      class="fixed inset-0 z-40 bg-black/40"
      @click="handleUpdateCollapsed"
    />
  </template>
  <PromptStore v-model:visible="show" />
</template>
