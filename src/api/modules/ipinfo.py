from api.modules.base import BaseModule, ModuleResult


class IPInfoModule(BaseModule):
    name = "ipinfo"
    accepted_target_types = ["ip"]
    requires_api_key = False

    def run(self, target_value: str, api_key: str | None = None) -> ModuleResult:
        raise NotImplementedError
