// 引入原有的 Dict 類型
import { Dict as OriginalDict } from '@types/node/globals';

// 使用 Omit 移除原有的索引簽名
type DictWithoutIndexSignature<T> = Omit<OriginalDict<T>, keyof OriginalDict<T>>;

// 使用聲明合併（declaration merging）覆寫 Dict
declare module '@types/node/globals' {
  interface Dict<T> extends DictWithoutIndexSignature<T> {
    [key: string]: T; // 新的索引簽名，只允許 T 類型
  }
}
