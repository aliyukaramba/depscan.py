import os
import json
import requests
import argparse
from packaging.version import parse

NPM_REGISTRY = "https://registry.npmjs.org"
PYPI_API = "https://pypi.org/pypi"

def check_npm_dependencies(file_path):
    with open(file_path, "r") as f:
        package_json = json.load(f)
    
    dependencies = package_json.get("dependencies", {})
    results = []

    for package, current_version in dependencies.items():
        current_version = current_version.replace("^", "").replace("~", "")
        response = requests.get(f"{NPM_REGISTRY}/{package}")
        
        if response.status_code == 200:
            latest_version = response.json()["dist-tags"]["latest"]
            if parse(current_version) < parse(latest_version):
                results.append((package, current_version, latest_version))
    
    return results

def check_pip_dependencies(file_path):
    results = []

    with open(file_path, "r") as f:
        dependencies = f.readlines()

    for dep in dependencies:
        dep = dep.strip()
        if "==" in dep:
            package, current_version = dep.split("==")
            response = requests.get(f"{PYPI_API}/{package}/json")

            if response.status_code == 200:
                latest_version = response.json()["info"]["version"]
                if parse(current_version) < parse(latest_version):
                    results.append((package, current_version, latest_version))
    
    return results

def scan_dependencies(directory):
    print("\n📦 Scanning dependencies...\n")

    npm_file = os.path.join(directory, "package.json")
    pip_file = os.path.join(directory, "requirements.txt")

    if os.path.exists(npm_file):
        print("🔍 Checking NPM dependencies...")
        npm_results = check_npm_dependencies(npm_file)
        for package, current, latest in npm_results:
            print(f"❌ {package} ({current}) → (Latest: {latest})")

    if os.path.exists(pip_file):
        print("\n🔍 Checking Python dependencies...")
        pip_results = check_pip_dependencies(pip_file)
        for package, current, latest in pip_results:
            print(f"❌ {package} ({current}) → (Latest: {latest})")

    if not npm_results and not pip_results:
        print("✅ All dependencies are up to date!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scan project dependencies for outdated versions")
    parser.add_argument("directory", help="Project directory containing package.json or requirements.txt")
    args = parser.parse_args()

    scan_dependencies(args.directory)
