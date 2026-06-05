from api.modules.base import BaseModule, ModuleResult


class SherlockModule(BaseModule):
    name = "sherlock"
    accepted_target_types = ["username"]
    requires_api_key = False

    def run(self, target_value: str, api_key: str | None = None) -> ModuleResult:
        raise NotImplementedError
