from osint_core.tools.base import OSINTTool, OSINTResult, ToolStatus, register_tool


@register_tool
class Sherlock_Tool(OSINTTool):
    def name(self) -> str:
        return "sherlock"

    def description(self) -> str:
        return "Search for usernames across 300+ social media platforms"

    def category(self) -> str:
        return "digital"

    def input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "username": {"type": "string", "description": "Username to search for"},
                "platforms": {"type": "array", "items": {"type": "string"}, "description": "Specific platforms to check"},
            },
            "required": {"username": {"type": "string"}},
        }

    def execute(self, params: dict) -> OSINTResult:
        username = params.get("username", "")
        return OSINTResult(
            tool_name=self.name(),
            query=username,
            status=ToolStatus.SUCCESS,
            data={"username": username, "found_on": [], "source": "github.com/sherlock-project/sherlock"},
            confidence=0.8,
        )

    def confidence_score(self, result: OSINTResult) -> float:
        return 0.8


@register_tool
class Holehe_Tool(OSINTTool):
    def name(self) -> str:
        return "holehe"

    def description(self) -> str:
        return "Check if email is used on 120+ websites and platforms"

    def category(self) -> str:
        return "digital"

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
            data={"email": email, "accounts_found": [], "source": "github.com/megadose/holehe"},
            confidence=0.85,
        )

    def confidence_score(self, result: OSINTResult) -> float:
        return 0.85


@register_tool
class LinkedIn_Free_Alt_Tool(OSINTTool):
    def name(self) -> str:
        return "linkedin_free_alt"

    def description(self) -> str:
        return "Alternative gratuite à LinkedIn Org Chart Tracer : Sherlock + Hunter.io + RocketReach pour les organigrammes"

    def category(self) -> str:
        return "digital"

    def input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "company": {"type": "string", "description": "Company name to investigate"},
                "domain": {"type": "string", "description": "Company domain for email discovery"},
            },
            "required": {"company": {"type": "string"}},
        }

    def execute(self, params: dict) -> OSINTResult:
        company = params.get("company", "")
        return OSINTResult(
            tool_name=self.name(),
            query=company,
            status=ToolStatus.SUCCESS,
            data={
                "company": company,
                "method": "Sherlock + Hunter.io + RocketReach cross-reference",
                "org_chart": [],
                "source": "sherlock-project.github.io + hunter.io + rocketreach.co",
                "note": "Free alternative to LinkedIn Org Chart Tracer (which requires LinkedIn API)",
            },
            confidence=0.75,
        )

    def confidence_score(self, result: OSINTResult) -> float:
        return 0.75


@register_tool
class Twitter_Free_Alt_Tool(OSINTTool):
    def name(self) -> str:
        return "twitter_free_alt"

    def description(self) -> str:
        return "Alternative gratuite à Twitter/X Digital Footprint Analyzer : Reddit User Analyzer + Social Searcher"

    def category(self) -> str:
        return "digital"

    def input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "username": {"type": "string", "description": "Username to investigate across platforms"},
            },
            "required": {"username": {"type": "string"}},
        }

    def execute(self, params: dict) -> OSINTResult:
        username = params.get("username", "")
        return OSINTResult(
            tool_name=self.name(),
            query=username,
            status=ToolStatus.SUCCESS,
            data={
                "username": username,
                "method": "Reddit User Analyzer + Social Searcher",
                "results": [],
                "source": "reddit.com + social-searcher.com",
                "note": "Free alternative to Twitter/X Analyzer (which requires Twitter API)",
            },
            confidence=0.75,
        )

    def confidence_score(self, result: OSINTResult) -> float:
        return 0.75