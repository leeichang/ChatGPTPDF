<script lang="ts">
import { defineComponent, onMounted, ref, watch } from "vue";
import * as pdfjsLib from "pdfjs-dist";
import { downloadFile } from "@/api/user";
// import { useAppStore , useChatStore  } from "@/store";
import { useAppStore } from "@/store";
import { storeToRefs } from "pinia";
import { isArray } from "lodash";
import _ from "lodash";
import Loading from "vue3-loading-overlay";
import "vue3-loading-overlay/dist/vue3-loading-overlay.css";
import { SvgIcon } from "@/components/common";

export default defineComponent({
  components: {
    Loading,
    SvgIcon,
  },
  props: {
    scale: {
      type: Number,
      default: 1,
    },
  },
  setup(props) {
    const pdfPages = ref<HTMLDivElement | null>(null);
    const pages = ref<number[]>([]);
    const url = "";
    let thePdf: pdfjsLib.PDFDocumentProxy;
    const viewer = ref<HTMLElement>(document.createElement("div"));
    const pdf = ref<File>(new File([], ""));
    const pdfScale = ref(props.scale);
    const userStore = useAppStore();
		// const chatStore = useChatStore();
    //const { selectedKeys, uploadPdf } = storeToRefs(userStore);
		const { selectedKeys } = storeToRefs(userStore);
    const canvases = ref<NodeListOf<HTMLCanvasElement>>(
      document.querySelectorAll(".pdf-page-canvas")
    );
    const isLoading = ref(false);
    const fullPage = ref(false);

    // 在 setup() 函數中添加以下變量
    const currentPage = ref(1);
    const totalPages = ref(0);

    // 在 setup() 函數中添加以下方法
    const zoomIn = () => {
      pdfScale.value += 0.1;
    };

    const zoomOut = () => {
      pdfScale.value -= 0.1;
    };

    const prevPage = () => {
      if (currentPage.value > 1) {
        currentPage.value--;
        scrollToPage(currentPage.value);
      }
    };

    const nextPage = () => {
      if (currentPage.value < totalPages.value) {
        currentPage.value++;
        scrollToPage(currentPage.value);
      }
    };

    const scrollToPage = (pageNumber: number) => {
      const pageElement = document.querySelectorAll(".pdf-page-canvas")[
        pageNumber - 1
      ] as HTMLElement;
      pageElement.scrollIntoView({ behavior: "smooth" });
    };

    const onCancel = () => {
      console.log("User cancelled the loader.");
      //because the props is single flow direction, you need to set isLoading status normally.
      isLoading.value = false;
    };
    const loadPdf = async (pdf: any = null) => {
      console.log("pdf", pdf);
      pdfjsLib.GlobalWorkerOptions.workerSrc =
        "../../../node_modules/pdfjs-dist/build/pdf.worker.js";
      if (pdf === undefined || pdf === null) {
        const canvasElements = document.querySelectorAll(".pdf-page-canvas");
        canvasElements.forEach((canvasElement) => {
          canvasElement.parentNode?.removeChild(canvasElement);
        });
        pdfjsLib.getDocument(url).promise.then(function (pdfDoc) {
          thePdf = pdfDoc;
          viewer.value = document.getElementById("pdf-viewer")!;

          for (var page = 1; page <= pdfDoc.numPages; page++) {
            var canvas = document.createElement("canvas");
            canvas.className = "pdf-page-canvas";
            viewer.value.appendChild(canvas);
            renderPage(page, canvas);
          }
          totalPages.value = pdfDoc.numPages;
        });
      } else {
        const canvasElements = document.querySelectorAll(".pdf-page-canvas");
        canvasElements.forEach((canvasElement) => {
          canvasElement.parentNode?.removeChild(canvasElement);
        });
        const pdfData = new Uint8Array(pdf.value);
        pdfjsLib.getDocument(pdfData).promise.then(function (pdfDoc) {
          thePdf = pdfDoc;
          viewer.value = document.getElementById("pdf-viewer")!;

          for (var page = 1; page <= pdfDoc.numPages; page++) {
            var canvas = document.createElement("canvas");
            canvas.className = "pdf-page-canvas";
            viewer.value.appendChild(canvas);
            renderPage(page, canvas);
          }
          totalPages.value = pdfDoc.numPages;
        });
      }
    };

    const renderPage = (pageNumber: number, canvas: HTMLCanvasElement) => {
      thePdf.getPage(pageNumber).then(function (page: pdfjsLib.PDFPageProxy) {
        const scale = pdfScale.value;
        const viewport = page.getViewport({ scale });
        canvas.height = viewport.height;
        canvas.width = viewport.width;
        page.render({
          canvasContext: canvas.getContext("2d")!,
          viewport: viewport,
        });
      });
    };

    const RerenderPage = _.debounce(async function () {
      canvases.value = document.querySelectorAll(".pdf-page-canvas")!;
      console.log("RerenderPage canvases.value", canvases.value);
      console.log("RerenderPage thePdf.numPages", thePdf.numPages);
      for (var pageNumber = 1; pageNumber <= thePdf.numPages; pageNumber++) {
        (function (pageNumber) {
          thePdf.getPage(pageNumber).then((page) => {
            const scale = pdfScale.value;
            const viewport = page.getViewport({ scale });
            let canvas = canvases.value[pageNumber];
            const context = canvas.getContext("2d")!;
            canvas.width = viewport.width;
            canvas.height = viewport.height;
            const renderContext = {
              canvasContext: context,
              viewport,
            };
            page.render(renderContext);
          });
        })(pageNumber);
      }
    }, 500);

    //透過api下載pdf檔案
    // Define a function named downloadFile that takes in a file uuid as a parameter
    const downloadfile = async (id: number) => {
      isLoading.value = true;
      downloadFile(id).then(async (response) => {
        const appStore = useAppStore();
        pdf.value = response.data;
        appStore.setPdf(pdf.value);
        loadPdf(pdf);
        isLoading.value = false;
      });
    };

    onMounted(() => {
      var id = userStore.selectedKeys;
      if (isArray(id)) {
        downloadfile(id[0]);
      } else {
        downloadfile(id);
      }
    });

    watch(
      () => props.scale,
      (newScale) => {
        pdfScale.value = newScale;
      }
    );
    // watch(uploadPdf, (newVal) => {
    //   if (newVal) {
		// 		let uuid = Date.now()
		// 		chatStore.addHistory({ title: newVal.name, uuid: uuid, isEdit: false, id:0, name:newVal.name},[]);

    //     (async () => {
    //       const arrayBuffer = await fileToArrayBuffer(newVal);
    //       loadPdf(arrayBuffer);
    //     })();
    //   }
    // });
    watch(pdfScale, (newVal) => {
      console.log("watch pdfScale", pdf);
      console.log("watch newVal", newVal);

      RerenderPage();
    });
    // watch(loading, (newVal) => {
    //   console.log("watch loading", newVal);
    //   isLoading.value = newVal;
    // });
    watch(selectedKeys, (newVal) => {
      if (newVal === undefined || newVal ===0 || isLoading.value) return;
      if (isArray(newVal)) {
        downloadfile(Number(newVal[0]));
      } else {
        downloadfile(newVal);
      }
    });

    // function fileToArrayBuffer(file: File): Promise<ArrayBuffer> {
    //   return new Promise((resolve, reject) => {
    //     const fileReader = new FileReader();

    //     fileReader.onload = (event) => {
    //       resolve(event.target?.result as ArrayBuffer);
    //     };

    //     fileReader.onerror = (error) => {
    //       reject(error);
    //     };

    //     fileReader.readAsArrayBuffer(file);
    //   });
    // }

    return {
      pdfPages,
      pages,
      isLoading,
      onCancel,
      fullPage,
      currentPage,
      totalPages,
      zoomIn,
      zoomOut,
      prevPage,
      nextPage,
    };
  },
});
</script>

<template>
  <div class="container">
    <div class="toolbar">
      <button @click="zoomIn">
        <SvgIcon icon="ic:baseline-zoom-in" class="mr-2 text-3xl" />
      </button>
      <button @click="zoomOut">
        <SvgIcon icon="ic:baseline-zoom-out" class="mr-2 text-3xl" />
      </button>
      <button @click="prevPage">
        <SvgIcon icon="ic:round-skip-previous" class="mr-2 text-3xl" />
      </button>
      <span>{{ currentPage }} / {{ totalPages }}</span>
      <button @click="nextPage">
        <SvgIcon icon="ic:round-skip-next" class="mr-2 text-3xl" />
      </button>
    </div>
    <div ref="pdf_viewer" class="pdf-viewer" id="pdf-viewer"></div>
    <loading
      :active="isLoading"
      :can-cancel="true"
      :on-cancel="onCancel"
      :is-full-page="fullPage"
      loader="spinner"
    ></loading>
  </div>
</template>

<style scoped>
.pdf-viewer {
  overflow-y: auto;
  overflow-x: hidden;
  height: 100%;
  /* Adjust this value to fit your desired container height */
}

.pdf-pages canvas {
  display: block;
  margin-bottom: 1rem;
}
.container {
  position: relative;
}
.toolbar {
  display: flex;
  justify-content: center;
  align-items: center;
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 40px;
  background-color: #f8f8f8;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  z-index: 100;
}

.toolbar button,
.toolbar span {
  margin: 0 10px;
}

.pdf-viewer {
  margin-top: 45px;
  overflow-y: auto;
  overflow-x: hidden;
  height: calc(100% - 50px);
}
</style>
