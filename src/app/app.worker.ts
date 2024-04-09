// @ts-nocheck
/// <reference lib="webworker" />
importScripts("https://cdn.jsdelivr.net/pyodide/v0.25.1/full/pyodide.js")

async function loadPyodideAndPackages() {
  self.pyodide = await loadPyodide()
  await self.pyodide.loadPackage(["opencv-python"])
}
let pyodideReadyPromise = loadPyodideAndPackages()

addEventListener("message", async (event) => {
  await pyodideReadyPromise
  const { python } = event.data
  try {
    await self.pyodide.loadPackagesFromImports(python)
    let results = await self.pyodide.runPythonAsync(python)
    postMessage({ results })
  } catch (error) {
    console.log(error)
    postMessage({ error: error.message })
  }
})
