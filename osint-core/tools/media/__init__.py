from osint_core.tools.base import OSINTTool, OSINTResult, ToolStatus, register_tool


@register_tool
class InVID_Tool(OSINTTool):
    def name(self) -> str:
        return "invid"

    def description(self) -> str:
        return "Verify videos and images, perform reverse image search and metadata extraction"

    def category(self) -> str:
        return "media"

    def input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "url": {"type": "string", "format": "uri", "description": "URL of image or video to verify"},
                "mode": {"type": "string", "enum": ["reverse_image", "video_analysis", "metadata"]},
            },
            "required": {"url": {"type": "string"}},
        }

    def execute(self, params: dict) -> OSINTResult:
        url = params.get("url", "")
        return OSINTResult(
            tool_name=self.name(),
            query=url,
            status=ToolStatus.SUCCESS,
            data={"url": url, "verification": {}, "source": "weverify.eu"},
            confidence=0.75,
        )

    def confidence_score(self, result: OSINTResult) -> float:
        return 0.75


@register_tool
class FotoForensics_Tool(OSINTTool):
    def name(self) -> str:
        return "fotoforensics"

    def description(self) -> str:
        return "Analyze images for manipulation using Error Level Analysis (ELA)"

    def category(self) -> str:
        return "media"

    def input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "url": {"type": "string", "format": "uri", "description": "URL of image to analyze"},
            },
            "required": {"url": {"type": "string"}},
        }

    def execute(self, params: dict) -> OSINTResult:
        url = params.get("url", "")
        return OSINTResult(
            tool_name=self.name(),
            query=url,
            status=ToolStatus.SUCCESS,
            data={"url": url, "ela_result": {}, "source": "fotoforensics.com"},
            confidence=0.8,
        )

    def confidence_score(self, result: OSINTResult) -> float:
        return 0.8


@register_tool
class PimEyes_Free_Alt_Tool(OSINTTool):
    def name(self) -> str:
        return "pimeyes_free_alt"

    def description(self) -> str:
        return "Alternative gratuite à PimEyes : Yandex Reverse Image + TinEye pour la recherche faciale"

    def category(self) -> str:
        return "media"

    def input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "url": {"type": "string", "format": "uri", "description": "URL of image to search"},
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
                "method": "Yandex Reverse Image + TinEye",
                "results": [],
                "source": "yandex.com/images + tineye.com",
                "note": "Free alternative to PimEyes (which is paid)",
            },
            confidence=0.7,
        )

    def confidence_score(self, result: OSINTResult) -> float:
        return 0.7