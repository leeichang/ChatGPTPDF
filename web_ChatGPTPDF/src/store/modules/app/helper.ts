import { ss } from "@/utils/storage";
const LOCAL_NAME = "appSetting";

export type Theme = "light" | "dark" | "auto";

export type Language = "zh-CN" | "zh-TW" | "en-US";

export interface AppState {
  siderCollapsed: boolean;
  theme: Theme;
  language: Language;
  selectedKeys: string[];
  pdf: File | null;
}

export function defaultSetting(): AppState {
  return {
    siderCollapsed: false,
    theme: "light",
    language: "zh-CN",
    selectedKeys: [],
    pdf: null,
  };
}

export function getLocalSetting(): AppState {
  const localSetting: AppState | undefined = ss.get(LOCAL_NAME);
  console.log("localSetting", localSetting);
  return { ...defaultSetting(), ...localSetting };
}

export function setLocalSetting(setting: AppState): void {
  ss.set(LOCAL_NAME, setting);
}
