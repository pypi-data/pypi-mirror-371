from setuptools import setup, find_packages
import sys

def run_post_install():
    try:
        import autopyexec.install_hook as hook
        hook.setup_file_association()
    except Exception as e:
        print("⚠️ Post-install hook failed:", e)

setup(
    name="autopyexec",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[],
    python_requires=">=3.6",
    author="Ganu Reddy",
    author_email="ganureddy54@email.com",
    description="Run .py files directly without typing python",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/ganureddy/autopyexec",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)

# Run post-install (risky!)
if "install" in sys.argv:
    run_post_install()
