<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from "vue";
import { useRoute } from "vue-router";
import { storeToRefs } from "pinia";
import {
  NAutoComplete,
  NButton,
  NInput,
  useDialog,
  useMessage,
} from "naive-ui";
import html2canvas from "html2canvas";
import { Message } from "./components";
import { useScroll } from "./hooks/useScroll";
import { useChat } from "./hooks/useChat";
import { useCopyCode } from "./hooks/useCopyCode";
import { useUsingContext } from "./hooks/useUsingContext";
import HeaderComponent from "./components/Header/index.vue";
import { HoverButton, SvgIcon } from "@/components/common";
import { useBasicLayout } from "@/hooks/useBasicLayout";
import { useChatStore, usePromptStore, useAppStore } from "@/store";
import { fetchChatAPIProcess } from "@/api";
import { last_chat_summary } from "@/api/user";
import { t } from "@/locales";
import PdfViewer from "../pdfviewer/index.vue";
import LoadingAnimation from "vue3-loading-overlay";
import "vue3-loading-overlay/dist/vue3-loading-overlay.css";
import { embedding_history } from "@/api/user";
// import { userInfo } from "os";

const isLoading = ref(false);
const fullPage = ref(false);
const opacity = ref(0.7);
let controller = new AbortController();

const openLongReply = import.meta.env.VITE_GLOB_OPEN_LONG_REPLY === "true";

const route = useRoute();
const dialog = useDialog();
const ms = useMessage();

const chatStore = useChatStore();

useCopyCode();

const { isMobile } = useBasicLayout();
const {
  addChat,
  updateChat,
  updateChatSome,
  getChatByUuidAndIndex,
} = useChat();
const { scrollRef, scrollToBottom } = useScroll();
const { usingContext, toggleUsingContext } = useUsingContext();

const { uuid } = route.params as { uuid: string };

const dataSources = computed(() => chatStore.getChatByUuid(+uuid));
const conversationList = computed(() =>
  dataSources.value.filter((item) => !item.inversion && !item.error)
);

const prompt = ref<string>("");
const loading = ref<boolean>(false);

// 添加PromptStore
const promptStore = usePromptStore();
// 使用storeToRefs，保证store修改后，联想部分能够重新渲染
const { promptList: promptTemplate } = storeToRefs<any>(promptStore);
const appStore = useAppStore();
const { loading: chatLoading, foldPdf: globalFoldPdf } = storeToRefs(appStore);
//處理左右滑動
const foldPdf = ref(globalFoldPdf.value);
const leftWidth = ref(50);
const rightWidth = ref(50);
const pdfScale = ref(1);

// interface PdfViewerRef {
//   downloadfile: (id: number) => void;
// }

const pdfViewer = ref<typeof PdfViewer | null>(null);

const startResize = (event: MouseEvent) => {
  const startX = event.pageX;
  console.log("startX", startX);
  const startLeftWidth = leftWidth.value;
  console.log("leftWidth", startLeftWidth);
  const startRightWidth = rightWidth.value;
  console.log("leftWidth", startRightWidth);

  const onMouseMove = (event: MouseEvent) => {
    const diffX = event.pageX - startX;
    leftWidth.value = startLeftWidth + (diffX / window.innerWidth) * 100;
    rightWidth.value = startRightWidth - (diffX / window.innerWidth) * 100;
    console.log("leftWidth", leftWidth.value);
    console.log("rightWidth", rightWidth.value);
    pdfScale.value = leftWidth.value / 50;
    console.log("pdfScale", pdfScale.value);
  };

  const onMouseUp = () => {
    window.removeEventListener("mousemove", onMouseMove);
    window.removeEventListener("mouseup", onMouseUp);
  };

  window.addEventListener("mousemove", onMouseMove);
  window.addEventListener("mouseup", onMouseUp);
};

watch(
  () => chatLoading.value,
  (newVal) => {
    isLoading.value = newVal;
  }
);

const onCancel = () => {
  //console.log("User cancelled the loader.");
  //because the props is single flow direction, you need to set isLoading status normally.
  isLoading.value = false;
};

function handleSubmit() {
  onConversation();
}

async function onConversation() {
  let message = prompt.value;

  if (loading.value) return;

  if (!message || message.trim() === "") return;

  controller = new AbortController();

  addChat(+uuid, {
    dateTime: new Date().toLocaleString(),
    text: message,
    inversion: true,
    error: false,
    conversationOptions: null,
    requestOptions: { prompt: message, options: null },
  });
  scrollToBottom();

  loading.value = true;
  prompt.value = "";

  let options: Chat.ConversationRequest = {};
  const lastContext =
    conversationList.value[conversationList.value.length - 1]
      ?.conversationOptions;

  if (lastContext && usingContext.value) options = { ...lastContext };

  addChat(+uuid, {
    dateTime: new Date().toLocaleString(),
    text: "",
    loading: true,
    inversion: false,
    error: false,
    conversationOptions: null,
    requestOptions: { prompt: message, options: { ...options } },
  });
  scrollToBottom();

  try {
    let lastText = "";
    const fetchChatAPIOnce = async () => {
      //console.log("message", message);
      //console.log("options", options);
      //console.log("signal", controller.signal);
      await fetchChatAPIProcess<Chat.ConversationResponse>({
        prompt: message,
        options,
        signal: controller.signal,
        onDownloadProgress: ({ event }) => {
          const xhr = event.target;
          const { responseText } = xhr;
          // Always process the final line
          const lastIndex = responseText.lastIndexOf("\n");
          let chunk = responseText;
          if (lastIndex !== -1) chunk = responseText.substring(lastIndex);
          try {
            const data = JSON.parse(chunk);
            updateChat(+uuid, dataSources.value.length - 1, {
              dateTime: new Date().toLocaleString(),
              text: lastText + data.text ?? "",
              inversion: data.inversion ?? false,
              error: false,
              loading: false,
              conversationOptions: {
                conversationId: data.conversationId,
                parentMessageId: data.id,
              },
              requestOptions: { prompt: message, options: { ...options } },
            });

            if (
              openLongReply &&
              data.detail.choices[0].finish_reason === "length"
            ) {
              options.parentMessageId = data.id;
              lastText = data.text;
              message = "";
              return fetchChatAPIOnce();
            }

            scrollToBottom();
          } catch (error) {
            //
          }
        },
      });
    };

    await fetchChatAPIOnce();
  } catch (error: any) {
    const errorMessage = error?.message ?? t("common.wrong");

    if (error.message === "canceled") {
      updateChatSome(+uuid, dataSources.value.length - 1, {
        loading: false,
      });
      scrollToBottom();
      return;
    }

    const currentChat = getChatByUuidAndIndex(
      +uuid,
      dataSources.value.length - 1
    );

    if (currentChat?.text && currentChat.text !== "") {
      updateChatSome(+uuid, dataSources.value.length - 1, {
        text: `${currentChat.text}\n[${errorMessage}]`,
        error: false,
        loading: false,
      });
      return;
    }

    updateChat(+uuid, dataSources.value.length - 1, {
      dateTime: new Date().toLocaleString(),
      text: errorMessage,
      inversion: false,
      error: true,
      loading: false,
      conversationOptions: null,
      requestOptions: { prompt: message, options: { ...options } },
    });
    scrollToBottom();
  } finally {
    loading.value = false;
  }
}

async function onRegenerate(index: number) {
  if (loading.value) return;

  controller = new AbortController();

  const { requestOptions } = dataSources.value[index];

  let message = requestOptions?.prompt ?? "";

  let options: Chat.ConversationRequest = {};

  if (requestOptions.options) options = { ...requestOptions.options };

  loading.value = true;

  updateChat(+uuid, index, {
    dateTime: new Date().toLocaleString(),
    text: "",
    inversion: false,
    error: false,
    loading: true,
    conversationOptions: null,
    requestOptions: { prompt: message, ...options },
  });

  try {
    let lastText = "";
    const fetchChatAPIOnce = async () => {
      await fetchChatAPIProcess<Chat.ConversationResponse>({
        prompt: message,
        options,
        signal: controller.signal,
        onDownloadProgress: ({ event }) => {
          const xhr = event.target;
          const { responseText } = xhr;
          // Always process the final line
          const lastIndex = responseText.lastIndexOf("\n");
          let chunk = responseText;
          if (lastIndex !== -1) chunk = responseText.substring(lastIndex);
          try {
            const data = JSON.parse(chunk);
            updateChat(+uuid, index, {
              dateTime: new Date().toLocaleString(),
              text: lastText + data.text ?? "",
              inversion: data.inversion ?? false,
              error: false,
              loading: false,
              conversationOptions: {
                conversationId: data.conversationId,
                parentMessageId: data.id,
              },
              requestOptions: { prompt: message, ...options },
            });

            if (
              openLongReply &&
              data.detail.choices[0].finish_reason === "length"
            ) {
              options.parentMessageId = data.id;
              lastText = data.text;
              message = "";
              return fetchChatAPIOnce();
            }
          } catch (error) {
            //
          }
        },
      });
    };
    await fetchChatAPIOnce();
  } catch (error:any) {
    if (error.message === "canceled") {
      updateChatSome(+uuid, index, {
        loading: false,
      });
      return;
    }

    const errorMessage = error?.message ?? t("common.wrong");

    updateChat(+uuid, index, {
      dateTime: new Date().toLocaleString(),
      text: errorMessage,
      inversion: false,
      error: true,
      loading: false,
      conversationOptions: null,
      requestOptions: { prompt: message, ...options },
    });
  } finally {
    loading.value = false;
  }
}

function handleExport() {
  if (loading.value) return;

  const d = dialog.warning({
    title: t("chat.exportImage"),
    content: t("chat.exportImageConfirm"),
    positiveText: t("common.yes"),
    negativeText: t("common.no"),
    onPositiveClick: async () => {
      try {
        d.loading = true;
        const ele = document.getElementById("image-wrapper");
        const canvas = await html2canvas(ele as HTMLDivElement, {
          useCORS: true,
        });
        const imgUrl = canvas.toDataURL("image/png");
        const tempLink = document.createElement("a");
        tempLink.style.display = "none";
        tempLink.href = imgUrl;
        tempLink.setAttribute("download", "chat-shot.png");
        if (typeof tempLink.download === "undefined")
          tempLink.setAttribute("target", "_blank");

        document.body.appendChild(tempLink);
        tempLink.click();
        document.body.removeChild(tempLink);
        window.URL.revokeObjectURL(imgUrl);
        d.loading = false;
        ms.success(t("chat.exportSuccess"));
        Promise.resolve();
      } catch (error) {
        ms.error(t("chat.exportFailed"));
      } finally {
        d.loading = false;
      }
    },
  });
}

function handleDelete(index: number) {
  if (loading.value) return;

  dialog.warning({
    title: t("chat.deleteMessage"),
    content: t("chat.deleteMessageConfirm"),
    positiveText: t("common.yes"),
    negativeText: t("common.no"),
    onPositiveClick: () => {
      chatStore.deleteChatByUuid(+uuid, index);
    },
  });
}

// function handleClear() {
//   if (loading.value) return;

//   dialog.warning({
//     title: t("chat.clearChat"),
//     content: t("chat.clearChatConfirm"),
//     positiveText: t("common.yes"),
//     negativeText: t("common.no"),
//     onPositiveClick: () => {
//       chatStore.clearChatByUuid(+uuid);
//     },
//   });
// }

function handleEnter(event: KeyboardEvent) {
  if (!isMobile.value) {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      handleSubmit();
    }
  } else {
    if (event.key === "Enter" && event.ctrlKey) {
      event.preventDefault();
      handleSubmit();
    }
  }
}

function handleStop() {
  if (loading.value) {
    controller.abort();
    loading.value = false;
  }
}
function handleHistory() {
  embedding_history().then((response) => {
    //console.log(response);
  });
}
// 可优化部分
// 搜索选项计算，这里使用value作为索引项，所以当出现重复value时渲染异常(多项同时出现选中效果)
// 理想状态下其实应该是key作为索引项,但官方的renderOption会出现问题，所以就需要value反renderLabel实现
const searchOptions = computed(() => {
  if (prompt.value.startsWith("/")) {
    return promptTemplate.value
      .filter((item: { key: string }) =>
        item.key.toLowerCase().includes(prompt.value.substring(1).toLowerCase())
      )
      .map((obj: { value: any }) => {
        return {
          label: obj.value,
          value: obj.value,
        };
      });
  } else {
    return [];
  }
});

// value反渲染key
const renderOption = (option: { label: string }) => {
  for (const i of promptTemplate.value) {
    if (i.value === option.label) return [i.key];
  }
  return [];
};

const setFoldPdf = (value: boolean) => {
  foldPdf.value = value;
  appStore.setFoldPdf(value);
  //appStore.setTriggerDownLoad(false);
  if (value === false) {
    //const downloadfile = inject("downloadfile") as (id: number) => Promise<void>;
    const uuid = chatStore.active;
    const chatIndex = chatStore.chat.findIndex((item) => item.uuid === uuid);

    if (chatIndex !== -1) {
      const id = chatStore.chat[chatIndex].pdfFileId;
      if (id > 0) {
        //onMounted(() => {
        appStore.setTriggerDownLoad(true);
        pdfViewer.value?.downloadfile(id);
        //});
      }
    }
  }
};
const placeholder = computed(() => {
  if (isMobile.value) return t("chat.placeholderMobile");
  return t("chat.placeholder");
});

const buttonDisabled = computed(() => {
  return loading.value || !prompt.value || prompt.value.trim() === "";
});

const footerClass = computed(() => {
  let classes = ["p-4"];
  if (isMobile.value)
    classes = [
      "sticky",
      "left-0",
      "bottom-0",
      "right-0",
      "p-2",
      "pr-3",
      "overflow-hidden",
    ];
  return classes;
});

const divWidth = computed(() => {
  return foldPdf.value ? "100%" : `${rightWidth.value}%`;
});

 onMounted(async () => {
	var id = appStore.selectedKeys;
	const response = await last_chat_summary(id);
	if(response!=""){
		const uuid = chatStore.active;
		if (uuid === null) {
      // 處理 uuid 為 null 的情況
      console.error('UUID is null');
      return;
    }
		addChat(+uuid, {
			dateTime: new Date().toLocaleString(),
			text: response,
			inversion: false,
			error: false,
			conversationOptions: null,
			requestOptions: { prompt: "", options: null },
		});
		scrollToBottom();
	}
  scrollToBottom();
});

onUnmounted(() => {
  if (loading.value) controller.abort();
});
</script>

<template>
  <div class="container" ref="containerRef">
    <button v-if="!foldPdf" class="fold_left" @click="setFoldPdf(!foldPdf)">
      <SvgIcon icon="line-md:menu-fold-left" class="mr-2 text-3xl" />
    </button>
    <button v-if="foldPdf" class="fold_right" @click="setFoldPdf(!foldPdf)">
      <SvgIcon icon="line-md:menu-fold-right" class="mr-2 text-3xl" />
    </button>

    <div
      v-if="!foldPdf"
      ref="left_div"
      class="left-div"
      :style="{ width: leftWidth + '%' }"
    >
      <PdfViewer ref="pdfViewer" :scale="pdfScale" :foldPdf="foldPdf" />
    </div>
    <div
      v-if="!foldPdf"
      class="drag-button"
      ref="dragButtonRef"
      @mousedown="startResize"
      :style="{ left: leftWidth + '%' }"
    ></div>
    <div class="right-div" :style="{ width: divWidth }">
      <div class="flex flex-col w-full h-full">
        <HeaderComponent
          v-if="isMobile"
          :using-context="usingContext"
          @export="handleExport"
          @toggle-using-context="toggleUsingContext"
        />
        <main class="flex-1 overflow-hidden">
          <div
            id="scrollRef"
            ref="scrollRef"
            class="h-full overflow-hidden overflow-y-auto"
          >
            <div
              id="image-wrapper"
              class="w-full max-w-screen-xl m-auto dark:bg-[#101014]"
              :class="[isMobile ? 'p-2' : 'p-4']"
            >
              <template v-if="!dataSources.length">
                <div
                  class="flex items-center justify-center mt-4 text-center text-neutral-300"
                >
                  <SvgIcon icon="ri:bubble-chart-fill" class="mr-2 text-3xl" />
                  <span>Aha~</span>
                </div>
              </template>
              <template v-else>
                <div>
                  <Message
                    v-for="(item, index) of dataSources"
                    :key="index"
                    :date-time="item.dateTime"
                    :text="item.text"
                    :inversion="item.inversion"
                    :error="item.error"
                    :loading="item.loading"
                    @regenerate="onRegenerate(index)"
                    @delete="handleDelete(index)"
                  />
                  <div class="sticky bottom-0 left-0 flex justify-center">
                    <NButton v-if="loading" type="warning" @click="handleStop">
                      <template #icon>
                        <SvgIcon icon="ri:stop-circle-line" />
                      </template>
                      Stop Responding
                    </NButton>
                  </div>
                </div>
              </template>
            </div>
          </div>
          <LoadingAnimation
            :active="isLoading"
            :can-cancel="true"
            :on-cancel="onCancel"
            :is-full-page="fullPage"
            loader="spinner"
            :opacity="opacity"
          ></LoadingAnimation>
        </main>
        <footer :class="footerClass">
          <div class="w-full max-w-screen-xl m-auto">
            <div class="flex items-center justify-between space-x-2">
              <!-- <HoverButton @click="handleClear">
                <span class="text-xl text-[#4f555e] dark:text-white">
                  <SvgIcon icon="ri:delete-bin-line" />
                </span>
              </HoverButton> -->
              <HoverButton v-if="!isMobile" @click="handleExport">
                <span class="text-xl text-[#4f555e] dark:text-white">
                  <SvgIcon icon="ri:download-2-line" />
                </span>
              </HoverButton>
              <HoverButton v-if="!isMobile" @click="handleHistory">
                <span
                  class="text-xl"
                  :class="{
                    'text-[#4b9e5f]': usingContext,
                    'text-[#a8071a]': !usingContext,
                  }"
                >
                  <SvgIcon icon="ri:chat-history-line" />
                </span>
              </HoverButton>
              <NAutoComplete
                v-model:value="prompt"
                :options="searchOptions"
                :render-label="renderOption"
              >
                <template #default="{ handleInput, handleBlur, handleFocus }">
                  <NInput
                    v-model:value="prompt"
                    type="textarea"
                    :placeholder="placeholder"
                    :autosize="{ minRows: 1, maxRows: isMobile ? 4 : 8 }"
                    @input="handleInput"
                    @focus="handleFocus"
                    @blur="handleBlur"
                    @keypress="handleEnter"
                  />
                </template>
              </NAutoComplete>
              <NButton
                type="primary"
                :disabled="buttonDisabled"
                @click="handleSubmit"
              >
                <template #icon>
                  <span class="dark:text-black">
                    <SvgIcon icon="ri:send-plane-fill" />
                  </span>
                </template>
              </NButton>
            </div>
          </div>
        </footer>
      </div>
    </div>
  </div>
</template>

<style scoped>
.container {
  position: relative;
  display: flex;
  height: 100%;
  width: 100%;
}
.fold_left {
  position: absolute;
  top: 0px;
  z-index: 999;
  width: 30px;
  height: 30px;
}
.fold_right {
  position: absolute;
  top: 0px;
  z-index: 999;
  width: 30px;
  height: 30px;
}
.left-div {
  position: relative;
}

.drag-button {
  position: absolute;
  top: 0;
  bottom: 0;
  width: 10px;
  background-color: #d3d3d3;
  cursor: col-resize;
  z-index: 1;
}

.right-div {
  position: relative;
}
</style>
