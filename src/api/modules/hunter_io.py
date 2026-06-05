from api.modules.base import BaseModule, ModuleResult


class HunterIOModule(BaseModule):
    name = "hunter_io"
    accepted_target_types = ["domain"]
    requires_api_key = True

    def run(self, target_value: str, api_key: str | None = None) -> ModuleResult:
        raise NotImplementedError
