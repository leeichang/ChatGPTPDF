/// <reference types="vite/client" />

import {
  LoadingBarProviderInst,
  DialogProviderInst,
  MessageProviderInst,
  NotificationProviderInst,
} from "naive-ui";
declare global {
  export interface Window {
    $loadingBar?: import("naive-ui").LoadingBarProviderInst;
    $dialog?: import("naive-ui").DialogProviderInst;
    $message?: import("naive-ui").MessageProviderInst;
    $notification?: import("naive-ui").NotificationProviderInst;
  }
}

export interface options {
  value: number;
  label: string;
}
