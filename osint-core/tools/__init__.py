from osint_core.tools.base import OSINTTool, OSINTResult, ToolStatus

TOOL_REGISTRY = {}


def register_tool(tool_class):
    instance = tool_class()
    TOOL_REGISTRY[instance.name()] = instance
    return tool_class


def get_tool(name: str) -> OSINTTool:
    return TOOL_REGISTRY.get(name)


def get_all_tools() -> dict:
    return dict(TOOL_REGISTRY)


def get_tools_by_category(category: str) -> dict:
    return {name: tool for name, tool in TOOL_REGISTRY.items() if tool.category() == category}


def get_tools_by_categories(categories: list) -> dict:
    result = {}
    for cat in categories:
        result.update(get_tools_by_category(cat))
    return result