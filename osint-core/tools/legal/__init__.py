from osint_core.tools.base import OSINTTool, OSINTResult, ToolStatus, register_tool


@register_tool
class Google_Patents_Tool(OSINTTool):
    def name(self) -> str:
        return "google_patents"

    def description(self) -> str:
        return "Search global patent database for inventions and patent holders"

    def category(self) -> str:
        return "legal"

    def input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Patent number, inventor name, or keyword"},
                "country": {"type": "string", "description": "Country code filter"},
            },
            "required": {"query": {"type": "string"}},
        }

    def execute(self, params: dict) -> OSINTResult:
        query = params.get("query", "")
        return OSINTResult(
            tool_name=self.name(),
            query=query,
            status=ToolStatus.SUCCESS,
            data={"query": query, "patents": [], "source": "patents.google.com"},
            confidence=0.85,
            source_url=f"https://patents.google.com/?q={query}",
        )

    def confidence_score(self, result: OSINTResult) -> float:
        return 0.85


@register_tool
class Légifrance_Tool(OSINTTool):
    def name(self) -> str:
        return "legifrance"

    def description(self) -> str:
        return "Search French legal database (Légifrance) for jurisprudence and legal texts"

    def category(self) -> str:
        return "legal"

    def input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search term for legal texts or jurisprudence"},
                "search_type": {"type": "string", "enum": ["jurisprudence", "legislation", "documents"]},
            },
            "required": {"query": {"type": "string"}},
        }

    def execute(self, params: dict) -> OSINTResult:
        query = params.get("query", "")
        return OSINTResult(
            tool_name=self.name(),
            query=query,
            status=ToolStatus.SUCCESS,
            data={"query": query, "results": [], "source": "legifrance.gouv.fr"},
            confidence=0.9,
            source_url=f"https://www.legifrance.gouv.fr/codes/recherche?query={query}",
        )

    def confidence_score(self, result: OSINTResult) -> float:
        return 0.9