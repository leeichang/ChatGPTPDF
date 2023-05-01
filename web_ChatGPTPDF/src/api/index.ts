import type { AxiosProgressEvent, GenericAbortSignal } from "axios";
import { post } from "@/utils/request";
import { useAppStore, useSettingStore } from "@/store";

//const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;
const API_APP_URL = import.meta.env.VITE_APP_URL;

export function fetchChatAPI<T = any>(
  prompt: string,
  options?: { conversationId?: string; parentMessageId?: string },
  signal?: GenericAbortSignal
) {
  return post<T>({
    url: "/chat",
    data: { prompt, options },
    signal,
  });
}

export function fetchChatConfig<T = any>() {
  return post<T>({
    url: "/config",
  });
}

export function fetchChatAPIProcess<T = any>(params: {
  prompt: string;
  options?: { conversationId?: string; parentMessageId?: string };
  signal?: GenericAbortSignal;
  onDownloadProgress?: (progressEvent: AxiosProgressEvent) => void;
}) {
  const settingStore = useSettingStore();
  const appStore = useAppStore();
  return post<T>({
    url: `${API_APP_URL}api/ChatGPTPDF/File/chat_process/`,
    data: {
      prompt: params.prompt,
      options: params.options,
      systemMessage: settingStore.systemMessage,
      selectedKeys: appStore.selectedKeys,
    },
    signal: params.signal,
    onDownloadProgress: params.onDownloadProgress,
  });
  // return post<T>({
  //   url: '/chat-process',
  //   data: { prompt: params.prompt, options: params.options, systemMessage: settingStore.systemMessage },
  //   signal: params.signal,
  //   onDownloadProgress: params.onDownloadProgress,
  // })
}

export function fetchSession<T>() {
  return post<T>({
    url: `${API_APP_URL}api/session/`,
  });
}

export function fetchVerify<T>(token: string) {
  return post<T>({
    url: `${API_APP_URL}/verify`,
    data: { token },
  });
}
