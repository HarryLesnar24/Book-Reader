"use strict";

import * as pdfjsLib from "../../../node_modules/pdfjs-dist";

import {
  EventBus,
  PDFLinkService,
  PDFViewer,
} from "../../../node_modules/pdfjs-dist/web/pdf_viewer.mjs";

pdfjsLib.GlobalWorkerOptions.workerSrc = "/static/pdf.worker.mjs";

// pdfjsLib.VerbosityLevel = pdfjsLib.VerbosityLevel.INFOS;

const pdfContainer = document.querySelector(".canvas-container");
const pdfViewContainer = document.querySelector(".viewer-pdf");
const srcURL = pdfViewContainer.dataset.url;

const eventBus = new EventBus();
const pdfLinkService = new PDFLinkService({ eventBus: eventBus });

const pdfViewer = new PDFViewer({
  container: pdfContainer,
  viewer: pdfViewContainer,
  linkService: pdfLinkService,
  eventBus: eventBus,
});

pdfLinkService.setViewer(pdfViewer);
const loadingTask = pdfjsLib.getDocument({
  url: srcURL,
  cMapUrl: "/static/pdfjs/web/cmaps/",
  cMapPacked: true,
  enableXfa: true,
  httpHeaders: { Authorization: "Bearer " },
});

loadingTask.onProgress = ({ loaded, total }) => {
  console.log(`Loading: ${(loaded / total) * 100}%\n`);
};

loadingTask.promise
  .then((pdfDocument) => {
    pdfDocument.getOutline();
    pdfViewer.setDocument(pdfDocument);
    pdfLinkService.setDocument(pdfDocument);
    eventBus.on("pagesinit", () => {
      pdfViewer.currentPageNumber = 1;
      pdfViewer;
    });
  })
  .catch((err) => console.error("PDF load error:", err));

// const page = await pdfDocument.getPage(1);
// const ctx = canvas.getContext("2d");
// let scale = 1.5;
// const viewport = page.getViewport({
//   scale: scale,
// });
// let outputScale = window.devicePixelRatio || 1;
// canvas.width = Math.floor(viewport.width * outputScale);
// canvas.height = Math.floor(viewport.height * outputScale);
// canvas.style.width = String(Math.floor(viewport.width)) + "px";
// canvas.style.height = String(Math.floor(viewport.height)) + "px";
// let transform =
//   outputScale !== 1 ? [outputScale, 0, 0, outputScale, 0, 0] : null;
// let renderContext = {
//   intent: "display",
//   canvasContext: ctx,
//   transform: transform,
//   viewport: viewport,
// };
// let renderTask = page.render(renderContext);
// renderTask.promise.then(() => console.log("Page loaded"));

// #!/bin/bash

// apt-get update -y
// snap install amazon-ssm-agent --classic
// systemctl enable snap.amazon-ssm-agent.amazon-ssm-agent.service
// systemctl start snap.amazon-ssm-agent.amazon-ssm-agent.service
