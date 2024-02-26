"""
This requires invoke to be installed on the machine (not venv), which can be
done via:
    pipx install invoke
"""
from os.path import join
from invoke import task
from hashlib import md5
from pathlib import Path
from typing import Optional
from shutil import rmtree


PROJECT: str = "Hello"
MD5: Optional[str] = None
BUILD_PATH: Optional[Path] = None
INSTALL_PATH: Optional[Path] = None
SRC_PATH: Path = Path(__file__).parent
# WORKSPACE: Path = Path("/tmp/builds/app")
WORKSPACE: Path = Path("./target")
VCPKG_TOOLCHAIN = SRC_PATH / "vcpkg/scripts/buildsystems/vcpkg.cmake"


def get_md5(content: str) -> str:
    global MD5
    if MD5 is None:
        MD5 = md5(str.encode(content)).hexdigest()
    return MD5


def get_cmake_workspace() -> Path:
    hash = get_md5(str(SRC_PATH))
    return WORKSPACE / f"{PROJECT}_{SRC_PATH.name}_{hash}"


def get_build_path() -> Path:
    global BUILD_PATH
    if BUILD_PATH is None:
        BUILD_PATH = get_cmake_workspace() / "build"
    return BUILD_PATH


def get_install_path() -> Path:
    global INSTALL_PATH
    if INSTALL_PATH is None:
        INSTALL_PATH = get_cmake_workspace() / "install"
    return INSTALL_PATH


@task
def info(c, topic="all"):
    """Show priject info."""
    if topic == "all":
        print(f"Project        = {PROJECT}")
        print(f"Source path    = {SRC_PATH}")
        print(f"Build path     = {get_build_path()}")
        print(f"Install path   = {get_install_path()}")
    elif topic == "build_path":
        print(get_build_path())
    elif topic == "install_path":
        print(get_install_path())
    else:
        print("Error: Valid 'topic' names are 'build_path'/'install_path'")


@task
def config(c):
    """Run cmake configure."""
    do_config(c)


def do_config(c):
    build_path = get_build_path()
    build_path.mkdir(parents=True, exist_ok=True)
    cmd = [
        "cmake",
        "-S",
        str(SRC_PATH),
        "-B",
        str(build_path),
        "-GNinja",
        "-DCMAKE_BUILD_TYPE=RelWithDebInfo",
        "-DCMAKE_EXPORT_COMPILE_COMMANDS=1",
        f"-DCMAKE_TOOLCHAIN_FILE={str(VCPKG_TOOLCHAIN)}",
    ]
    c.run(" ".join(cmd), pty=True)

    # Symlink compile_commands.json
    src_ccdb_file = SRC_PATH / "compile_commands.json"
    build_ccdb_file = build_path / "compile_commands.json"
    if build_ccdb_file.exists():
        if not src_ccdb_file.exists():
            src_ccdb_file.symlink_to(build_ccdb_file)


@task(help={"config": "Whether to generate config"})
def build(c, config=False):
    """Run builds via cmake."""
    build_path = get_build_path()

    if not build_path.exists():
        if config:
            do_config(c)
        else:
            print("Error: build path doesn't exist.")
            return

    cmd = ["cmake", "--build", str(build_path)]
    c.run(" ".join(cmd), pty=True)


@task(help={"exec_path": "path of exe. eg: src/app"})
def run(c, exec_path, **kwargs):
    """Run main exe in build path."""
    build_path = get_build_path()
    if not build_path.exists():
        print("Need build first ...")
        return
    app_path = build_path / exec_path
    cmd_str = f"./{str(app_path)}"
    cmd = [cmd_str] + [f"{value}" for key, value in kwargs.items()]
    c.run(" ".join(cmd), pty=True)


@task
def install(c):
    """Run install via cmake."""
    build_path = get_build_path()
    install_path = get_install_path()

    if not build_path.exists():
        print("Error: build path doesn't exist.")
        return

    cmd = ["cmake", "--install", str(build_path)]
    c.run(" ".join(cmd), env={"DESTDIR": install_path}, pty=True)


@task
def clean(c):
    """Clean build directory."""
    build_path = get_build_path()
    if build_path.exists():
        rmtree(build_path)
        print(f"Cleaned {build_path}")
    else:
        print("Build path absent. Nothing todo.")


@task(pre=[clean])
def clean_all(c):
    """Clean build and install directory."""
    install_path = get_install_path()
    if install_path.exists():
        rmtree(install_path)
        print(f"Cleaned {install_path}")
    else:
        print("Install path absent. Nothing todo.")


@task
def ls(c):
    """List files using lsd and skip vcpkg and .cache folder."""
    cmd = [
        "lsd",
        "--tree",
        "--ignore-glob vcpkg",
        "--ignore-glob .cache",
        "--ignore-glob vcpkg_installed",
    ]
    c.run(" ".join(cmd), pty=True)
