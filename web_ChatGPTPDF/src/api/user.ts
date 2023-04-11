import { get, post } from "@/utils/request";
//import { useSettingStore } from "@/store";
import { MyFile } from "@/typings/user.d.ts";
import axios from "axios"; // 引入 MyFile 介面，並指定其路徑

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

export async function getMyFiles(userId: number): Promise<MyFile[]> {
  try {
    const response = await get<MyFile[]>({
      url: API_BASE_URL + "api/ChatGPTPDF/File/my_files/",
      data: { user: userId },
    });
    const files = response.data;
    return files;
  } catch (error) {
    console.error("Failed to fetch data:", error);
    return [];
  }
}

export async function downloadFile(uuid: string): Promise<any> {
  // Define the url to be used in the get request
  const url = `${API_BASE_URL}api/ChatGPTPDF/File/downloadFile/?id=${uuid}`
  // Call the get function from the request module with the url and method set to 'GET'
  const response = await axios.get(url, {
    responseType: "arraybuffer",
  });
  // Return the response
  return response;
}

export function set_qa_documents(
  document_ids: string[] | string
): Promise<any> {
  const url = `${API_BASE_URL}api/ChatGPTPDF/File/set_qa_documents/`;
  return post({
    url,
    method: "POST",
    data: { document_ids: document_ids },
  });
}
