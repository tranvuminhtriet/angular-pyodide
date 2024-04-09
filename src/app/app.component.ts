import { Component, OnInit } from "@angular/core"
import { HttpClient } from "@angular/common/http"

@Component({
  selector: "app-root",
  templateUrl: "./app.component.html",
  styleUrls: ["./app.component.scss"],
})
export class AppComponent implements OnInit {
  title = "webworker"
  worker!: Worker
  loading = false

  pythonScript!: string
  url_vis: string = "http://localhost:4200/assets/IMG_vis.jpeg"
  url_IR: string = "http://localhost:4200/assets/IMG_IR.jpeg"

  resultImage!: string

  constructor(private http: HttpClient) {}

  async ngOnInit() {
    let script = await this.fetchPythonFile()
    if (!script) return
    this.pythonScript = script.replace("${url_vis}", this.url_vis).replace("${url_IR}", this.url_IR)
  }

  async fetchPythonFile() {
    const data = await this.http.get("/assets/process_img.py", { responseType: "text" }).toPromise()
    return data
  }

  processImage() {
    this.loading = true
    this.worker = new Worker(new URL("./app.worker", import.meta.url))
    this.worker.onmessage = ({ data }) => {
      const regularURL = this.dataURLtoURL(data.results)
      this.resultImage = regularURL

      console.log(regularURL)
      this.loading = false
    }
    this.worker.postMessage({ python: this.pythonScript })
  }

  dataURLtoURL(dataURL: string): string {
    const byteString = atob(dataURL.split(",")[1])
    const mimeString = dataURL.split(",")[0].split(":")[1].split(";")[0]
    const ab = new ArrayBuffer(byteString.length)
    const ia = new Uint8Array(ab)

    for (let i = 0; i < byteString.length; i++) {
      ia[i] = byteString.charCodeAt(i)
    }

    const blob = new Blob([ab], { type: mimeString })
    return URL.createObjectURL(blob)
  }

  cancelWorker() {
    this.worker.terminate()
    this.loading = false
  }
}
