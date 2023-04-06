<script lang='ts'>
import { defineComponent, onMounted, ref } from "vue";
import * as pdfjsLib from "pdfjs-dist";
import "pdfjs-dist/build/pdf.worker.entry.js";

export default defineComponent({
  name: "PdfViewer",
  setup() {
    const pdfCanvas = ref<HTMLCanvasElement | null>(null);
    // PDF文件的URL
    const url = "sample.pdf";

    // 載入PDF文件
    const loadPdf = async () => {
      const pdfDoc = await pdfjsLib.getDocument(url).promise;

      // 獲取第1頁
      const page = await pdfDoc.getPage(1);

      // 設置縮放比例
      const scale = 1;

      // 獲取渲染用的canvas元素
      const canvas = pdfCanvas.value;

      if (!canvas) {
        return;
      }

      // 獲取渲染上下文
      const context = canvas.getContext("2d");

      if (!context) {
        return;
      }

      // 計算渲染用的canvas元素的寬度和高度
      const viewport = page.getViewport({ scale });
      canvas.width = viewport.width;
      canvas.height = viewport.height;

      // 渲染第1頁
      await page.render({
        canvasContext: context,
        viewport,
      });
    };

    onMounted(() => {
      loadPdf();
    });

    return {
      pdfCanvas,
    };
  },
});
</script>

<template>
  <div>
    <canvas ref="pdfCanvas"></canvas>
  </div>
</template>
