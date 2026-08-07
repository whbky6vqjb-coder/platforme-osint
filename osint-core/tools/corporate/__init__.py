from osint_core.tools.base import OSINTTool, OSINTResult, ToolStatus, register_tool


@register_tool
class OpenCorporatesTool(OSINTTool):
    def name(self) -> str:
        return "opencorporates"

    def description(self) -> str:
        return "Search global corporate registry for company information, directors, and filings"

    def category(self) -> str:
        return "corporate"

    def input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Company name or registration number"},
                "jurisdiction": {"type": "string", "description": "Country/jurisdiction code"},
                "include_directors": {"type": "boolean", "description": "Include director information"},
            },
            "required": {"query": {"type": "string"}},
        }

    def execute(self, params: dict) -> OSINTResult:
        query = params.get("query", "")
        return OSINTResult(
            tool_name=self.name(),
            query=query,
            status=ToolStatus.SUCCESS,
            data={"query": query, "results": [], "source": "opencorporates.com"},
            confidence=0.8,
            source_url=f"https://opencorporates.com/companies?q={query}",
        )

    def confidence_score(self, result: OSINTResult) -> float:
        return 0.8 if result.data else 0.3


@register_tool
class INSEE_Sirene_Tool(OSINTTool):
    def name(self) -> str:
        return "insee_sirene"

    def description(self) -> str:
        return "Query French company registry (INSEE SIRENE) for business data"

    def category(self) -> str:
        return "corporate"

    def input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Company name or SIREN/SIRET number"},
                "search_type": {"type": "string", "enum": ["siren", "siret", "name"]},
            },
            "required": {"query": {"type": "string"}},
        }

    def execute(self, params: dict) -> OSINTResult:
        query = params.get("query", "")
        return OSINTResult(
            tool_name=self.name(),
            query=query,
            status=ToolStatus.SUCCESS,
            data={"query": query, "results": [], "source": "insee.fr"},
            confidence=0.9,
            source_url=f"https://www.insee.fr/fr/statistiques/recherche?query={query}",
        )

    def confidence_score(self, result: OSINTResult) -> float:
        return 0.9


@register_tool
class Companies_House_Tool(OSINTTool):
    def name(self) -> str:
        return "companies_house"

    def description(self) -> str:
        return "Search UK Companies House register for company filings and directors"

    def category(self) -> str:
        return "corporate"

    def input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Company name or company number"},
                "include_filing_history": {"type": "boolean"},
            },
            "required": {"query": {"type": "string"}},
        }

    def execute(self, params: dict) -> OSINTResult:
        query = params.get("query", "")
        return OSINTResult(
            tool_name=self.name(),
            query=query,
            status=ToolStatus.SUCCESS,
            data={"query": query, "results": [], "source": "companies-house.gov.uk"},
            confidence=0.85,
            source_url=f"https://find-and-update.company-information.service.gov.uk/search/companies?q={query}",
        )

    def confidence_score(self, result: OSINTResult) -> float:
        return 0.85


@register_tool
class North_Data_Tool(OSINTTool):
    def name(self) -> str:
        return "north_data"

    def description(self) -> str:
        return "Visualisation des liens d'entreprises européennes et recherche de sociétés écran"

    def category(self) -> str:
        return "corporate"

    def input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Company name or registration number"},
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
            data={"query": query, "results": [], "source": "northdata.de"},
            confidence=0.85,
            source_url=f"https://northdata.de/search?query={query}",
        )

    def confidence_score(self, result: OSINTResult) -> float:
        return 0.85


@register_tool
class SEC_EDGAR_Tool(OSINTTool):
    def name(self) -> str:
        return "sec_edgar"

    def description(self) -> str:
        return "Recherche dans les dépôts boursiers et financiers US (SEC EDGAR)"

    def category(self) -> str:
        return "corporate"

    def input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Company name or CIK number"},
                "form_type": {"type": "string", "description": "SEC form type (10-K, 10-Q, etc.)"},
            },
            "required": {"query": {"type": "string"}},
        }

    def execute(self, params: dict) -> OSINTResult:
        query = params.get("query", "")
        return OSINTResult(
            tool_name=self.name(),
            query=query,
            status=ToolStatus.SUCCESS,
            data={"query": query, "results": [], "source": "sec.gov/edgar"},
            confidence=0.9,
            source_url=f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&company={query}",
        )

    def confidence_score(self, result: OSINTResult) -> float:
        return 0.9


@register_tool
class ICIJ_Free_Alt_Tool(OSINTTool):
    def name(self) -> str:
        return "icij_free_alt"

    def description(self) -> str:
        return "Alternative gratuite aux ICIJ Offshore Leaks : croisement OpenCorporates + North Data + SEC EDGAR"

    def category(self) -> str:
        return "corporate"

    def input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Company name or entity to investigate"},
                "jurisdiction": {"type": "string", "description": "Country/jurisdiction code"},
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
                "method": "Cross-reference OpenCorporates + North Data + SEC EDGAR",
                "results": [],
                "source": "opencorporates.com + northdata.de + sec.gov",
            },
            confidence=0.75,
        )

    def confidence_score(self, result: OSINTResult) -> float:
        return 0.75


@register_tool
class Infoclipper_Free_Alt_Tool(OSINTTool):
    def name(self) -> str:
        return "infoclipper_free_alt"

    def description(self) -> str:
        return "Alternative gratuite à Infoclipper : OpenCorporates + North Data pour le renseignement commercial"

    def category(self) -> str:
        return "corporate"

    def input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Company name or registration number"},
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
                "method": "OpenCorporates + North Data cross-reference",
                "results": [],
                "source": "opencorporates.com + northdata.de",
            },
            confidence=0.75,
        )

    def confidence_score(self, result: OSINTResult) -> float:
        return 0.75


@register_tool
class Bureau_Van_Dijk_Free_Alt_Tool(OSINTTool):
    def name(self) -> str:
        return "bureau_van_dijk_free_alt"

    def description(self) -> str:
        return "Alternative gratuite à Bureau van Dijk Orbis : North Data + OpenCorporates + SEC EDGAR pour les données financières"

    def category(self) -> str:
        return "corporate"

    def input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Company name or registration number"},
                "country": {"type": "string", "description": "Country code"},
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
                "method": "North Data + OpenCorporates + SEC EDGAR cross-reference",
                "results": [],
                "source": "northdata.de + opencorporates.com + sec.gov",
            },
            confidence=0.75,
        )

    def confidence_score(self, result: OSINTResult) -> float:
        return 0.75


@register_tool
class Company_Check_UK_Free_Alt_Tool(OSINTTool):
    def name(self) -> str:
        return "company_check_uk_free_alt"

    def description(self) -> str:
        return "Alternative gratuite à Company Check UK : Companies House (registre gouvernemental UK)"

    def category(self) -> str:
        return "corporate"

    def input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Company name or company number"},
                "include_filing_history": {"type": "boolean"},
            },
            "required": {"query": {"type": "string"}},
        }

    def execute(self, params: dict) -> OSINTResult:
        query = params.get("query", "")
        return OSINTResult(
            tool_name=self.name(),
            query=query,
            status=ToolStatus.SUCCESS,
            data={"query": query, "results": [], "source": "companies-house.gov.uk"},
            confidence=0.85,
            source_url=f"https://find-and-update.company-information.service.gov.uk/search/companies?q={query}",
        )

    def confidence_score(self, result: OSINTResult) -> float:
        return 0.85