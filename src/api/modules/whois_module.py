from api.modules.base import BaseModule, ModuleResult


class WhoisModule(BaseModule):
    name = "whois"
    accepted_target_types = ["domain"]
    requires_api_key = False

    def run(self, target_value: str, api_key: str | None = None) -> ModuleResult:
        raise NotImplementedError
