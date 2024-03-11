import toml
import subprocess

def upgrade_package(package_name):
    """Upgrades a single package to its latest version"""
    try:
        result = subprocess.run(
            ["poetry", "add", f"{package_name}@latest"],
            capture_output=True,
            text=True,
            check=True
        )
        print(f"({package_name}) -> {result.stdout}")
    except subprocess.CalledProcessError as e:
        print(f"Error upgrading {package_name}: {e.stderr}")

def main():
    """Main logic for upgrading packages in pyproject.toml"""
    with open("pyproject.toml", "r") as f:
        data = toml.load(f)

    dependencies = data.get("tool", {}).get("poetry", {}).get("dependencies", {})
    dev_dependencies = data.get("tool", {}).get("poetry", {}).get("dev-dependencies", {})

    # Upgrade regular dependencies
    for package in dependencies:
        upgrade_package(package)

    # Upgrade dev dependencies
    for package in dev_dependencies:
        upgrade_package(package)

if __name__ == "__main__":
    main()