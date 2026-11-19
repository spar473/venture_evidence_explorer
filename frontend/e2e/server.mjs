/** Disposable browser-test database: never migrate or replace the user's evidence. */
import { spawn, spawnSync } from "node:child_process";
import { mkdtempSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const root = resolve(dirname(fileURLToPath(import.meta.url)), "../..");
const temp = mkdtempSync(join(tmpdir(), "vee-browser-"));
const python = process.env.VEE_PYTHON || "python3";
const db = join(temp, "browser.sqlite");
const bootstrap = spawnSync(python, ["scripts/bootstrap.py", "--db", db, "--output-dir", temp], {cwd: root, stdio: "inherit"});
if (bootstrap.status !== 0 || bootstrap.error) {
  rmSync(temp, {recursive: true, force: true});
  if (bootstrap.error) console.error(bootstrap.error.message);
  process.exit(bootstrap.status || 1);
}
const research = spawnSync(python, ["scripts/import_research.py", "--input", "research/framework-v0.2.1/Two_Dossier_Research_Example.json", "--db", db, "--as-of", "2026-11-18", "--apply"], {cwd: root, stdio: "inherit"});
if (research.status !== 0 || research.error) {
  rmSync(temp, {recursive: true, force: true});
  if (research.error) console.error(research.error.message);
  process.exit(research.status || 1);
}
const healthtech = spawnSync(python, ["scripts/import_research.py", "--input", "research/healthtech-pilot/packet.json", "--db", db, "--as-of", "2026-11-19", "--apply", "--report", join(temp, "healthtech-import.json")], {cwd: root, stdio: "inherit"});
if (healthtech.status !== 0 || healthtech.error) {rmSync(temp,{recursive:true,force:true}); process.exit(healthtech.status || 1);}
const extension = spawnSync(python, ["scripts/import_research.py", "--input", "research/healthtech-pilot/extension.json", "--db", db, "--as-of", "2026-11-19", "--apply", "--report", join(temp, "healthtech-extension.json")], {cwd: root, stdio: "inherit"});
if (extension.status !== 0 || extension.error) {rmSync(temp,{recursive:true,force:true}); process.exit(extension.status || 1);}
const discovery = spawnSync(python, ["scripts/import_discovery.py", "--db", db, "--as-of", "2026-11-18", "--apply"], {cwd: root, stdio: "inherit"});
if (discovery.status !== 0 || discovery.error) {rmSync(temp,{recursive:true,force:true}); process.exit(discovery.status || 1);}
const child = spawn(python, ["scripts/serve.py", "--port", process.env.VEE_TEST_PORT || "8138"], {cwd: root, env: {...process.env, VEE_DB: db}, stdio: "inherit"});
for (const signal of ["SIGTERM", "SIGINT"]) process.on(signal, () => child.kill(signal));
child.on("exit", code => {rmSync(temp, {recursive: true, force: true}); process.exit(code || 0);});
child.on("error", error => {console.error(error.message); rmSync(temp, {recursive: true, force: true}); process.exit(1);});
