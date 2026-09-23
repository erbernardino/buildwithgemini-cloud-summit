"""Cloud Summit AI Concierge — Agent Definition."""

import os
from typing import Any, Optional

from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.apps import App
from google.adk.models import Gemini
from google.adk.tools.preload_memory_tool import PreloadMemoryTool
from google.genai import types

from .a2ui_utils import a2ui_callback
from .tools.calculator import calculate_schedule_timing
from .tools.media import generate_attendee_badge
from .tools.sessions import (
    bookmark_session,
    get_session_details,
    list_bookmarked_sessions,
    search_sessions,
)


def _build_system_instruction() -> str:
    """Builds system prompt integrating persona, domain instructions and A2UI v0.8 guidance."""
    base_role = (
        "Você é o Cloud Summit AI Concierge, o assistente oficial inteligente do Google Cloud Summit. "
        "Seu objetivo é guiar participantes pelas trilhas técnicas, palestras, keynotes, workshops práticos "
        "(com destaque especial para a Trilha 3: Build with Gemini e IA Agêntica), ajudar a favoritar sessões "
        "na agenda pessoal (Firestore), gerar crachás visuais personalizados (Gemini Image Gen) e calcular "
        "grades horárias de itinerário.\n\n"
        "Comportamento e Diretrizes:\n"
        "1. Seja cordial, técnico, prestativo e entusiasta sobre as tecnologias do Google Cloud.\n"
        "2. Sempre que o usuário perguntar sobre palestras ou tópicos da conferência, utilize a ferramenta `search_sessions`.\n"
        "3. Quando o participante pedir para salvar ou favoritar palestras, utilize `bookmark_session` e confirme o armazenamento.\n"
        "4. Quando o participante quiser ver sua programação salva, use `list_bookmarked_sessions`.\n"
        "5. Quando o participante quiser gerar um crachá de participante, use `generate_attendee_badge`.\n"
        "6. Para planejar horários, transições entre salas e tempos de intervalo, utilize `calculate_schedule_timing`.\n"
        "7. Lembre-se das preferências do usuário entre turnos e conversas (interesses técnicos, trilha favorita, empresa).\n"
    )

    # Attempt to load A2uiSchemaManager if a2ui-agent-sdk is installed
    try:
        from a2ui.basic_catalog.provider import BasicCatalog
        from a2ui.schema.manager import A2uiSchemaManager

        schema_manager = A2uiSchemaManager(
            version="0.8",
            catalogs=[BasicCatalog.get_config("0.8")],
        )
        return schema_manager.generate_system_prompt(
            role_description=base_role,
            workflow_description="Analyze the attendee request, invoke appropriate tools, and return structured A2UI UI cards/tables when presenting sessions, badges, or schedules.",
            ui_description=(
                "Keep every surface tiny and flat: ONE Card > ONE Column > a few Text rows. "
                "Never nest a Card inside a Card. "
                "Use ONLY these components: Card, Column, Row, Text, and Image. Do not use "
                "Table or Heading (unsupported), or Buttons, actions, or forms (they do "
                "nothing in adk web). "
                "You may include one Image component, but only when you have a public https "
                "URL for the image (such as the URL returned by generate_attendee_badge). "
                "Set the Image url to that exact https link: {\"Image\": {\"url\": {\"literalString\": \"https://...\"}}}. "
                "Never point an Image at a bare filename or artifact name. If you do not have a public URL, add a short Text line noting the image instead. "
                "No markdown in text; use usageHint property ('h1', 'h2', 'body') for headings and emphasis. "
                "When returning A2UI, output ONLY the raw A2UI JSON array — no prose, and never wrap it in <a2a_datapart_json> tags."
            ),
            include_schema=True,
            include_examples=True,
        )
    except Exception:
        # Robust fallback prompt conforming strictly to A2UI v0.8 specification
        a2ui_instructions = (
            "\n\n### Diretrizes de Interface A2UI (v0.8):\n"
            "Quando apresentar resultados de sessões, catálogos ou crachás, você pode emitir uma interface rica A2UI em JSON v0.8.\n"
            "Mantenha a superfície plana: Card > Column > Text / Image. Use apenas links HTTPS públicos em componentes Image.\n"
        )
        return base_role + a2ui_instructions


# Callback para enviar sessão ao Vertex AI Memory Bank ao final de cada turno
async def generate_memories_callback(callback_context: CallbackContext) -> Optional[Any]:
    """Writes persistent conversational memories to the Memory Bank service."""
    try:
        await callback_context.add_session_to_memory()
    except Exception:
        # In local in-memory run, Memory Bank client may be inactive
        pass
    return None


# Root Agent Definition
root_agent = Agent(
    name="cloud_summit_concierge",
    model=Gemini(
        model=os.environ.get("GEMINI_MODEL", "gemini-2.5-flash"),
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=_build_system_instruction(),
    tools=[
        PreloadMemoryTool(),
        search_sessions,
        get_session_details,
        bookmark_session,
        list_bookmarked_sessions,
        generate_attendee_badge,
        calculate_schedule_timing,
    ],
    after_model_callback=a2ui_callback,
    after_agent_callback=generate_memories_callback,
)

app = App(
    root_agent=root_agent,
    name="cloudsummit_agent",
)
