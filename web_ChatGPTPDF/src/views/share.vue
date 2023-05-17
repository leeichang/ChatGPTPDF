<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { getShare } from "@/api/user";
import { useAppStore, useChatStore } from "@/store";
import { useChat } from "@/views/chat/hooks/useChat";
import { Document } from "@/typings/user";

const { addChat } = useChat();
const appStore = useAppStore();
const chatStore = useChatStore();
const route = useRoute();
const router = useRouter();

const uuid = ref("");
onMounted(() => {
  uuid.value = route.query.uuid as string;
  getShare(uuid.value).then((res) => {
    //console.log(res);
    let document = res as Document;
    if (document.id) {
      let uuid = Date.now();
      chatStore.addHistory(
        {
          title: document.name,
          uuid: uuid,
          isEdit: false,
          id: document.id,
          name: document.name,
        },
        []
      );
      let options: Chat.ConversationRequest = {};

      addChat(uuid, {
        dateTime: new Date().toLocaleString(),
        text: document.data,
        inversion: false,
        error: false,
        conversationOptions: null,
        requestOptions: { prompt: "", options: { ...options } },
      });
			appStore.setTriggerDownLoad(true);
			appStore.setSelectedKeys(document.id);
      router.push("/chat/" + uuid);
    }
  });
});
</script>
<template>
  <div>
    <h1>錯誤的連結資料</h1>
  </div>
</template>
