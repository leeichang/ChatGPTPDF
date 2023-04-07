<script lang="ts">
import { defineComponent, onMounted, ref, watch } from "vue";
import * as pdfjsLib from "pdfjs-dist";
import "pdfjs-dist/build/pdf.worker.entry.js";

export default defineComponent({
	name: "PdfViewer",
	props: {
		scale: {
			type: Number,
			default: 1.35,
		},
	},
	setup(props) {
		const pdfCanvas = ref<HTMLCanvasElement | null>(null);
		const url = "sample.pdf";
		const pdfScale = ref(props.scale);

		const loadPdf = async () => {
			const pdfDoc = await pdfjsLib.getDocument(url).promise;
			const page = await pdfDoc.getPage(1);
			const scale = pdfScale.value;
			const canvas = pdfCanvas.value;
			if (!canvas) {
				return;
			}
			const context = canvas.getContext("2d");
			if (!context) {
				return;
			}
			const viewport = page.getViewport({ scale });
			canvas.width = viewport.width;
			canvas.height = viewport.height;
			await page.render({
				canvasContext: context,
				viewport,
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

		watch(pdfScale, () => {
			loadPdf();
		});

		return {
			pdfCanvas,
			pdfScale,
		};
	},
});
</script>

<template>
	<div>
		<canvas ref="pdfCanvas"></canvas>
	</div>
</template>
