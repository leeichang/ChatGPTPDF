<script setup lang="ts">
import type { CSSProperties } from "vue";
import { computed, ref, watch, onMounted } from "vue";
import {
  NButton,
  NIcon,
  NLayoutSider,
  NSelect,
  NSpace,
  NText,
  NUpload,
  NUploadDragger,
  UploadFileInfo,
  useMessage,
} from "naive-ui";
import { ArchiveOutline as ArchiveIcon } from "@vicons/ionicons5";
import List from "./List.vue";
import Footer from "./Footer.vue";
import { useAppStore, useChatStore } from "@/store";
import { useBasicLayout } from "@/hooks/useBasicLayout";
import { PromptStore } from "@/components/common";
import { getMyFiles, set_qa_documents } from "@/api/user";
import { options } from "@/typings/global";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;
const UploadUrl = `${API_BASE_URL}api/ChatGPTPDF/File/perform_create/`;
const appStore = useAppStore();
const chatStore = useChatStore();

const { isMobile } = useBasicLayout();
const show = ref(false);

const collapsed = computed(() => appStore.siderCollapsed);

const selected_pdf_ids = ref([]);
const options = ref<options[]>([]);

const message = useMessage();
const uploadRef = ref(null);
const fileList = ref([]);

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

async function fetchData() {
  try {
    const userId = 1; // 替換為您的 userId 參數值
    const files = await getMyFiles(userId); // 傳入 userId
    options.value = [];
    //檔案逐筆處理
    files.forEach((file) => {
      const firstUnderscoreIndex = file.file_name.indexOf("_"); // 找到第一個底線的索引
      const lastDotIndex = file.file_name.lastIndexOf("."); // 找到最後一個句點的索引
      const newName: string =
        file.file_name.substring(0, firstUnderscoreIndex) +
        file.file_name.substring(lastDotIndex); // 取底線前的內容加上最後一個句點以後的文字當副檔名
      options.value.push({
        value: file.id,
        label: newName,
      });
    });
  } catch (error) {
    console.error("Failed to fetch data:", error);
  }
}

// const handleSelectChange = () => {
//   const value = selected_pdf_ids.value;
//   set_qa_documents(value).then((response) => {
//     message.success("setting successfully");
//   });
//   if (isArray(value)) {
//     this.$refs.pdfViewer.downloadfile(value[0]);
//   } else {
//     this.$refs.pdfViewer.downloadfile(value);
//   }
// };

const handleFinish = ({
  file,
  event,
}: {
  file: UploadFileInfo;
  event?: ProgressEvent;
}) => {
  message.success("Upload successfully");
  fetchData();
  set_qa_documents(selected_pdf_ids.value).then((response) => {
    message.success("setting successfully");
  });
  appStore.setSelectedKeys(selected_pdf_ids.value);
};

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

watch(selected_pdf_ids, (newValue) => {
  if (newValue.length > 0) {
    set_qa_documents(newValue).then((response) => {
      message.success("setting successfully");
    });
    appStore.setSelectedKeys(newValue);
  }
});

onMounted(() => {
  fetchData();
});
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
              ref="uploadRef"
              v-model:fileList="fileList"
              multiple
              directory-dnd
              :action="UploadUrl"
              :max="5"
              style="height: 170px;"
              @finish="handleFinish"
            >
              <NUploadDragger style="height: 125px;">
                <div style="margin-bottom: 5px;">
                  <NIcon size="36" :depth="3">
                    <ArchiveIcon />
                  </NIcon>
                </div>
                <NText style="font-size: 14px;">
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
