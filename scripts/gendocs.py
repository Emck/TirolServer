import shutil
import subprocess
from pathlib import Path

# Modules to export
MODULES = [
	"tirolserver.config",
	"tirolserver.core",
	"tirolserver.dirtyapp",
	"tirolserver.routers",
	"tirolserver.utils",
	"tirolserver.server",
]
OUTPUT_DIR = Path("docs/content")


def cleanup_output():
	if OUTPUT_DIR.exists():
		print(f"🧹 Cleaning up old documentation in: {OUTPUT_DIR}...")
		shutil.rmtree(OUTPUT_DIR)
	OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
	print("✨ Output directory ready.")


def griffe2md():
	output_path = Path("docs/content")
	output_path.mkdir(parents=True, exist_ok=True)

	for module in MODULES:
		print(f"📄 Exporting {module}...")
		cmd = [
			"griffe2md",
			module,
			"-f",
			"--mdformat-extensions",
			"tables",
			"-o",
			f"docs/content/{module.split('.')[-1]}.md",
		]
		subprocess.run(cmd)

	print("📄 Generate Documentation finished.")


def main():
	cleanup_output()
	griffe2md()


if __name__ == "__main__":
	main()
