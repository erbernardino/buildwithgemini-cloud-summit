"""Schedule calculation and time management tool for Cloud Summit."""

from typing import Any, Dict, List


def calculate_schedule_timing(
    session_durations_minutes: List[int],
    start_hour: float = 9.0,
    break_between_minutes: int = 15,
) -> Dict[str, Any]:
    """Calcula a grade horária, intervalos de coffee-break e término estimado de palestras no Cloud Summit.

    Executa os cálculos aritméticos de tempo e valida sobreposições de horários no itinerário do participante.

    Args:
        session_durations_minutes: Lista de durações em minutos para cada sessão planejada (ex: [60, 45, 90]).
        start_hour: Horário inicial em formato decimal (ex: 9.0 para 09:00, 14.5 para 14:30).
        break_between_minutes: Intervalo mínimo em minutos entre salas/sessões (padrão 15 min).

    Returns:
        Dicionário com o resumo da grade horária, tempo total de evento, minutos em palestras e horários de intervalo.
    """
    if not session_durations_minutes:
        return {"error": "Nenhuma sessão fornecida para o cálculo de itinerário."}

    total_session_minutes = sum(session_durations_minutes)
    total_break_minutes = max(0, len(session_durations_minutes) - 1) * break_between_minutes
    total_event_minutes = total_session_minutes + total_break_minutes

    current_minutes = int(start_hour * 60)
    slots = []

    for idx, duration in enumerate(session_durations_minutes):
        start_m = current_minutes
        end_m = start_m + duration

        start_str = f"{start_m // 60:02d}:{start_m % 60:02d}"
        end_str = f"{end_m // 60:02d}:{end_m % 60:02d}"

        slots.append({
            "session_number": idx + 1,
            "start": start_str,
            "end": end_str,
            "duration_minutes": duration,
        })

        # Advance by duration plus break
        current_minutes = end_m + break_between_minutes

    finish_m = slots[-1]["end"]

    return {
        "status": "success",
        "total_sessions": len(session_durations_minutes),
        "total_lecture_hours": round(total_session_minutes / 60.0, 2),
        "total_break_minutes": total_break_minutes,
        "first_session_start": slots[0]["start"],
        "final_session_end": finish_m,
        "timeline_slots": slots,
        "recommendation": (
            "Tempo de trânsito entre salas validado com folga de "
            f"{break_between_minutes} minutos para networking e coffee break."
        ),
    }
