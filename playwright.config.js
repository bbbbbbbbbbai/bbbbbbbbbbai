import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: "./tests",
  testMatch: "browser.spec.js",
  workers: 1,
  timeout: 30000,
  use: {
    channel: "msedge",
    baseURL: "http://127.0.0.1:5178",
    viewport: { width: 1440, height: 900 },
    screenshot: "only-on-failure",
    launchOptions: { args: ["--enable-webgl", "--use-gl=angle", "--use-angle=swiftshader"] },
  },
  projects: [
    { name: "desktop", use: { viewport: { width: 1440, height: 900 } } },
    { name: "full-hd", use: { viewport: { width: 1920, height: 1080 } } },
    { name: "qhd", use: { viewport: { width: 2560, height: 1440 } } },
    { name: "mobile", use: { viewport: { width: 390, height: 844 } } },
  ],
});
