import signal
from typing import Optional, Self

import questionary

from pof.command.base import CommandContext
from pof.k8s import (
    KubernetesPortForward,
    fzf_select_from_choices,
    run_interactive_port_forward,
)
from pof.models import PofError


class CommandK8s(CommandContext):
    """
    Builder for Kubernetes port forwarding configurations.
    """

    def __init__(self):
        super().__init__()
        self.context: Optional[str] = None
        self.namespace: Optional[str] = None
        self.service: Optional[str] = None
        self.pod: Optional[str] = None

    @classmethod
    def build(
        cls,
        *,
        port_from: int,
        port_to: int,
        context: str,
        namespace: str,
        service: Optional[str],
        pod: Optional[str],
    ) -> Self:
        """
        Build the port forwarding command for Kubernetes.
        """
        instance = cls()
        instance.port_from = port_from
        instance.port_to = port_to
        # kubernetes-specific options
        instance.context = context
        instance.namespace = namespace
        instance.service = service
        instance.pod = pod
        return instance

    def setup(self):
        pass

    @classmethod
    def interactive(cls):
        raise PofError("interactive mode is not supported yet")
        instance = cls()
        run_interactive_port_forward()
        context = cls._i_get_context()
        namespace = cls._i_get_namespace()
        instance.context = context
        instance.namespace = namespace
        return instance

    @staticmethod
    def _i_get_context():
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
        return selected_context

    @staticmethod
    def _i_get_namespace():
        return "default"

    @property
    def command(self) -> str:
        if self.service:
            command = f"kubectl port-forward -n {self.namespace} service/{self.service} {self.port_to}:{self.port_from}"
        elif self.pod:
            command = f"kubectl port-forward -n {self.namespace} pod/{self.pod} {self.port_to}:{self.port_from}"
        else:
            raise PofError("either service or pod must be specified")

        return command

    # TODO: make these static not to fully restore context
    @property
    def type_(self) -> str:
        return "kubernetes"

    @property
    def executable(self) -> str:
        return "kubectl"

    @property
    def signal(self) -> signal.Signals:
        return signal.SIGINT

    @property
    def metadata(self):
        data = {}

        def add_if_defined(label, value):
            data.update({label: value}) if value else ...

        add_if_defined("context", self.context)
        add_if_defined("namespace", self.namespace)
        add_if_defined("service", self.service)
        add_if_defined("pod", self.pod)
        return data
