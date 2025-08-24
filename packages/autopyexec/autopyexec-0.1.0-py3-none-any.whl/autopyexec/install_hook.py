import os
import sys
import platform
import subprocess

def setup_file_association():
    system = platform.system()

    if system in ["Linux", "Darwin"]:  # Linux or macOS
        print("🔧 Setting up autopyexec for Linux/macOS...")

        # Add shebang automatically if missing
        for filename in os.listdir("."):
            if filename.endswith(".py"):
                try:
                    with open(filename, "r+", encoding="utf-8") as f:
                        content = f.read()
                        if not content.startswith("#!"):
                            f.seek(0, 0)
                            f.write("#!/usr/bin/env python3\n" + content)
                            print(f"✅ Added shebang to {filename}")
                    os.chmod(filename, 0o755)
                except Exception as e:
                    print(f"⚠️ Could not update {filename}: {e}")

        print("✅ Now you can run ./filename.py")

    elif system == "Windows":
        print("🔧 Setting up autopyexec for Windows...")
        python_path = sys.executable.replace("\\", "\\\\")
        try:
            subprocess.run("assoc .py=Python.File", shell=True, check=True)
            subprocess.run(
                f'ftype Python.File="{python_path}" "%1" %*',
                shell=True, check=True
            )
            print(f"✅ Associated .py with {python_path}")
            print("✅ Now you can run filename.py directly in CMD/PowerShell")
        except Exception as e:
            print(f"⚠️ Could not update file associations: {e}")
    else:
        print(f"❌ Unsupported OS: {system}")


if __name__ == "__main__":
    setup_file_association()
