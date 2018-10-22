import sys
from deploy_package import DeployPackage

if __name__ == '__main__':
    config_path = sys.argv[1] if len(sys.argv) > 1 else "./config/config.json"
    package = DeployPackage(config_path)
    package.perform_deployment()
