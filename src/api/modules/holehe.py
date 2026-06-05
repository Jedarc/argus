from api.modules.base import BaseModule, ModuleResult


class HoleheModule(BaseModule):
    name = "holehe"
    accepted_target_types = ["email"]
    requires_api_key = False

    def run(self, target_value: str, api_key: str | None = None) -> ModuleResult:
        raise NotImplementedError
