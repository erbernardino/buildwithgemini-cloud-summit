"""Unit tests for Cloud Summit AI Concierge tools and logic."""

import unittest
from app.tools.calculator import calculate_schedule_timing
from app.tools.media import generate_attendee_badge
from app.tools.sessions import (
    bookmark_session,
    get_session_details,
    list_bookmarked_sessions,
    search_sessions,
)


class TestCloudSummitAgentTools(unittest.TestCase):
    """Test suite for agent tools."""

    def test_search_sessions_all(self):
        """Verify search returns all sessions when no query is passed."""
        sessions = search_sessions()
        self.assertGreaterEqual(len(sessions), 5)
        track3 = [s for s in sessions if "track3-agents" == s["id"]]
        self.assertEqual(len(track3), 1)
        self.assertIn("Build with Gemini", track3[0]["title"])

    def test_search_sessions_by_keyword(self):
        """Verify search filters by query term accurately."""
        gemini_sessions = search_sessions("gemini")
        self.assertGreaterEqual(len(gemini_sessions), 1)
        self.assertTrue(any("track3-agents" == s["id"] for s in gemini_sessions))

    def test_search_sessions_by_track(self):
        """Verify search filters by track."""
        arch_sessions = search_sessions(track="Architecture")
        self.assertGreaterEqual(len(arch_sessions), 1)
        self.assertEqual(arch_sessions[0]["id"], "track1-arch")

    def test_get_session_details_success(self):
        """Verify details lookup for existing session."""
        details = get_session_details("track3-agents")
        self.assertEqual(details["id"], "track3-agents")
        self.assertIn("Sala 103", details["room"])
        self.assertIn("ADK e A2UI", details["title"])

    def test_get_session_details_not_found(self):
        """Verify lookup returns error dictionary for nonexistent session."""
        details = get_session_details("nonexistent-id")
        self.assertIn("error", details)

    def test_bookmark_and_list_sessions(self):
        """Verify bookmarking and retrieval for an attendee."""
        attendee = "attendee_test_123"
        result = bookmark_session("track3-agents", attendee_id=attendee)
        self.assertEqual(result["status"], "success")
        self.assertIn("ADK e A2UI", result["message"])

        bookmarks = list_bookmarked_sessions(attendee_id=attendee)
        self.assertEqual(len(bookmarks), 1)
        self.assertEqual(bookmarks[0]["session_id"], "track3-agents")

    def test_calculate_schedule_timing(self):
        """Verify timing and break calculation for consecutive sessions."""
        result = calculate_schedule_timing([60, 45, 90], start_hour=9.0, break_between_minutes=15)
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["total_sessions"], 3)
        self.assertEqual(result["total_lecture_hours"], 3.25)
        self.assertEqual(result["total_break_minutes"], 30)
        self.assertEqual(result["first_session_start"], "09:00")
        self.assertEqual(len(result["timeline_slots"]), 3)
        self.assertEqual(result["timeline_slots"][0]["end"], "10:00")
        # Second session starts after 15 min break (10:15)
        self.assertEqual(result["timeline_slots"][1]["start"], "10:15")

    def test_generate_attendee_badge(self):
        """Verify attendee badge generation metadata and public url."""
        badge = generate_attendee_badge(
            attendee_name="Emerson Bernardino",
            company="Google Developer Experts",
            track_interest="Agentic AI / Build with Gemini",
        )
        self.assertEqual(badge["status"], "success")
        self.assertEqual(badge["attendee_name"], "Emerson Bernardino")
        self.assertEqual(badge["company"], "Google Developer Experts")
        self.assertTrue(badge["image_url"].startswith("https://"))


if __name__ == "__main__":
    unittest.main()
