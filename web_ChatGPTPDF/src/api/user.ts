import { get } from "@/utils/request";
//import { useSettingStore } from "@/store";
import { MyFile } from "@/typings/user.d.ts"; // 引入 MyFile 介面，並指定其路徑

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

export async function getMyFiles(userId: number): Promise<MyFile[]> {
	try {
		const response = await get<MyFile[]>({
			url: API_BASE_URL+ "api/ChatGPTPDF/File/my_files/",
			data: { user: userId },
		});
		const files = response.data;
		return files;
	} catch (error) {
		console.error("Failed to fetch data:", error);
		return [];
	}
}
