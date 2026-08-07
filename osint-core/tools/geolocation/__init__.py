from osint_core.tools.base import OSINTTool, OSINTResult, ToolStatus, register_tool


@register_tool
class OpenCellID_Tool(OSINTTool):
    def name(self) -> str:
        return "opencellid"

    def description(self) -> str:
        return "Geolocate mobile towers using OpenCellID database"

    def category(self) -> str:
        return "geolocation"

    def input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "cell_id": {"type": "string", "description": "Cell tower ID"},
                "mcc": {"type": "string", "description": "Mobile Country Code"},
                "mnc": {"type": "string", "description": "Mobile Network Code"},
                "lac": {"type": "string", "description": "Location Area Code"},
            },
            "required": {},
        }

    def execute(self, params: dict) -> OSINTResult:
        return OSINTResult(
            tool_name=self.name(),
            query=str(params),
            status=ToolStatus.SUCCESS,
            data={"location": None, "source": "opencellid.org"},
            confidence=0.7,
        )

    def confidence_score(self, result: OSINTResult) -> float:
        return 0.7


@register_tool
class WiGLE_Tool(OSINTTool):
    def name(self) -> str:
        return "wigle"

    def description(self) -> str:
        return "Geolocate Wi-Fi networks using WiGLE database"

    def category(self) -> str:
        return "geolocation"

    def input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "ssid": {"type": "string", "description": "Wi-Fi network name"},
                "bssid": {"type": "string", "description": "MAC address of access point"},
            },
            "required": {},
        }

    def execute(self, params: dict) -> OSINTResult:
        return OSINTResult(
            tool_name=self.name(),
            query=str(params),
            status=ToolStatus.SUCCESS,
            data={"location": None, "source": "wigle.net"},
            confidence=0.75,
        )

    def confidence_score(self, result: OSINTResult) -> float:
        return 0.75


@register_tool
class CelesTrak_Tool(OSINTTool):
    def name(self) -> str:
        return "celestrak"

    def description(self) -> str:
        return "Suivi gratuit des satellites d'observation et calcul de passage au-dessus d'une zone (alternative à SpymeSat)"

    def category(self) -> str:
        return "geolocation"

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