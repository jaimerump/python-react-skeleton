# Dev orchestrator. Turns the compose files into a live-reloading environment and
# re-implements the boot ordering Tilt doesn't honor from Compose `depends_on`.

load('ext://dotenv', 'dotenv')

# Load the existing .env; we deliberately do NOT regenerate it on every `tilt up`
# (that would clobber hand-edits / write literal {{PLACEHOLDER}}s). Regenerate manually:
#   local('./scripts/generate-env.sh -f')
if not os.path.exists('.env'):
    fail("No .env found. Run ./scripts/generate-env.sh first.")
dotenv()

# --- Flags: a tilt arg OR an env var ---
config.define_bool("no-localstack")      # opt-OUT; LocalStack is ON by default
config.define_string("instance")         # or INSTANCE (default "1")
config.define_string("port-increment")   # or TILT_PORT_INCREMENT (default "100")
cfg = config.parse()

no_localstack = cfg.get("no-localstack", os.getenv("TILT_NO_LOCALSTACK") == "1")
instance = int(cfg.get("instance", os.getenv("INSTANCE", "1")))
increment = int(cfg.get("port-increment", os.getenv("TILT_PORT_INCREMENT", "100")))

if increment not in (1, 100):
    fail("port-increment must be 1 (dense) or 100 (sparse); got %d" % increment)
if instance < 1 or instance > 99:
    fail("instance must be between 1 and 99; got %d" % instance)

# --- Port formula: the single source of truth (mirrored by the cleanup scripts) ---
offset = (instance - 1) * increment
ports = {
    "DB_PORT": 5432 + offset,
    "API_PORT": 8000 + offset,
    "UI_PORT": 5173 + offset,
    "LOCALSTACK_PORT": 4566 + offset,
}
tilt_port = 10350 + offset  # bound by the launcher (scripts/tilt-auto.sh), not here
for name, value in ports.items():
    os.environ[name] = str(value)

# --- Per-instance isolation ---
os.environ["COMPOSE_PROJECT_NAME"] = "app-" + str(instance)
image_suffix = "" if instance == 1 else "-" + str(instance)
api_image = "app_api" + image_suffix
ui_image = "app_ui" + image_suffix
os.environ["API_IMAGE"] = api_image
os.environ["UI_IMAGE"] = ui_image

# --- Overlay assembly ---
compose_files = ['docker-compose.yml']
if not no_localstack:
    compose_files.append('docker-compose.localstack.yml')
docker_compose(compose_files)

# --- Live-update image builds (hot reload without full rebuilds) ---
docker_build(
    api_image, '.', dockerfile='./Dockerfile',
    only=['./src', './migrations', './alembic.ini', './pyproject.toml', './uv.lock'],
    live_update=[
        sync('./src', '/app/src'),
        run('uv sync', trigger=['./pyproject.toml', './uv.lock']),
    ],
)
docker_build(
    ui_image, './ui', dockerfile='./ui/Dockerfile', target='dev',
    only=['./src', './package.json', './package-lock.json', './index.html',
          './vite.config.ts', './tsconfig.json', './tsconfig.app.json',
          './tsconfig.node.json', './postcss.config.js', './tailwind.config.ts'],
    live_update=[
        sync('./ui/src', '/app/src'),
        run('npm install', trigger=['./ui/package.json']),
    ],
)

# --- Boot order re-declared (Tilt ignores Compose depends_on conditions) ---
dc_resource('migrations', trigger_mode=TRIGGER_MODE_AUTO)
dc_resource('api', resource_deps=['migrations'])
dc_resource('ui', resource_deps=['api'])
if not no_localstack:
    dc_resource('localstack-init', resource_deps=['localstack'])
    dc_resource('worker', resource_deps=['migrations', 'localstack-init'])

print("Instance %d | API :%d | UI :%d | Tilt UI :%d" % (
    instance, ports["API_PORT"], ports["UI_PORT"], tilt_port))
