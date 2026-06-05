from api.modules.base import BaseModule, ModuleResult


class HibpModule(BaseModule):
    name = "hibp"
    accepted_target_types = ["email"]
    requires_api_key = True

    def run(self, target_value: str, api_key: str | None = None) -> ModuleResult:
        raise NotImplementedError
