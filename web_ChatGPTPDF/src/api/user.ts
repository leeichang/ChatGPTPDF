import { get, post } from "@/utils/request";
//import { ref } from "vue";
//import { useSettingStore } from "@/store";
import { MyFile } from "@/typings/user";
import axios from "axios"; // 引入 MyFile 介面，並指定其路徑

//const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;
const API_APP_URL = import.meta.env.VITE_APP_URL;

export async function getMyFiles(userId: number): Promise<MyFile[]> {
  try {
    const response = await get<MyFile[]>({
      url: API_APP_URL + "api/ChatGPTPDF/File/my_files/",
      data: { user: userId },
    });
    const files = response.data;
    return files;
  } catch (error:any) {
    console.error("Failed to fetch data:", error);
    return [];
  }
}

export async function downloadFile(id: number): Promise<any> {
  // Define the url to be used in the get request
  const url = `${API_APP_URL}api/ChatGPTPDF/File/downloadFile/?id=${id}`;
  // Call the get function from the request module with the url and method set to 'GET'
  const response = await axios.get(url, {
    responseType: "arraybuffer",
  });
  // Return the response
  return response;
}

export function set_qa_documents(
  document_ids: number[] | number
): Promise<any> {
  const url = `${API_APP_URL}api/ChatGPTPDF/File/set_qa_documents/`;
  return post({
    url,
    method: "POST",
    data: { document_ids: document_ids },
  });
}

/**
 * 上傳產品圖檔
 *
 * @author leeichang
 * @date 2020/5/17 01:50
 */
export function uploadFile(formData: FormData) {
  // const uploading = ref(true);
  // const progress = ref(0);
  axios.defaults.withCredentials = true;
  // const VITE_APP_URL = import.meta.env.VITE_APP_URL;
  const UploadUrl = `${API_APP_URL}api/ChatGPTPDF/File/perform_create/`;

  return axios.post(
    UploadUrl,
    formData,
    {
      headers: {
        "Content-Type": "multipart/form-data",
        //"Accept-Encoding": "gzip, deflate, br",
        // Connection: "keep-alive",
        // Host: API_BASE_URL,
        // Origin: VITE_APP_URL,
        // Referer: VITE_APP_URL,
      }
    }
  );
}
