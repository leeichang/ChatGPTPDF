<script lang="ts">
import { defineComponent, ref } from "vue";
import { useMessage } from "naive-ui";
import { set_qa_documents , uploadFile, } from "@/api/user";
import { t } from "@/locales";
import { useAppStore } from "@/store";

export default defineComponent({
  emits: { historyAdd: (object: { id: number; name: string }) => true },
  name: "FileUploader",
  setup(props, { emit }) {
    const fileInput = ref<HTMLInputElement | null>(null);
    const uploading = ref(false);
    const uploaded = ref(false);
    const progress = ref(0);
    const message = useMessage();
		const appStore = useAppStore();

    const onUploaderClick = () => {
      fileInput.value?.click();
    };

    const onFileInputChange = (event: Event) => {
      const files = (event.target as HTMLInputElement).files;
      if (files) {
        uploadFiles(files);
      }
    };

    const onDrop = (event: DragEvent) => {
      event.preventDefault();
      const files = event.dataTransfer?.files;
      if (files) {
        uploadFiles(files);
      }
    };

    const uploadFiles = (files: FileList) => {
      uploading.value = true;
      uploaded.value = false;
      let filename: string = "";
      // 上傳文件的邏輯
      let formData = new FormData();
      for (var i = 0; i < files.length; i++) {
        var item: File = files[i];
        console.log(item);
        formData.append("file", item, item.name);
        filename = item.name;
      }
      uploadFile(formData)
        .then((res) => {
          console.log(res);
          uploaded.value = true;
          uploading.value = false;
          let id = res.data.id;
          let name = filename;

          emit("historyAdd", { id: id, name: name });
          if (id > 0) {
            set_qa_documents(id).then((response) => {
							console.log(response);
            });
            appStore.setSelectedKeys(id);
						message.success(t("upload_success"));
          }
          setTimeout(() => {
            uploaded.value = false;
          }, 3000);
        })
        .catch((err) => {
          message.error(err);
        });
    };

    return {
      fileInput,
      uploading,
      uploaded,
      progress,
      onUploaderClick,
      onFileInputChange,
      onDrop,
      uploadFiles,
    };
  },
});
</script>

<template>
  <div
    class="file-uploader"
    @dragover.prevent
    @drop="onDrop"
    @click="onUploaderClick"
  >
    <input ref="fileInput" type="file" hidden @change="onFileInputChange" />
    <div class="tip" v-if="!uploading && !uploaded">
      <p>{{ $t("common.Drog_Drop_File_Here") }}</p>
    </div>
    <div class="loading" v-if="uploading">
      <span class="top"></span>
      <span class="bottom"></span>
      <div class="processing">{{ $t("common.processing") }}</div>
    </div>
    <div class="message" v-if="uploaded">
      <p>{{ $t("common.upload_success") }}</p>
    </div>
  </div>
</template>

<style scoped>
.file-uploader {
  position: relative;
  left: 10px;
  top: 5px;
  width: 240px;
  height: 70px;
  outline: 1px dashed black;
  display: flex;
  justify-content: center; /* 水平置中 */
  align-items: center; /* 垂直置中 */
  border-radius: 0.5em;
  margin-bottom: 10px;
  background-color: #f7f7f7;
}
.processing {
  position: absolute;
  top: 35%;
  left: 95%;
  width: 100px;
}
.loading {
  width: 29px;
  height: 65px;
  /* 相对定位 */
  position: relative;
  /* 弹性布局 */
  display: flex;
  /* 将元素垂直显示 */
  flex-direction: column;
  /* 将元素靠边对齐 */
  justify-content: space-between;
  align-items: center;
  /* 执行动画：动画 时长 线性的 无限次播放 */
  animation: rotating 2s linear infinite;
}
/* 添加流下的元素 */
.loading::after {
  content: "";
  width: 2px;
  height: 27px;
  background-color: #cabbe9;
  /* 绝对定位 */
  position: absolute;
  top: 5px;
  /* 执行动画 */
  animation: flow 2s linear infinite;
}
/* 沙漏上下两个容器 */
.top,
.bottom {
  width: 23px;
  height: 23px;
  border-style: solid;
  border-color: #dcdcdc;
  border-width: 2px 2px 4px 4px;
  border-radius: 50% 100% 50% 30%;
  position: relative;
  overflow: hidden;
}
.top {
  /* 旋转-45度 */
  transform: rotate(-45deg);
  top: 7px;
}
.bottom {
  /* 旋转135度 */
  transform: rotate(135deg);
  bottom: 7px;
}
.top::before,
.bottom::before {
  content: "";
  /* 绝对定位 */
  position: absolute;
  /* inherit表示继承父元素（这里指宽高） */
  width: inherit;
  height: inherit;
  background-color: #cabbe9;
  /* 执行动画，先设置动画的参数，不指定动画名称 */
  animation: 2s linear infinite;
}
.top::before {
  /* 通过设置圆角改变沙的形状 */
  border-radius: 0 100% 0 0;
  /* 指定执行的动画 */
  animation-name: drop-sand;
}
.bottom::before {
  /* 通过设置圆角改变沙的形状 */
  border-radius: 0 0 0 25%;
  /* 指定执行的动画 */
  animation-name: fill-sand;
  /* 把下面的沙移出可视范围 */
  transform: translate(17px, -17px);
}

/* 定义动画 */
/* 落沙动画 */
@keyframes drop-sand {
  to {
    transform: translate(-17px, 17px);
  }
}
/* 填沙动画 */
@keyframes fill-sand {
  to {
    transform: translate(0, 0);
  }
}
/* 沙流下动画 */
@keyframes flow {
  10%,
  100% {
    transform: translateY(22px);
  }
}
/* 沙漏旋转动画 */
@keyframes rotating {
  0%,
  90% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(180deg);
  }
}
</style>
