from skbuild import setup

setup(
    name="loudstream",
    version="0.3.1",
    packages=["loudstream"],
    package_dir={"": "src"},
    cmake_install_dir="src/loudstream",
)
