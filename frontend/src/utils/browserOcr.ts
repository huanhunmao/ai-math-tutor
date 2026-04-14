export async function extractTextInBrowser(file: File) {
  const { createWorker } = await import("tesseract.js");
  const worker = await createWorker("chi_sim+eng");

  try {
    const {
      data: { text },
    } = await worker.recognize(file);
    return text.trim();
  } finally {
    await worker.terminate();
  }
}
