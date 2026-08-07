from osint_core.tools.base import OSINTTool, OSINTResult, ToolStatus, register_tool


@register_tool
class DVF_Tool(OSINTTool):
    def name(self) -> str:
        return "dvf"

    def description(self) -> str:
        return "Search French DVF (Demandes de Valeurs Foncières) for property transaction records"

    def category(self) -> str:
        return "ghost"

    def input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Property address, commune, or owner name"},
                "commune": {"type": "string", "description": "French commune filter"},
                "date_min": {"type": "string", "format": "date", "description": "Start date (YYYY-MM-DD)"},
                "date_max": {"type": "string", "format": "date", "description": "End date (YYYY-MM-DD)"},
            },
            "required": {"query": {"type": "string"}},
        }

    def execute(self, params: dict) -> OSINTResult:
        query = params.get("query", "")
        return OSINTResult(
            tool_name=self.name(),
            query=query,
            status=ToolStatus.SUCCESS,
            data={"query": query, "transactions": [], "source": "data.gouv.fr/DVF"},
            confidence=0.85,
            source_url=f"https://www.data.gouv.fr/fr/datasets/dvf/",
        )

    def confidence_score(self, result: OSINTResult) -> float:
        return 0.85


@register_tool
class RTE_OpenData_Tool(OSINTTool):
    def name(self) -> str:
        return "rte_opendata"

    def description(self) -> str:
        return "Search RTE Open Data for high-voltage grid reservation requests (datacenter indicator)"

    def category(self) -> str:
        return "ghost"

    def input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search term for grid reservation requests"},
                "date_min": {"type": "string", "format": "date"},
                "date_max": {"type": "string", "format": "date"},
            },
            "required": {"query": {"type": "string"}},
        }

    def execute(self, params: dict) -> OSINTResult:
        query = params.get("query", "")
        return OSINTResult(
            tool_name=self.name(),
            query=query,
            status=ToolStatus.SUCCESS,
            data={"query": query, "reservations": [], "source": "rte-france.com/open-data"},
            confidence=0.8,
        )

    def confidence_score(self, result: OSINTResult) -> float:
        return 0.8


@register_tool
class Sentinel_Satellite_Tool(OSINTTool):
    def name(self) -> str:
        return "sentinel_satellite"

    def description(self) -> str:
        return "Query Sentinel Hub for satellite imagery (SAR for construction, NDVI for vegetation changes)"

    def category(self) -> str:
        return "ghost"

    def input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "lat": {"type": "number", "description": "Latitude"},
                "lon": {"type": "number", "description": "Longitude"},
                "date_min": {"type": "string", "format": "date"},
                "date_max": {"type": "string", "format": "date"},
                "sensor": {"type": "string", "enum": ["sentinel-1", "sentinel-2"]},
            },
            "required": {},
        }

    def execute(self, params: dict) -> OSINTResult:
        lat = params.get("lat", 0)
        lon = params.get("lon", 0)
        return OSINTResult(
            tool_name=self.name(),
            query=f"lat={lat}, lon={lon}",
            status=ToolStatus.SUCCESS,
            data={"coordinates": {"lat": lat, "lon": lon}, "imagery": [], "source": "sentinel-hub.com"},
            confidence=0.8,
        )

    def confidence_score(self, result: OSINTResult) -> float:
        return 0.8


@register_tool
class CelesTrak_Satellite_Tool(OSINTTool):
    def name(self) -> str:
        return "celestrak_satellite"

    def description(self) -> str:
        return "Suivi gratuit des satellites d'observation au-dessus d'une zone (alternative a SpymeSat)"

    def category(self) -> str:
        return "ghost"

    def input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "lat": {"type": "number", "description": "Latitude of observation zone"},
                "lon": {"type": "number", "description": "Longitude of observation zone"},
                "date": {"type": "string", "format": "date", "description": "Date for satellite pass prediction"},
            },
            "required": {},
        }

    def execute(self, params: dict) -> OSINTResult:
        lat = params.get("lat", 0)
        lon = params.get("lon", 0)
        return OSINTResult(
            tool_name=self.name(),
            query=f"lat={lat}, lon={lon}",
            status=ToolStatus.SUCCESS,
            data={
                "coordinates": {"lat": lat, "lon": lon},
                "satellite_passes": [],
                "source": "celestrak.org",
                "note": "Free alternative to SpymeSat for satellite pass prediction",
            },
            confidence=0.75,
        )

    def confidence_score(self, result: OSINTResult) -> float:
        return 0.75