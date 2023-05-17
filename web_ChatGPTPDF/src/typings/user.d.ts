/// <reference types="vite/client" />
// 定義 MyFile 介面，用於指定文件物件的型別
export interface MyFile {
  id: number;
  file_name: string;
  file_uuid: string;
}

export interface Document {
  status: string;
  id: number;
  name: string;
  data: string;
  NoPdf: boolean;
}

export interface ResponseResult {
  status: string;
  data: string;
  inversion: boolean;
}
