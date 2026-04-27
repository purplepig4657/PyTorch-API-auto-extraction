import os
import glob
import shutil
import json
import sys
import argparse

def bootstrap_local_site_packages() -> None:
    project_root = os.path.dirname(os.path.abspath(__file__))
    pattern = os.path.join(project_root, "venv", "lib", "python*", "site-packages")
    for site_packages in sorted(glob.glob(pattern), reverse=True):
        if site_packages not in sys.path:
            sys.path.insert(0, site_packages)


def ensure_supported_python() -> None:
    if sys.version_info >= (3, 10):
        return

    python311 = shutil.which("python3.11")
    if python311 is None:
        raise RuntimeError(
            "PyTorch 2.11 source parsing requires Python 3.10+ because the source tree uses match/case syntax."
        )

    env = os.environ.copy()
    current_site_packages = next((path for path in sys.path if "site-packages" in path), None)
    if current_site_packages is not None:
        existing = env.get("PYTHONPATH", "")
        env["PYTHONPATH"] = current_site_packages if existing == "" else f"{current_site_packages}:{existing}"

    os.execvpe(python311, [python311, __file__, *sys.argv[1:]], env)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--library", choices=["pytorch", "numpy"], default="pytorch")
    return parser.parse_args()


def main() -> None:
    bootstrap_local_site_packages()
    ensure_supported_python()
    from src.common.classified_result import classified_result
    from src.common.library_spec import get_library_spec
    from src.comparison.compare import Compare

    args = parse_args()
    compare = Compare(classified_result, library_spec=get_library_spec(args.library))
    result = compare.compare()
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
