"""Kubernetes interaction module for port forwarding."""

from typing import Dict, List, Optional, Tuple

import questionary
from kubernetes import client, config
from kubernetes.client.rest import ApiException
from questionary import Style

FZF_STYLE = Style(
    [
        ("qmark", "fg:#673ab7 bold"),  # token in front of the question
        # Main question/prompt
        ("question", "bold"),
        ("instruction", "italic fg:#666666"),
        # Selected item (highlighted)
        ("selected", "fg:#ffffff bg:#005577 bold"),
        # Pointer/cursor (similar to fzf's >)
        ("pointer", "fg:#005577 bold"),
        # Normal items
        ("", "fg:#cccccc"),
        # Answer (what was selected)
        ("answer", "fg:#00aa00 bold"),
        # Disabled items
        ("disabled", "italic fg:#666666"),
        # Text input
        ("text", "fg:#ffffff"),
        # Fuzzy search match highlighting
        ("fuzzy-match", "fg:#ffff00 bold"),
        # Validation errors
        ("validation-error", "fg:#ff0000 bold"),
        ("separator", "fg:#cc5454"),  # separator in lists
    ]
)


class KubernetesPortForward:
    """Handle Kubernetes operations for port forwarding."""

    def __init__(self, context: Optional[str] = None):
        """Initialize Kubernetes client."""
        self.v1: Optional[client.CoreV1Api] = None
        self.current_context = context
        self._load_config()

    def _load_config(self) -> None:
        """Load Kubernetes configuration."""
        try:
            # Load from kubeconfig file with optional context
            config.load_kube_config(context=self.current_context)
            if self.current_context:
                print(
                    f"✓ Loaded Kubernetes config with context: {self.current_context}"
                )
            else:
                print("✓ Loaded Kubernetes config from kubeconfig")
        except config.ConfigException as e:
            print(f"❌ Failed to load Kubernetes config: {e}")
            raise

        self.v1 = client.CoreV1Api()

    @staticmethod
    def get_available_contexts() -> List[Dict[str, str]]:
        """Get all available Kubernetes contexts."""
        try:
            contexts, active_context = config.list_kube_config_contexts()
            context_list = []

            for context in contexts:
                context_info = {
                    "name": context["name"],
                    "cluster": context["context"].get("cluster", "unknown"),
                    "user": context["context"].get("user", "unknown"),
                    "namespace": context["context"].get("namespace", "default"),
                    "active": context["name"] == active_context["name"]
                    if active_context
                    else False,
                }
                context_list.append(context_info)

            return context_list
        except config.ConfigException as e:
            print(f"❌ Error fetching contexts: {e}")
            return []

    @staticmethod
    def get_current_context() -> Optional[str]:
        """Get the currently active Kubernetes context."""
        try:
            _, active_context = config.list_kube_config_contexts()
            return active_context["name"] if active_context else None
        except config.ConfigException:
            return None

    def get_namespaces(self) -> List[str]:
        """Get all available namespaces."""
        if not self.v1:
            print("❌ Kubernetes client not initialized")
            return []

        try:
            namespaces = self.v1.list_namespace()
            return [ns.metadata.name for ns in namespaces.items]
        except ApiException as e:
            print(f"❌ Error fetching namespaces: {e}")
            return []

    def get_pods(self, namespace: str) -> List[Dict[str, str]]:
        """Get all pods in a namespace."""
        if not self.v1:
            print("❌ Kubernetes client not initialized")
            return []

        try:
            pods = self.v1.list_namespaced_pod(namespace=namespace)
            pod_list = []
            for pod in pods.items:
                if pod.status.phase == "Running":
                    pod_info = {
                        "name": pod.metadata.name,
                        "status": pod.status.phase,
                        "ready": self._get_pod_ready_status(pod),
                    }
                    pod_list.append(pod_info)
            return pod_list
        except ApiException as e:
            print(f"❌ Error fetching pods: {e}")
            return []

    def get_services(self, namespace: str) -> List[Dict[str, str]]:
        """Get all services in a namespace."""
        if not self.v1:
            print("❌ Kubernetes client not initialized")
            return []

        try:
            services = self.v1.list_namespaced_service(namespace=namespace)
            service_list = []
            for svc in services.items:
                ports = []
                if svc.spec.ports:
                    ports = [
                        f"{port.port}:{port.target_port}" for port in svc.spec.ports
                    ]

                service_info = {
                    "name": svc.metadata.name,
                    "type": svc.spec.type,
                    "ports": ", ".join(ports) if ports else "None",
                }
                service_list.append(service_info)
            return service_list
        except ApiException as e:
            print(f"❌ Error fetching services: {e}")
            return []

    def get_pod_ports(self, namespace: str, pod_name: str) -> List[int]:
        """Get available ports for a pod."""
        if not self.v1:
            print("❌ Kubernetes client not initialized")
            return [8080]

        try:
            pod = self.v1.read_namespaced_pod(name=pod_name, namespace=namespace)
            ports = []

            if pod.spec.containers:
                for container in pod.spec.containers:
                    if container.ports:
                        for port in container.ports:
                            if port.container_port:
                                ports.append(port.container_port)

            return sorted(list(set(ports))) if ports else [8080]  # Default port
        except ApiException as e:
            print(f"❌ Error fetching pod ports: {e}")
            return [8080]

    def get_service_ports(
        self, namespace: str, service_name: str
    ) -> List[Tuple[int, int]]:
        """Get available ports for a service (port, target_port)."""
        if not self.v1:
            print("❌ Kubernetes client not initialized")
            return [(80, 8080)]

        try:
            service = self.v1.read_namespaced_service(
                name=service_name, namespace=namespace
            )
            ports = []

            if service.spec.ports:
                for port in service.spec.ports:
                    target_port = port.target_port
                    if isinstance(target_port, str):
                        # If target_port is a string (named port), use the port number
                        target_port = port.port
                    ports.append((port.port, target_port))

            return ports if ports else [(80, 8080)]  # Default ports
        except ApiException as e:
            print(f"❌ Error fetching service ports: {e}")
            return [(80, 8080)]

    def _get_pod_ready_status(self, pod) -> str:
        """Get the ready status of a pod."""
        if not pod.status.conditions:
            return "Unknown"

        for condition in pod.status.conditions:
            if condition.type == "Ready":
                return "Ready" if condition.status == "True" else "Not Ready"

        return "Unknown"


def interactive_port_forward() -> Optional[str]:
    """Interactive questionary flow for port forwarding setup with fzf-like interface."""

    print("🔍 Kubernetes Port Forward (fzf-style)")
    print("═" * 45)
    print("💡 Use 'q' or 'Esc' to quit at any step")
    print()

    # Step 0: Select Kubernetes context (if not in-cluster)

    contexts = KubernetesPortForward.get_available_contexts()
    if not contexts:
        print("❌ No Kubernetes contexts found")
        return None

    if len(contexts) == 1:
        # Only one context available, use it directly
        selected_context = contexts[0]["name"]
        print(f"✓ Using context: {selected_context}")
    else:
        # Multiple contexts, let user choose with fzf-like interface
        context_choices = []
        for ctx in contexts:
            display = f"{ctx['name']}"
            if ctx["active"]:
                display += " *"  # Mark active context
            display += f" [{ctx['cluster']}]"
            context_choices.append(questionary.Choice(display, ctx["name"]))

        selected_context = fzf_select_from_choices(
            "select kubernetes context:", context_choices
        )

        if not selected_context:
            print("👋 Context selection cancelled")
            return None

        try:
            k8s = KubernetesPortForward(context=selected_context)
        except Exception as e:
            print(f"❌ Failed to initialize Kubernetes client: {e}")
            return None

    # Step 1: Select namespace with fuzzy search
    namespaces = k8s.get_namespaces()
    if not namespaces:
        print("❌ No namespaces found")
        return None

    namespace = fzf_select_from_choices("Select namespace:", namespaces)

    if not namespace:
        print("👋 Namespace selection cancelled")
        return None

    # Step 2: Select resource type
    resource_choices = [
        questionary.Choice("pod", "pod"),
        questionary.Choice("service", "service"),
    ]

    resource_type = fzf_select_from_choices("Select resource type:", resource_choices)

    if not resource_type:
        print("👋 Resource type selection cancelled")
        return None

    # Step 3: Select specific resource
    if resource_type == "pod":
        pods = k8s.get_pods(namespace)
        if not pods:
            print(f"❌ No running pods found in namespace '{namespace}'")
            return None

        # Create choices with status info
        pod_choices = []
        for pod in pods:
            display = f"{pod['name']} [{pod['status']}, {pod['ready']}]"
            pod_choices.append(questionary.Choice(display, pod["name"]))

        selected_resource = fzf_select_from_choices("Select pod:", pod_choices)

        if not selected_resource:
            print("👋 Pod selection cancelled")
            return None

        # Get pod ports
        ports = k8s.get_pod_ports(namespace, selected_resource)

        if len(ports) > 1:
            port_choices = [questionary.Choice(str(port), str(port)) for port in ports]
            selected_port = fzf_select_from_choices("Select port:", port_choices)

            if not selected_port:
                print("👋 Port selection cancelled")
                return None

            container_port = int(selected_port)
        else:
            container_port = ports[0]

        # Ask for local port with fzf-like input
        try:
            local_port_str = questionary.text(
                f"Enter local port [{container_port}]: ",
                default=str(container_port),
                style=FZF_STYLE,
                instruction=" (Enter for default, Ctrl+C to cancel)",
            ).ask()
        except (KeyboardInterrupt, EOFError):
            print("👋 Local port input cancelled")
            return None

        if local_port_str is None:
            return None

        local_port = local_port_str or str(container_port)

        # Generate kubectl command
        kubectl_command = f"kubectl port-forward -n {namespace} pod/{selected_resource} {local_port}:{container_port}"

    else:  # service
        services = k8s.get_services(namespace)
        if not services:
            print(f"❌ No services found in namespace '{namespace}'")
            return None

        service_choices = []
        for svc in services:
            display = f"{svc['name']} [{svc['type']}] {svc['ports']}"
            service_choices.append(questionary.Choice(display, svc["name"]))

        selected_resource = fzf_select_from_choices("Select service:", service_choices)

        if not selected_resource:
            print("👋 Service selection cancelled")
            return None

        # Get service ports
        service_ports = k8s.get_service_ports(namespace, selected_resource)

        if len(service_ports) > 1:
            port_choices = []
            for port, target_port in service_ports:
                display = f"{port}:{target_port}"
                port_choices.append(
                    questionary.Choice(display, f"{port}:{target_port}")
                )

            selected_port_pair = fzf_select_from_choices(
                "Select port mapping:", port_choices
            )

            if not selected_port_pair:
                print("👋 Port mapping selection cancelled")
                return None

            service_port, target_port = map(int, selected_port_pair.split(":"))
        else:
            service_port, target_port = service_ports[0]

        # Ask for local port
        try:
            local_port_str = questionary.text(
                f"Enter local port [{service_port}]: ",
                default=str(service_port),
                style=FZF_STYLE,
                instruction=" (Enter for default, Ctrl+C to cancel)",
            ).ask()
        except (KeyboardInterrupt, EOFError):
            print("👋 Local port input cancelled")
            return None

        if local_port_str is None:
            return None

        local_port = local_port_str or str(service_port)

        # Generate kubectl command
        kubectl_command = f"kubectl port-forward -n {namespace} service/{selected_resource} {local_port}:{service_port}"

    return kubectl_command


def fzf_select(
    message: str, choices: List[str], allow_quit: bool = True
) -> Optional[str]:
    """FZF-like selection with fuzzy search and quit capability."""
    try:
        result = questionary.autocomplete(
            message,
            choices=choices,
            style=FZF_STYLE,
            validate=lambda x: x in choices if x else True,
            # Enable fuzzy matching
            match_middle=True,
        ).ask()

        # Handle quit scenarios
        if not result and allow_quit:
            return None

        return result
    except (KeyboardInterrupt, EOFError):
        if allow_quit:
            return None
        raise


def fzf_select_from_choices(
    message: str, choices: List[questionary.Choice], allow_quit: bool = True
) -> Optional[str]:
    """FZF-like selection with questionary.Choice objects."""
    try:
        result = questionary.select(
            message,
            choices=choices,
            style=FZF_STYLE,
            qmark="> ",
            # Enable keyboard shortcuts and navigation
            use_shortcuts=False,
            use_arrow_keys=True,
            use_jk_keys=True,  # vim-like j/k navigation
            use_emacs_keys=False,
            # Show instruction
            instruction=" (↑↓/jk to navigate, Enter to select"
            + (", q/Esc to quit" if allow_quit else "")
            + ")",
        ).ask()

        return result
    except (KeyboardInterrupt, EOFError):
        pass


def run_interactive_port_forward():
    print("🚀 Kubernetes Port Forward Setup")

    # Show current context info if available
    try:
        current_context = KubernetesPortForward.get_current_context()
        if current_context:
            print(f"📍 Current context: {current_context}")
        print()
    except Exception:
        pass  # Ignore if we can't get context info

    try:
        command = interactive_port_forward()

        if command:
            print("\n✅ Port forward command generated:")
            print(f"📋 {command}")
            print(
                "\n💡 Copy and run this command in your terminal to start port forwarding."
            )

            # Ask if user wants to save to database
            try:
                save_choice = (
                    input("\n� Save this configuration? [Y/n]: ").lower().strip()
                )
                if save_choice in ["", "y", "yes"]:
                    from pof.service import PortForwardService

                    service = PortForwardService()

                    # Extract details from command for database
                    if "pod/" in command:
                        resource_type = "pod"
                        resource_name = command.split("pod/")[1].split()[0]
                    elif "service/" in command:
                        resource_type = "service"
                        resource_name = command.split("service/")[1].split()[0]
                    else:
                        resource_type = "unknown"
                        resource_name = "unknown"

                    # Extract namespace and ports
                    namespace_part = (
                        command.split("-n ")[1].split()[0]
                        if "-n " in command
                        else "default"
                    )
                    port_mapping = command.split()[
                        -1
                    ]  # Last argument should be port mapping
                    local_port, remote_port = map(int, port_mapping.split(":"))

                    # Extract context if present
                    context_name = (
                        command.split("--context ")[1].split()[0]
                        if "--context " in command
                        else None
                    )

                    entry = service.create_k8s_entry(
                        namespace=namespace_part,
                        resource_name=resource_name,
                        resource_type=resource_type,
                        local_port=local_port,
                        remote_port=remote_port,
                        context=context_name,
                    )

                    print(f"✅ Saved as '{entry.name}' (ID: {entry.id_})")
                    print("   Use 'pof status' to view all saved configurations")

            except (KeyboardInterrupt, EOFError):
                pass  # User cancelled
            except Exception as e:
                print(f"❌ Failed to save configuration: {e}")

        else:
            print("❌ Port forward setup cancelled or failed.")

    except KeyboardInterrupt:
        print("\n👋 Setup cancelled by user.")
    except Exception as e:
        print(f"❌ An error occurred: {e}")


if __name__ == "__main__":
    run_interactive_port_forward()
