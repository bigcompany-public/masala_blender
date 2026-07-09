# Download all wheels required by Masala
# Mainly for blender extension

import re
import shutil
import subprocess
from pathlib import Path

root_dir = Path(__file__).parent
dist_dir = root_dir / "dist"
requirements_path = dist_dir / "requirements.txt"
extension_dir = root_dir / "user_default/masala_blender"
wheels_dir = extension_dir / "wheels"
manifest_path = extension_dir / "blender_manifest.toml"


def clear_wheels():
    if wheels_dir.exists():
        shutil.rmtree(wheels_dir)


def main():
    # clear_wheels()
    # download_wheels()
    update_wheels_in_manifest()


def download_wheels():
    subprocess.run(["uv", "export", "--no-hashes", "-o", requirements_path.as_posix()])
    subprocess.run(["pip", "download", "-r", requirements_path.as_posix(), "-d", wheels_dir.as_posix()])


def update_wheels_in_manifest():
    # Get wheels relative paths
    wheels = []
    for wheel in wheels_dir.iterdir():
        if wheel.suffix != ".whl":
            continue
        relative_path = wheel.as_posix().replace(extension_dir.as_posix(), ".")
        wheels.append(relative_path)

    # Replace in manifest file
    content = manifest_path.read_text()
    pattern = re.compile(r"^wheels = (.|\n)+?\]", re.MULTILINE)
    new_wheels_text = "wheels = [\n"
    for wheel in wheels:
        new_wheels_text += f'  "{wheel}",\n'
    new_wheels_text += "]"
    new_content = re.sub(pattern, new_wheels_text, content)
    manifest_path.write_text(new_content)


if __name__ == "__main__":
    main()
