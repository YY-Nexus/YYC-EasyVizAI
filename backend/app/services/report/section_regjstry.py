from typing import Dict, Type

class BaseSectionBuilder:
    section_type = "abstract"
    def validate(self, payload): ...
    def build(self, context): ...
    def metrics_tag(self):
        return self.section_type

_REGISTRY: Dict[str, Type[BaseSectionBuilder]] = {}

def register(section_type: str):
    def wrapper(cls: Type[BaseSectionBuilder]):
        if section_type in _REGISTRY:
            raise ValueError(f"Section type {section_type} already registered")
        cls.section_type = section_type
        _REGISTRY[section_type] = cls
        return cls
    return wrapper

def get_builder(section_type: str) -> Type[BaseSectionBuilder]:
    return _REGISTRY[section_type]

def list_section_types():
    return list(_REGISTRY.keys())

# 示例扩展
@register("summary")
class SummarySection(BaseSectionBuilder):
    def validate(self, payload):
        pass
    def build(self, context):
        return {"text": "本周进展摘要...", "tokens": 120}