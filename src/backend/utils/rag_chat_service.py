"""
Local RAG service for network operations Q&A.
Builds retrieval context from incidents, devices, and metrics, then answers
questions with grounded evidence snippets.
"""

import re
from datetime import datetime
from typing import Any, Dict, List


class NetworkRAGAssistant:
    """RAG-style assistant with lightweight lexical retrieval."""

    STOP_WORDS = {
        "the", "a", "an", "and", "or", "to", "of", "in", "on", "for", "with", "is", "are", "was", "were",
        "what", "which", "who", "when", "where", "why", "how", "about", "show", "tell", "me", "please", "can"
    }

    def __init__(self) -> None:
        self.last_refresh = None

    def _tokenize(self, text: str) -> List[str]:
        tokens = re.findall(r"[a-zA-Z0-9_\-\.]+", (text or "").lower())
        return [t for t in tokens if t not in self.STOP_WORDS and len(t) > 1]

    def _intent(self, question: str) -> str:
        q = (question or "").lower()
        if any(k in q for k in ["incident", "ticket", "root cause", "outage", "p1", "p2"]):
            return "incident"
        if any(k in q for k in ["device", "router", "switch", "host", "server", "ip"]):
            return "device"
        if any(k in q for k in ["metric", "cpu", "memory", "latency", "disk", "threshold", "critical"]):
            return "metric"
        return "general"

    def _build_documents(self, session) -> List[Dict[str, Any]]:
        from ..app.production_models import NetworkIncident, NetworkDevice, NetworkMetric

        docs: List[Dict[str, Any]] = []

        incidents = session.query(NetworkIncident).order_by(NetworkIncident.created_at.desc()).limit(120).all()
        for inc in incidents:
            text = " ".join([
                inc.ticket_id or "",
                inc.title or "",
                inc.description or "",
                inc.symptom_summary or "",
                inc.root_cause or "",
                inc.severity or "",
                inc.status or "",
            ])
            docs.append({
                "id": inc.ticket_id,
                "doc_type": "incident",
                "created_at": inc.created_at,
                "text": text,
                "snippet": f"{inc.ticket_id}: {inc.title} [{inc.severity}/{inc.status}]",
                "metadata": {
                    "severity": inc.severity,
                    "status": inc.status,
                    "title": inc.title,
                },
            })

        devices = session.query(NetworkDevice).order_by(NetworkDevice.updated_at.desc()).limit(120).all()
        for dev in devices:
            text = " ".join([
                dev.device_id or "",
                dev.device_name or "",
                dev.device_type or "",
                dev.vendor or "",
                dev.model or "",
                dev.ip_address or "",
                dev.location or "",
                dev.lab_network or "",
                dev.status or "",
            ])
            docs.append({
                "id": dev.device_id,
                "doc_type": "device",
                "created_at": dev.updated_at,
                "text": text,
                "snippet": f"{dev.device_id}: {dev.device_name} ({dev.device_type}) status={dev.status} ip={dev.ip_address}",
                "metadata": {
                    "status": dev.status,
                    "type": dev.device_type,
                    "network": dev.lab_network,
                },
            })

        metrics = session.query(NetworkMetric).order_by(NetworkMetric.timestamp.desc()).limit(250).all()
        for met in metrics:
            device_ref = met.device.device_id if met.device else "unknown"
            text = " ".join([
                device_ref,
                met.metric_name or "",
                str(met.metric_value),
                met.unit or "",
                met.status or "",
                str(met.threshold_warn) if met.threshold_warn is not None else "",
                str(met.threshold_crit) if met.threshold_crit is not None else "",
            ])
            docs.append({
                "id": f"metric:{device_ref}:{met.metric_name}:{met.timestamp.isoformat() if met.timestamp else 'na'}",
                "doc_type": "metric",
                "created_at": met.timestamp,
                "text": text,
                "snippet": f"metric {met.metric_name} on {device_ref} value={met.metric_value}{met.unit or ''} status={met.status}",
                "metadata": {
                    "device": device_ref,
                    "metric": met.metric_name,
                    "value": met.metric_value,
                    "status": met.status,
                },
            })

        self.last_refresh = datetime.utcnow().isoformat()
        return docs

    def _score_document(self, query_tokens: List[str], doc: Dict[str, Any], intent: str) -> float:
        doc_tokens = set(self._tokenize(doc["text"]))
        if not doc_tokens:
            return 0.0

        overlap = sum(1 for t in query_tokens if t in doc_tokens)
        overlap_score = overlap / max(1, len(set(query_tokens)))

        exact_bonus = 0.0
        q_text = " ".join(query_tokens)
        if q_text and q_text in doc["text"].lower():
            exact_bonus = 0.15

        intent_bonus = 0.15 if intent != "general" and doc["doc_type"] == intent else 0.0

        recency_bonus = 0.0
        created_at = doc.get("created_at")
        if created_at:
            age_hours = max(0.0, (datetime.utcnow() - created_at).total_seconds() / 3600.0)
            recency_bonus = max(0.0, 0.12 - min(0.12, age_hours / 1000.0))

        return overlap_score + exact_bonus + intent_bonus + recency_bonus

    def retrieve(self, session, question: str, top_k: int = 6) -> Dict[str, Any]:
        query_tokens = self._tokenize(question)
        intent = self._intent(question)
        docs = self._build_documents(session)

        scored = []
        for doc in docs:
            score = self._score_document(query_tokens, doc, intent)
            if score > 0:
                scored.append({"score": score, "doc": doc})

        scored.sort(key=lambda x: x["score"], reverse=True)
        top = scored[:top_k]

        evidence = [
            {
                "doc_type": item["doc"]["doc_type"],
                "id": item["doc"]["id"],
                "score": round(item["score"] * 100, 2),
                "snippet": item["doc"]["snippet"],
                "metadata": item["doc"].get("metadata", {}),
            }
            for item in top
        ]

        retrieval_confidence = round(min(100.0, (sum(i["score"] for i in top) / max(1, len(top))) * 100), 2) if top else 20.0

        return {
            "intent": intent,
            "query_tokens": query_tokens,
            "evidence": evidence,
            "retrieval_confidence": retrieval_confidence,
            "documents_indexed": len(docs),
            "index_last_refresh": self.last_refresh,
        }

    def answer(self, session, question: str) -> Dict[str, Any]:
        from ..app.production_models import NetworkIncident, NetworkDevice, NetworkMetric

        retrieval = self.retrieve(session, question, top_k=6)

        open_incidents = session.query(NetworkIncident).filter(NetworkIncident.status == "OPEN").count()
        critical_incidents = session.query(NetworkIncident).filter(
            NetworkIncident.status == "OPEN", NetworkIncident.severity == "P1"
        ).count()
        total_devices = session.query(NetworkDevice).count()
        non_ok_metrics = session.query(NetworkMetric).filter(NetworkMetric.status != "OK").count()

        evidence = retrieval["evidence"]

        if not evidence:
            answer = (
                "I could not find strong matching context for that question yet. "
                "Try including a ticket ID, device ID, metric name, or severity (for example: P1)."
            )
            confidence = 25.0
        else:
            top_lines = []
            for item in evidence[:4]:
                top_lines.append(f"- [{item['doc_type']}] {item['snippet']}")

            answer = (
                "Here is what I found from incidents/devices/metrics context:\n"
                + "\n".join(top_lines)
                + "\n\n"
                + f"Current posture: open_incidents={open_incidents}, critical_incidents={critical_incidents}, "
                + f"total_devices={total_devices}, non_ok_metrics={non_ok_metrics}."
            )
            confidence = round(min(100.0, 0.65 * retrieval["retrieval_confidence"] + 35.0), 2)

        suggestions = [
            "Which incidents are highest priority right now?",
            "What is the likely root cause for open P1 incidents?",
            "Show devices with degraded or down status.",
            "Summarize non-OK metrics by device.",
            "What should we fix first in the next 30 minutes?",
        ]

        return {
            "question": question,
            "answer": answer,
            "intent": retrieval["intent"],
            "confidence": confidence,
            "retrieval_confidence": retrieval["retrieval_confidence"],
            "evidence": evidence,
            "suggestions": suggestions,
            "stats": {
                "open_incidents": open_incidents,
                "critical_incidents": critical_incidents,
                "total_devices": total_devices,
                "non_ok_metrics": non_ok_metrics,
            },
        }
