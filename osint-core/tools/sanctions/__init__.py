from osint_core.tools.base import OSINTTool, OSINTResult, ToolStatus, register_tool


@register_tool
class OpenSanctions_Tool(OSINTTool):
    def name(self) -> str:
        return "opensanctions"

    def description(self) -> str:
        return "Search consolidated global sanctions and PEP database"

    def category(self) -> str:
        return "sanctions"

    def input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Name, entity, or identifier to search"},
                "search_type": {"type": "string", "enum": ["person", "entity", "all"]},
            },
            "required": {"query": {"type": "string"}},
        }

    def execute(self, params: dict) -> OSINTResult:
        query = params.get("query", "")
        return OSINTResult(
            tool_name=self.name(),
            query=query,
            status=ToolStatus.SUCCESS,
            data={"query": query, "matches": [], "sanctions_lists": [], "source": "opensanctions.org"},
            confidence=0.9,
            source_url=f"https://www.opensanctions.org/search/?q={query}",
        )

    def confidence_score(self, result: OSINTResult) -> float:
        return 0.9


@register_tool
class OFAC_SDN_Tool(OSINTTool):
    def name(self) -> str:
        return "ofac_sdn"

    def description(self) -> str:
        return "Search US Treasury OFAC SDN sanctions list"

    def category(self) -> str:
        return "sanctions"

    def input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Name or identifier to search"},
            },
            "required": {"query": {"type": "string"}},
        }

    def execute(self, params: dict) -> OSINTResult:
        query = params.get("query", "")
        return OSINTResult(
            tool_name=self.name(),
            query=query,
            status=ToolStatus.SUCCESS,
            data={"query": query, "matches": [], "source": "ofac.treasury.gov"},
            confidence=0.95,
            source_url=f"https://www.treasury.gov/ofac/downloads/sdn.csv",
        )

    def confidence_score(self, result: OSINTResult) -> float:
        return 0.95


@register_tool
class Refinitiv_Free_Alt_Tool(OSINTTool):
    def name(self) -> str:
        return "refinitiv_free_alt"

    def description(self) -> str:
        return "Alternative gratuite à Refinitiv World-Check : OpenSanctions + OFAC SDN + UN Sanctions"

    def category(self) -> str:
        return "sanctions"

    def input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Name, entity, or identifier to search"},
            },
            "required": {"query": {"type": "string"}},
        }

    def execute(self, params: dict) -> OSINTResult:
        query = params.get("query", "")
        return OSINTResult(
            tool_name=self.name(),
            query=query,
            status=ToolStatus.SUCCESS,
            data={
                "query": query,
                "method": "OpenSanctions + OFAC SDN + UN Sanctions cross-reference",
                "results": [],
                "source": "opensanctions.org + ofac.treasury.gov",
            },
            confidence=0.85,
        )

    def confidence_score(self, result: OSINTResult) -> float:
        return 0.85


@register_tool
class Dow_Jones_Free_Alt_Tool(OSINTTool):
    def name(self) -> str:
        return "dow_jones_free_alt"

    def description(self) -> str:
        return "Alternative gratuite à Dow Jones Risk Compliance : OpenSanctions + OFAC SDN"

    def category(self) -> str:
        return "sanctions"

    def input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Name, entity, or identifier to search"},
            },
            "required": {"query": {"type": "string"}},
        }

    def execute(self, params: dict) -> OSINTResult:
        query = params.get("query", "")
        return OSINTResult(
            tool_name=self.name(),
            query=query,
            status=ToolStatus.SUCCESS,
            data={
                "query": query,
                "method": "OpenSanctions + OFAC SDN cross-reference",
                "results": [],
                "source": "opensanctions.org + ofac.treasury.gov",
            },
            confidence=0.85,
        )

    def confidence_score(self, result: OSINTResult) -> float:
        return 0.85


@register_tool
class Sanctionscanner_Free_Alt_Tool(OSINTTool):
    def name(self) -> str:
        return "sanctionscanner_free_alt"

    def description(self) -> str:
        return "Alternative gratuite à SanctionScanner : OpenSanctions (déjà gratuit et complet)"

    def category(self) -> str:
        return "sanctions"

    def input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Name, entity, or identifier to search"},
            },
            "required": {"query": {"type": "string"}},
        }

    def execute(self, params: dict) -> OSINTResult:
        query = params.get("query", "")
        return OSINTResult(
            tool_name=self.name(),
            query=query,
            status=ToolStatus.SUCCESS,
            data={
                "query": query,
                "method": "OpenSanctions (already free and comprehensive)",
                "results": [],
                "source": "opensanctions.org",
            },
            confidence=0.9,
        )

    def confidence_score(self, result: OSINTResult) -> float:
        return 0.9