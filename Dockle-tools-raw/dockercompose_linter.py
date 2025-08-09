from collections import defaultdict
import yaml
import re

class ComposeLinter:
    def __init__(self):
        self.smells = defaultdict(list)
        self.data = {}

    def process_file(self, compose_path):
        try:
            with open(compose_path, 'r', encoding='utf-8') as f:
                self.data = yaml.safe_load(f)
                if not isinstance(self.data, dict):
                    self.smells["Invalid Format"].append("The Compose file is not a valid YAML dictionary.")
                    return self.smells
        except FileNotFoundError:
            self.smells["File Not Found"].append(f"The file '{compose_path}' does not exist.")
            return self.smells
        except yaml.YAMLError as e:
            self.smells["Invalid YAML"].append(f"Error parsing YAML: {e}")
            return self.smells

        self._check_all_services()
        self._check_top_level_configs()
        return self.smells

    def _check_all_services(self):
        services = self.data.get('services', {})
        if not services:
            self.smells["Configuration"].append("No 'services' are defined in the Compose file.")
            return

        for name, config in services.items():
            if not isinstance(config, dict): continue
            self._check_service_image(name, config)
            self._check_service_restart_policy(name, config)
            self._check_service_security(name, config)
            self._check_service_build_and_naming(name, config)
            self._check_service_resources(name, config)
            self._check_service_healthcheck(name, config)
            self._check_service_volumes(name, config)
            
    def _check_service_image(self, name, config):
        image = config.get('image')
        if image and (':' not in image or image.endswith(':latest')):
            self.smells["Best Practices"].append(f"Service '{name}': Uses a mutable image tag ('latest'). Pin to a specific version.")
            
    def _check_service_restart_policy(self, name, config):
        if 'restart' not in config:
            self.smells["Reliability"].append(f"Service '{name}': No restart policy is set. Consider 'unless-stopped'.")

    def _check_service_security(self, name, config):
        if config.get('privileged'):
            self.smells["Security"].append(f"Service '{name}': 'privileged: true' is highly insecure and should be avoided.")
        
        env = config.get('environment', [])
        if isinstance(env, dict): env = [f"{k}={v}" for k, v in env.items()]
        
        for var in env:
            if re.search(r'^(PASSWORD|SECRET|TOKEN|API_KEY)=', var, re.IGNORECASE):
                self.smells["Security"].append(f"Service '{name}': A secret appears to be hardcoded in environment variables. Use Docker secrets or an env_file.")
                break
        
        vols = config.get('volumes', [])
        for vol in vols:
            if isinstance(vol, str) and 'docker.sock' in vol:
                self.smells["Security"].append(f"Service '{name}': Mounting the Docker socket is a security risk.")

    def _check_service_build_and_naming(self, name, config):
        if 'container_name' in config:
            self.smells["Best Practices"].append(f"Service '{name}': Avoid using 'container_name' as it prevents scaling.")
        if 'links' in config:
            self.smells["Legacy Features"].append(f"Service '{name}': 'links' is a legacy feature. Use user-defined networks instead.")

    def _check_service_resources(self, name, config):
        try:
            limits = config['deploy']['resources']['limits']
            if 'cpus' not in limits or 'memory' not in limits:
                self.smells["Resource Management"].append(f"Service '{name}': Resource limits for CPU or memory are defined but incomplete.")
        except (KeyError, TypeError):
             self.smells["Resource Management"].append(f"Service '{name}': No CPU or memory limits are set under 'deploy.resources.limits'.")

    def _check_service_healthcheck(self, name, config):
        if 'healthcheck' not in config:
             self.smells["Reliability"].append(f"Service '{name}': Missing a 'healthcheck' to verify service health.")

    def _check_service_volumes(self, name, config):
        vols = config.get('volumes', [])
        db_images = ['postgres', 'mysql', 'mariadb', 'mongo', 'redis']
        if any(db in config.get('image', '') for db in db_images):
            for vol in vols:
                if isinstance(vol, str) and vol.startswith(('./', '/')):
                     self.smells["Data Persistence"].append(f"Service '{name}': Uses a host-bind mount for database data. Prefer named volumes.")

    def _check_top_level_configs(self):
        services = self.data.get('services', {})
        if len(services) > 1 and 'networks' not in self.data:
            self.smells["Networking"].append("Multiple services are defined but they are not using a user-defined network.")
