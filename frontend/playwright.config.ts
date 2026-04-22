import { defineConfig, devices } from "@playwright/test";
import path from "path";

export default defineConfig({
  testDir: "./tests",
  timeout: 60_000,
  expect: {
    timeout: 10_000,
  },
  use: {
    baseURL: "http://127.0.0.1:8765",
    trace: "retain-on-failure",
  },
  webServer: {
    command: ".venv\\Scripts\\python.exe -m uvicorn backend.main:app --port 8765",
    cwd: path.join(__dirname, ".."),
    url: "http://127.0.0.1:8765",
    reuseExistingServer: true,
    timeout: 30_000,
    env: {
      ...process.env,
      DB_PATH: "test-kanban.db",
    },
  },
  projects: [
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"] },
    },
  ],
});
