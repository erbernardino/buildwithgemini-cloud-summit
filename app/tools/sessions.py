"""Cloud Summit Sessions and Firestore Bookmark Tools."""

import os
from datetime import datetime
from typing import Any, Dict, List, Optional

# In-memory session catalog for Google Cloud Summit
SUMMIT_CATALOG = [
    {
        "id": "keynote-01",
        "title": "Abertura Oficial: O Futuro da IA Agêntica no Google Cloud",
        "track": "Keynote",
        "room": "Auditório Principal (Main Stage)",
        "time": "09:00 - 10:00",
        "speakers": ["Sundar Pichai (Keynote Virtual)", "Google Cloud Leadership Brasil"],
        "description": "Visão geral sobre modelos Gemini, Vertex AI Agent Platform e o impacto da IA corporativa no ecossistema de nuvem.",
        "tags": ["keynote", "ia", "gemini", "agent-platform"],
    },
    {
        "id": "track1-arch",
        "title": "Trilha 1: Arquiteturas Resilientes e Multi-Region no Google Cloud",
        "track": "Cloud Architecture",
        "room": "Sala 101 - Andromeda",
        "time": "10:15 - 11:15",
        "speakers": ["Ana Ribeiro (Principal Architect)"],
        "description": "Boas práticas de alta disponibilidade, Spanner, Anthos e topologias globais com baixa latência.",
        "tags": ["architecture", "spanner", "resilience"],
    },
    {
        "id": "track2-data",
        "title": "Trilha 2: BigQuery & Gemini: Da Ingestão a Insights em Tempo Real",
        "track": "Data & AI",
        "room": "Sala 102 - Cygnus",
        "time": "11:30 - 12:30",
        "speakers": ["Carlos Mendes (Staff Data Engineer)"],
        "description": "Uso de BigQuery ML, BigFrames e Gemini Data Analytics para consultas e visualizações interativas em petabytes de dados.",
        "tags": ["data", "bigquery", "analytics"],
    },
    {
        "id": "track3-agents",
        "title": "Trilha 3: Build with Gemini: Construindo Agentes com ADK e A2UI",
        "track": "Agentic AI / Build with Gemini",
        "room": "Sala 103 - Orion (Hands-on Lab)",
        "time": "14:00 - 15:30",
        "speakers": ["Equipe Google Cloud DevRel & GDEs"],
        "description": "Workshop prático passo a passo desenvolvendo agentes empresariais com Memory Bank, Firestore, geração de imagens e interfaces visuais A2UI.",
        "tags": ["agents", "adk", "a2ui", "gemini", "swag"],
    },
    {
        "id": "track4-security",
        "title": "Trilha 4: Zero Trust, Assured Workloads e Governança com SAIF",
        "track": "DevOps & Security",
        "room": "Sala 104 - Pegasus",
        "time": "15:45 - 16:45",
        "speakers": ["Juliana Costa (Cloud Security Director)"],
        "description": "Protegendo ativos críticos com BeyondCorp, Secure AI Framework (SAIF) e Cloud KMS.",
        "tags": ["security", "zero-trust", "saif"],
    },
    {
        "id": "track5-cloudrun",
        "title": "Trilha 5: Modernizando Microsserviços e Frontends com Cloud Run",
        "track": "Cloud Native & DevOps",
        "room": "Sala 105 - Phoenix",
        "time": "17:00 - 18:00",
        "speakers": ["Roberto Silva (Serverless Lead)"],
        "description": "Deploy rápido de contêineres serverless, proxies FastAPI e escalabilidade instantânea de zero a milhares de instâncias.",
        "tags": ["serverless", "cloud-run", "fastapi"],
    },
]

# Local fallback store when Firestore is unavailable or running locally
_LOCAL_BOOKMARKS: Dict[str, List[Dict[str, Any]]] = {}


def _get_firestore_client():
    """Lazily initialize Google Cloud Firestore client if credentials and project are set."""
    try:
        from google.cloud import firestore

        project_id = os.environ.get("GOOGLE_CLOUD_PROJECT") or os.environ.get("GCP_PROJECT")
        return firestore.Client(project=project_id)
    except Exception:
        return None


def search_sessions(query: str = "", track: str = "") -> List[Dict[str, Any]]:
    """Busca palestras e workshops na agenda oficial do Google Cloud Summit.

    Args:
        query: Termo de busca (título, descrição, tecnologia ou palestrante).
        track: Filtro por trilha específica (ex: 'Keynote', 'Agentic AI / Build with Gemini', 'Data & AI').

    Returns:
        Lista de sessões encontradas com horários, salas e palestrantes.
    """
    query_lower = query.lower().strip()
    track_lower = track.lower().strip()

    results = []
    for s in SUMMIT_CATALOG:
        match_query = (
            not query_lower
            or query_lower in s["title"].lower()
            or query_lower in s["description"].lower()
            or any(query_lower in tag for tag in s["tags"])
            or any(query_lower in spk.lower() for spk in s["speakers"])
        )
        match_track = not track_lower or track_lower in s["track"].lower()

        if match_query and match_track:
            results.append(s)

    return results


def get_session_details(session_id: str) -> Dict[str, Any]:
    """Obtém detalhes completos de uma sessão específica do Google Cloud Summit pelo ID.

    Args:
        session_id: O identificador da sessão (ex: 'track3-agents', 'keynote-01').

    Returns:
        Dicionário com informações detalhadas da sessão.
    """
    for s in SUMMIT_CATALOG:
        if s["id"].lower() == session_id.lower():
            return s
    return {"error": f"Sessão com ID '{session_id}' não encontrada no catálogo do Cloud Summit."}


def bookmark_session(session_id: str, attendee_id: str = "attendee_default") -> Dict[str, Any]:
    """Salva uma sessão nos favoritos / agenda pessoal do participante no Firestore.

    Args:
        session_id: O ID da sessão a ser favoritada (ex: 'track3-agents').
        attendee_id: Identificador ou e-mail do participante.

    Returns:
        Status da operação e resumo da sessão favoritada.
    """
    session = get_session_details(session_id)
    if "error" in session:
        return session

    record = {
        "session_id": session["id"],
        "title": session["title"],
        "track": session["track"],
        "room": session["room"],
        "time": session["time"],
        "bookmarked_at": datetime.utcnow().isoformat(),
        "attendee_id": attendee_id,
    }

    db = _get_firestore_client()
    if db:
        try:
            doc_ref = db.collection("summit_bookmarks").document(f"{attendee_id}_{session['id']}")
            doc_ref.set(record)
            storage_type = "Firestore"
        except Exception:
            # Fallback to local store if Firestore write fails
            _save_local_bookmark(attendee_id, record)
            storage_type = "Local Memory (Firestore offline)"
    else:
        _save_local_bookmark(attendee_id, record)
        storage_type = "Local Memory"

    return {
        "status": "success",
        "message": f"Sessão '{session['title']}' favoritada com sucesso na sua agenda!",
        "storage": storage_type,
        "session": record,
    }


def list_bookmarked_sessions(attendee_id: str = "attendee_default") -> List[Dict[str, Any]]:
    """Lista todas as sessões salvas na agenda do participante no Firestore.

    Args:
        attendee_id: Identificador ou e-mail do participante.

    Returns:
        Lista de sessões salvas na agenda pessoal.
    """
    db = _get_firestore_client()
    if db:
        try:
            docs = (
                db.collection("summit_bookmarks")
                .where("attendee_id", "==", attendee_id)
                .stream()
            )
            bookmarks = [doc.to_dict() for doc in docs]
            if bookmarks:
                return bookmarks
        except Exception:
            pass

    return _LOCAL_BOOKMARKS.get(attendee_id, [])


def _save_local_bookmark(attendee_id: str, record: Dict[str, Any]) -> None:
    if attendee_id not in _LOCAL_BOOKMARKS:
        _LOCAL_BOOKMARKS[attendee_id] = []
    # Avoid duplicate bookmarks
    for item in _LOCAL_BOOKMARKS[attendee_id]:
        if item["session_id"] == record["session_id"]:
            return
    _LOCAL_BOOKMARKS[attendee_id].append(record)
