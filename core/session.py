"""In-memory multi-turn session state manager. No database or file persistence."""

from typing import Optional


class SessionManager:
    """In-memory store for multi-turn component generation sessions."""

    def __init__(self) -> None:
        """Initialize empty sessions dict."""
        self._sessions: dict[str, dict] = {}

    def get_or_create(self, session_id: str) -> dict:
        """Return existing session or create a new one with empty state."""
        if session_id not in self._sessions:
            self._sessions[session_id] = {"history": [], "last_component": ""}
        return self._sessions[session_id]

    def get_last_component(self, session_id: str) -> str:
        """Return the most recently generated component, or empty string."""
        session = self._sessions.get(session_id)
        return session["last_component"] if session else ""

    def push(self, session_id: str, user_prompt: str, component_code: str) -> None:
        """Append user+assistant turn to history and update last component."""
        session = self.get_or_create(session_id)
        session["history"].append({"role": "user", "content": user_prompt})
        session["history"].append({"role": "assistant", "content": component_code})
        session["last_component"] = component_code
        if len(session["history"]) > 10:
            session["history"] = session["history"][-10:]

    def reset(self, session_id: str) -> None:
        """Clear all state for the given session."""
        self._sessions[session_id] = {"history": [], "last_component": ""}


session_manager = SessionManager()
