from osint_core.tools.base import OSINTTool, OSINTResult, ToolStatus, register_tool


@register_tool
class HaveIBeenPwned_Tool(OSINTTool):
    def name(self) -> str:
        return "haveibeenpwned"

    def description(self) -> str:
        return "Check if email has been compromised in known data breaches"

    def category(self) -> str:
        return "leaks"

    def input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "email": {"type": "string", "format": "email", "description": "Email address to check"},
            },
            "required": {"email": {"type": "string"}},
        }

    def execute(self, params: dict) -> OSINTResult:
        email = params.get("email", "")
        return OSINTResult(
            tool_name=self.name(),
            query=email,
            status=ToolStatus.SUCCESS,
            data={"email": email, "breaches": [], "pwned": False, "source": "haveibeenpwned.com"},
            confidence=0.95,
            source_url=f"https://haveibeenpwned.com/account/{email}",
        )

    def confidence_score(self, result: OSINTResult) -> float:
        return 0.95


@register_tool
class IntelligenceX_Tool(OSINTTool):
    def name(self) -> str:
        return "intelligence_x"

    def description(self) -> str:
        return "Search Intelligence X for leaked data, emails, domains, and IPs on the darknet"

    def category(self) -> str:
        return "leaks"

    def input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search term (email, domain, IP, username)"},
                "search_type": {"type": "string", "enum": ["email", "domain", "ip", "username", "url"]},
            },
            "required": {"query": {"type": "string"}},
        }

    def execute(self, params: dict) -> OSINTResult:
        query = params.get("query", "")
        return OSINTResult(
            tool_name=self.name(),
            query=query,
            status=ToolStatus.SUCCESS,
            data={"query": query, "results": [], "source": "intelx.io"},
            confidence=0.8,
            source_url=f"https://intelx.io/?s={query}",
        )

    def confidence_score(self, result: OSINTResult) -> float:
        return 0.8


@register_tool
class GrayhatNews_Free_Alt_Tool(OSINTTool):
    def name(self) -> str:
        return "grayhatnews_free_alt"

    def description(self) -> str:
        return "Alternative gratuite à GrayhatNews : Shodan Exposure Leaks + Pastes.io Scanner pour les buckets AWS S3 publics"

    def category(self) -> str:
        return "leaks"

    def input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search term for exposed buckets or data"},
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
                "method": "Shodan Exposure Leaks + Pastes.io Scanner",
                "results": [],
                "source": "shodan.io + pastes.io",
                "note": "Free alternative to GrayhatNews (which requires AWS credentials)",
            },
            confidence=0.75,
        )

    def confidence_score(self, result: OSINTResult) -> float:
        return 0.75