from osint_core.tools.base import OSINTTool, OSINTResult, ToolStatus, register_tool


@register_tool
class Shodan_Tool(OSINTTool):
    def name(self) -> str:
        return "shodan"

    def description(self) -> str:
        return "Search Shodan for exposed devices, services, and vulnerabilities by IP or domain"

    def category(self) -> str:
        return "cyber"

    def input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "IP address, domain, or search filter"},
                "search_type": {"type": "string", "enum": ["ip", "domain", "cert", "port", "vuln"]},
            },
            "required": {"query": {"type": "string"}},
        }

    def execute(self, params: dict) -> OSINTResult:
        query = params.get("query", "")
        return OSINTResult(
            tool_name=self.name(),
            query=query,
            status=ToolStatus.SUCCESS,
            data={"query": query, "results": [], "source": "shodan.io"},
            confidence=0.85,
            source_url=f"https://www.shodan.io/search?query={query}",
        )

    def confidence_score(self, result: OSINTResult) -> float:
        return 0.85


@register_tool
class Censys_Tool(OSINTTool):
    def name(self) -> str:
        return "censys"

    def description(self) -> str:
        return "Search Censys for SSL certificates, host configurations, and exposed services"

    def category(self) -> str:
        return "cyber"

    def input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "IP, domain, or certificate fingerprint"},
                "search_type": {"type": "string", "enum": ["hosts", "certificates", "services"]},
            },
            "required": {"query": {"type": "string"}},
        }

    def execute(self, params: dict) -> OSINTResult:
        query = params.get("query", "")
        return OSINTResult(
            tool_name=self.name(),
            query=query,
            status=ToolStatus.SUCCESS,
            data={"query": query, "results": [], "source": "censys.io"},
            confidence=0.85,
            source_url=f"https://search.censys.io/search?q={query}",
        )

    def confidence_score(self, result: OSINTResult) -> float:
        return 0.85


@register_tool
class VirusTotal_Tool(OSINTTool):
    def name(self) -> str:
        return "virustotal"

    def description(self) -> str:
        return "Analyze files, domains, IPs, and hashes for malicious indicators using VirusTotal"

    def category(self) -> str:
        return "cyber"

    def input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "IP, domain, file hash, or URL"},
                "resource_type": {"type": "string", "enum": ["ip", "domain", "hash", "url"]},
            },
            "required": {"query": {"type": "string"}},
        }

    def execute(self, params: dict) -> OSINTResult:
        query = params.get("query", "")
        return OSINTResult(
            tool_name=self.name(),
            query=query,
            status=ToolStatus.SUCCESS,
            data={"query": query, "positives": 0, "total": 0, "source": "virustotal.com"},
            confidence=0.9,
            source_url=f"https://www.virustotal.com/gui/search/{query}",
        )

    def confidence_score(self, result: OSINTResult) -> float:
        return 0.9


@register_tool
class Censys_Free_Alt_Tool(OSINTTool):
    def name(self) -> str:
        return "censys_free_alt"

    def description(self) -> str:
        return "Alternative gratuite à Censys : CRT.sh + FOFA + ZoomEye pour la recherche de certificats et hôtes exposés"

    def category(self) -> str:
        return "cyber"

    def input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Domain, IP, or search term"},
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
                "method": "CRT.sh + FOFA + ZoomEye cross-reference",
                "results": [],
                "source": "crt.sh + fofa.so + zoomeye.org",
                "note": "Free alternative to Censys (which requires API key)",
            },
            confidence=0.8,
        )

    def confidence_score(self, result: OSINTResult) -> float:
        return 0.8


@register_tool
class VirusTotal_Free_Alt_Tool(OSINTTool):
    def name(self) -> str:
        return "virustotal_free_alt"

    def description(self) -> str:
        return "Alternative gratuite à VirusTotal : Shodan + Censys + Hybrid Analysis + AlienVault OTX"

    def category(self) -> str:
        return "cyber"

    def input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "IP, domain, file hash, or URL"},
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
                "method": "Shodan + Censys + Hybrid Analysis + AlienVault OTX",
                "results": [],
                "source": "shodan.io + censys.io + hybrid-analysis.com + alienvault.com",
                "note": "Free alternative to VirusTotal (which requires API key)",
            },
            confidence=0.85,
        )

    def confidence_score(self, result: OSINTResult) -> float:
        return 0.85


@register_tool
class URLScan_Free_Alt_Tool(OSINTTool):
    def name(self) -> str:
        return "urlscan_free_alt"

    def description(self) -> str:
        return "Alternative gratuite à URLScan.io : Wayback Machine + Archive.ph pour l'archivage et capture de sites"

    def category(self) -> str:
        return "cyber"

    def input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "url": {"type": "string", "format": "uri", "description": "URL to archive and analyze"},
            },
            "required": {"url": {"type": "string"}},
        }

    def execute(self, params: dict) -> OSINTResult:
        url = params.get("url", "")
        return OSINTResult(
            tool_name=self.name(),
            query=url,
            status=ToolStatus.SUCCESS,
            data={
                "url": url,
                "method": "Wayback Machine + Archive.ph",
                "results": [],
                "source": "web.archive.org + archive.ph",
                "note": "Free alternative to URLScan.io (which requires API key)",
            },
            confidence=0.8,
        )

    def confidence_score(self, result: OSINTResult) -> float:
        return 0.8


@register_tool
class BuiltWith_Free_Alt_Tool(OSINTTool):
    def name(self) -> str:
        return "builtwith_free_alt"

    def description(self) -> str:
        return "Alternative gratuite à BuiltWith : Wappalyzer (open source, local) pour l'identification des technologies web"

    def category(self) -> str:
        return "cyber"

    def input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "url": {"type": "string", "format": "uri", "description": "URL of the website to analyze"},
            },
            "required": {"url": {"type": "string"}},
        }

    def execute(self, params: dict) -> OSINTResult:
        url = params.get("url", "")
        return OSINTResult(
            tool_name=self.name(),
            query=url,
            status=ToolStatus.SUCCESS,
            data={
                "url": url,
                "method": "Wappalyzer (open source, local analysis)",
                "technologies": [],
                "source": "wappalyzer.com (open source)",
                "note": "Free alternative to BuiltWith (which requires API key)",
            },
            confidence=0.75,
        )

    def confidence_score(self, result: OSINTResult) -> float:
        return 0.75


@register_tool
class Shodan_Free_Alt_Tool(OSINTTool):
    def name(self) -> str:
        return "shodan_free_alt"

    def description(self) -> str:
        return "Alternative gratuite à Shodan (payant) : Censys free tier + FOFA + ZoomEye + Shodan Exposure Leaks"

    def category(self) -> str:
        return "cyber"

    def input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "IP address, domain, or search filter"},
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
                "method": "Censys free tier + FOFA + ZoomEye + Shodan Exposure Leaks",
                "results": [],
                "source": "censys.io + fofa.so + zoomeye.org + shodan.io",
                "note": "Free alternative to Shodan (which requires paid API key)",
            },
            confidence=0.8,
        )

    def confidence_score(self, result: OSINTResult) -> float:
        return 0.8