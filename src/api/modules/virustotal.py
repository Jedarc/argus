from api.modules.base import BaseModule, ModuleResult


class VirusTotalModule(BaseModule):
    name = "virustotal"
    accepted_target_types = ["ip", "domain"]
    requires_api_key = True

    def run(self, target_value: str, api_key: str | None = None) -> ModuleResult:
        raise NotImplementedError
