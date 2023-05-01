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
		// Vue: {
    //   // ...其他已声明的Vue属性和方法
    //   computed<T>(getter: () => T): ComputedRef<T>;
		// 	ref<T>(value?: T): Ref<T>;
		// 	nextTick(fn: () => void): Promise<void>;
		// 	useAttrs(): Ref<Record<string, unknown>>;
    //   onMounted(fn: () => void): void;
    //   h(type: any, propsOrChildren?: any, children?: any): VNode;
    //   watch<T>(
    //     source: WatchSource<T> | WatchSource<T>[],
    //     effect: WatchEffect<T>,
    //     options?: WatchOptions
    //   ): WatchStopHandle;
		// 	defineComponent<T extends Component>(component: T): DefineComponent<T>;
    //   defineAsyncComponent<T extends Component>(
    //     loader: AsyncComponentLoader<T>,
    //     options?: AsyncComponentOptions
    //   ): DefineComponent<T>;
    // };
  }
}

export interface options {
  value: number;
  label: string;
}
