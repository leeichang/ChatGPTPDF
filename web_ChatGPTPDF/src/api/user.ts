import { get, post } from "@/utils/request";
//import { ref } from "vue";
//import { useSettingStore } from "@/store";

import axios from "axios"; // 引入 MyFile 介面，並指定其路徑
import { useAppStore } from '@/store'

//const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;
const API_APP_URL = import.meta.env.VITE_APP_URL;

export async function getShare(uuid: string){
  try {
    const response = await get<Document>({
      url: API_APP_URL + "api/ChatGPTPDF/File/get_share/",
      data: { uuid: uuid },
    });
    const document = response;
    return document;
  } catch (error:any) {
    console.error("Failed to fetch data:", error);
    return {};
  }
}

export async function last_chat_summary(id: number): Promise<string> {
  try {
		const appStore = useAppStore()
    const response = await get<string>({
      url: API_APP_URL + "api/ChatGPTPDF/File/last_chat_summary/",
      data: { id: id,
						 guid: appStore.user_guid },
    });
    const data = response.data;
    return data;
  } catch (error:any) {
    console.error("Failed to fetch data:", error);
    return "";
  }
}

export async function downloadFile(id: number): Promise<any> {
  // Define the url to be used in the get request
	const appStore = useAppStore()
  const url = `${API_APP_URL}api/ChatGPTPDF/File/downloadFile/?id=${id}&guid=${appStore.user_guid}`;
  // Call the get function from the request module with the url and method set to 'GET'
  const response = await axios.get(url, {
    responseType: "arraybuffer",
		timeout: 600000,
		validateStatus: (status) => {
			return status === 200;
		}
  });
  // Return the response
  return response;
}

export function set_qa_documents(
  document_ids: number[] | number
): Promise<any> {
	const appStore = useAppStore()
  const url = `${API_APP_URL}api/ChatGPTPDF/File/set_qa_documents/`;
  return post({
    url,
    method: "POST",
    data: { document_ids: document_ids,
					 guid: appStore.user_guid },
  });
}

export function embedding_history(): Promise<any> {
	const appStore = useAppStore()
  const url = `${API_APP_URL}api/ChatGPTPDF/File/embedding_history/`;
  return post({
    url,
    method: "POST",
    data: { guid: appStore.user_guid },
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
  const appStore = useAppStore()
  return axios.post(
    UploadUrl,
    formData,
    {
      headers: {
        "Content-Type": "multipart/form-data",
    		"X-GUID":appStore.user_guid  }
    }
  );
}
