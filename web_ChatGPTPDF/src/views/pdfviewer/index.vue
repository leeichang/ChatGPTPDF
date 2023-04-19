<script lang="ts">
import {
  defineComponent,
  onMounted,
  ref,
  watch,
} from "vue";
import * as pdfjsLib from "pdfjs-dist";
import { downloadFile } from "@/api/user";
import { useAppStore } from "@/store";
import { storeToRefs } from "pinia";
import { isArray } from "lodash";
import _ from "lodash";

export default defineComponent({
  props: {
    scale: {
      type: Number,
      default: 1,
    },
  },
  setup(props) {
    const pdfPages = ref<HTMLDivElement | null>(null);
    const pages = ref<number[]>([]);
    const url = "sample.pdf";
    let thePdf:pdfjsLib.PDFDocumentProxy;
    const viewer = ref<HTMLElement>(document.createElement('div'));
		const pdf = ref<File>(new File([], ""));
    const pdfScale = ref(props.scale);
    const userStore = useAppStore();
    const { selectedKeys } = storeToRefs(userStore);
    const canvases = ref<NodeListOf<HTMLCanvasElement>>(document.querySelectorAll(".pdf-page-canvas"));

    // const divStyle = computed(() => {
    //   const div = this.$refs.pdf_viewer as HTMLElement;
    //   if (div && div.offsetWidth >= 700) {
    //     return { overflowX: "auto" };
    //   } else {
    //     return { overflowX: "hidden" };
    //   }
    // });

    const loadPdf = async (pdf: any = null) => {
      console.log("pdf", pdf);
      pdfjsLib.GlobalWorkerOptions.workerSrc =
        "../../../node_modules/pdfjs-dist/build/pdf.worker.js";
      if (pdf === undefined||pdf === null) {
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
        });
      }
    };

    const renderPage = (pageNumber:number, canvas:HTMLCanvasElement) => {
      thePdf.getPage(pageNumber).then(function (page:pdfjsLib.PDFPageProxy) {
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
      downloadFile(id).then(async (response) => {
        const appStore = useAppStore();
        pdf.value = response.data;
        appStore.setPdf(pdf.value);
        loadPdf(pdf);
      });
    };

    onMounted(() => {
      loadPdf();
    });

    watch(
      () => props.scale,
      (newScale) => {
        pdfScale.value = newScale;
      }
    );

    watch(pdfScale, (newVal) => {
      console.log("watch pdfScale", pdf);
      console.log("watch newVal", newVal);

      RerenderPage();
    });

    watch(selectedKeys, (newVal) => {
			if (newVal === undefined)
				return;
      if (isArray(newVal)) {
        downloadfile(Number(newVal[0]));
      } else {
        downloadfile(newVal);
      }
    });

    return {
      pdfPages,
      pages,
    };
  },
});
</script>

<template>
  <div ref="pdf_viewer" class="pdf-viewer" id="pdf-viewer"></div>
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
</style>
