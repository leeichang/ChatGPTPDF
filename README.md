# 前端 Service♝

## 进入项目目录
cd web_ChatGPTPDF/service
## 編譯要安装依赖
yarn install

## 編譯程式
yarn build 

## 編譯後的程式在service/build 資料夾下
## 正常除錯是启动服务
yarn run dev

## 部署到正式環境要參考qrcode專案nodejs的部署方式

# 前端 Web♝`
## 进入项目目录
cd web_ChatGPTPDF
## 編譯要安装依赖
yarn install

## 修改 .env 對應正式環境的後端服務器地址 主要是修改 VITE_API_BASE_URL=http://localhost:8000/，這個是python的服務位置
## 編譯程式
yarn build 

## 將dist資料夾下的所有檔案複製server發布資料夾上

## 要設定nginx的設定檔，將所有的請求都導向到index.html，這樣才能讓vue-router正常運作，也要參考之前的vue專案設定vue-router的對應設定檔，這是對外的入口，service與python服務都不需要對外開放

# 后端💈python

~~~bash
1. 进入项目目录 cd backend
2. 修改 .env 文件中的配置信息
FILE_UPLOAD_DIR =目前是設定專案的根目錄的upload資料夾，後續要改成設定成環境變數，並且要授權給www-data
FILE_INDEX_DIR  =目前是設定專案的根目錄的index資料夾，後續要改成設定成環境變數，並且要授權給www-data
3. 建立虚拟环境
	在 backend目录下执行
	python3 -m venv venv
	電腦起動開機要設定：source backend路徑/venv/bin/activate
4. 安装依赖环境
	pip3 install -r requirements.txt
5. 启动项目
	在backend目录下执行 uwsgi --ini ChatGPTPDF_uwsgi.ini 這個要設定成開機自動執行
6. ChatGPTPDF_uwsgi.ini 設定檔 包含同時可以處理的執行序數量(workers)與log檔案位置(daemonize) 這兩個要配合環境設定
~~~


