from api.modules.base import BaseModule, ModuleResult


class HudsonRockModule(BaseModule):
    name = "hudsonrock"
    accepted_target_types = ["username", "email"]
    requires_api_key = False

    def run(self, target_value: str, api_key: str | None = None) -> ModuleResult:
        raise NotImplementedError
