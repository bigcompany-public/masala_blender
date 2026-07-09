import os
import subprocess
from pathlib import Path


def main():
    current_dir = Path(__file__).parent
    env = os.environ.copy()

    # Set executable
    exe = Path(r"C:\Program Files\Blender Foundation\Blender 5.1\blender.exe")

    # Set extensions path
    # WARNING : Blender needs a user_default subdir
    env["BLENDER_USER_EXTENSIONS"] = str(current_dir)

    # Set pythonpath
    # lib_path = current_dir / ".venv/Lib/site-packages"
    # env["PYTHONPATH"] = lib_path.as_posix()
    env["PYTHONPATH"] = r"D:\gitWorkspace\masala\src"

    # Open Blender with a separate console and hide console by default
    # This must be done so blender doesn't use bluepepper's console and so "toggle system console" works as intended
    flag = subprocess.CREATE_NEW_CONSOLE
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    startupinfo.wShowWindow = subprocess.SW_HIDE

    command = [
        str(exe),
        "--python-use-system-env",
        # "--factory-startup",
    ]
    # Enable masala_blender by default
    command += ["--addons", "bl_ext.user_default.masala_blender"]

    subprocess.Popen(
        command,
        env=env,
        creationflags=flag,
        startupinfo=startupinfo,
    )


if __name__ == "__main__":
    main()
