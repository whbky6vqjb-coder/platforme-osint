import re
from typing import Any, Dict, List, Set
from dataclasses import dataclass, field


EMAIL_RE = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
IPV4_RE = re.compile(r'\b(?:(?:25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)\.){3}(?:25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)\b')
IPV6_RE = re.compile(r'\b(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}\b')
DOMAIN_RE = re.compile(r'\b(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}\b')
PHONE_RE = re.compile(r'\b(?:\+?\d{1,3}[-.\s]?)?(?:\(?\d{1,4}\)?[-.\s]?)?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{0,4}\b')
URL_RE = re.compile(r'https?://[^\s<>"\']+')
UUID_RE = re.compile(r'\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b')
BTC_ADDR_RE = re.compile(r'\b[13][a-km-zA-HJ-NP-Z1-9]{25,34}\b')
ETH_ADDR_RE = re.compile(r'\b0x[a-fA-F0-9]{40}\b')


@dataclass
class Entity:
    id: str
    type: str
    value: str
    source_tool: str
    source_query: str
    confidence: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class EntityExtractor:
    def __init__(self):
        self.extractors = {
            "email": self._extract_emails,
            "ip": self._extract_ips,
            "domain": self._extract_domains,
            "phone": self._extract_phones,
            "url": self._extract_urls,
            "uuid": self._extract_uuids,
            "btc_address": self._extract_btc,
            "eth_address": self._extract_eth,
            "company": self._extract_companies,
            "person": self._extract_persons,
        }

    def extract_all(self, text: str, source_tool: str = "", source_query: str = "") -> List[Entity]:
        entities = []
        seen = set()

        for entity_type, extractor in self.extractors.items():
            for match in extractor(text):
                key = f"{entity_type}:{match.lower()}"
                if key in seen:
                    continue
                seen.add(key)
                entities.append(Entity(
                    id=f"{entity_type}:{match.lower()}",
                    type=entity_type,
                    value=match,
                    source_tool=source_tool,
                    source_query=source_query,
                    confidence=0.5,
                ))

        return entities

    def extract_from_result(self, result: Any, source_tool: str = "", source_query: str = "") -> List[Entity]:
        entities = []
        if isinstance(result, dict):
            for key, value in result.items():
                if isinstance(value, str):
                    entities.extend(self.extract_all(value, source_tool, source_query))
                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, str):
                            entities.extend(self.extract_all(item, source_tool, source_query))
        elif isinstance(result, str):
            entities.extend(self.extract_all(result, source_tool, source_query))
        return entities

    def _extract_emails(self, text: str) -> List[str]:
        return [m.group(0) for m in EMAIL_RE.finditer(text)]

    def _extract_ips(self, text: str) -> List[str]:
        return [m.group(0) for m in IPV4_RE.finditer(text)]

    def _extract_domains(self, text: str) -> List[str]:
        return [m.group(0) for m in DOMAIN_RE.finditer(text)]

    def _extract_phones(self, text: str) -> List[str]:
        return [m.group(0) for m in PHONE_RE.finditer(text)]

    def _extract_urls(self, text: str) -> List[str]:
        return [m.group(0) for m in URL_RE.finditer(text)]

    def _extract_uuids(self, text: str) -> List[str]:
        return [m.group(0) for m in UUID_RE.finditer(text)]

    def _extract_btc(self, text: str) -> List[str]:
        return [m.group(0) for m in BTC_ADDR_RE.finditer(text)]

    def _extract_eth(self, text: str) -> List[str]:
        return [m.group(0) for m in ETH_ADDR_RE.finditer(text)]

    def _extract_companies(self, text: str) -> List[str]:
        patterns = [
            r'\b(?:SA|SARL|SAS|SA|SNC|SCI|SEL|SNC|SA|SRL|GmbH|AG|AG|PLC|Inc\.|LLC|Corp\.|Ltd\.|BV|NV|SE|AB|Pty|Ltd)\b[^\n,.]{0,100}',
        ]
        results = []
        for pattern in patterns:
            for m in re.finditer(pattern, text, re.IGNORECASE):
                results.append(m.group(0).strip())
        return results

    def _extract_persons(self, text: str) -> List[str]:
        return []