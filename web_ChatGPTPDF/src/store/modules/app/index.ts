import { defineStore } from "pinia";
import type { AppState, Language, Theme } from "./helper";
import { getLocalSetting, setLocalSetting } from "./helper";
import { store } from "@/store";

export const useAppStore = defineStore("app-store", {
  state: (): AppState => getLocalSetting(),
  actions: {
    setSiderCollapsed(collapsed: boolean) {
      this.siderCollapsed = collapsed;
      this.recordState();
    },

    setTheme(theme: Theme) {
      this.theme = theme;
      this.recordState();
    },

    setLanguage(language: Language) {
      if (this.language !== language) {
        this.language = language;
        this.recordState();
      }
    },
    setSelectedKeys(selectedKeys: number[] | number) {
      //if (this.selectedKeys !== selectedKeys) {
      this.selectedKeys = selectedKeys;
      this.recordState();
      //}
    },
    setPdf(pdf: File) {
      console.log("setPdf: ", pdf);
      this.pdf = pdf;
      this.recordState();
    },
    setUploadPdf(uploadPdf: File) {
      console.log("setUploadPdf: ", uploadPdf);
      this.uploadPdf = uploadPdf;
      this.recordState();
    },
    setLoading(loading: boolean) {
      console.log("setLoading: ", loading);
      this.loading = loading;
      this.recordState();
    },
    setFoldPdf(foldPdf: boolean) {
      console.log("setFoldPdf: ", foldPdf);
      this.foldPdf = foldPdf;
      this.recordState();
    },
    setDownLoadPdf(downloadPdf: boolean) {
      console.log("setDownloadPdf: ", downloadPdf);
      this.downloadPdf = downloadPdf;
      this.recordState();
    },
    setIsFirstLoad(isFirstLoad: boolean) {
      console.log("setIsFirstLoad: ", isFirstLoad);
      this.isFirstLoad = isFirstLoad;
      this.recordState();
    },

    recordState() {
      setLocalSetting(this.$state);
    },
  },
});

export function useAppStoreWithOut() {
  return useAppStore(store);
}
