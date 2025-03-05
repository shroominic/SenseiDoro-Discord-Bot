from datetime import datetime
from enum import Enum
from typing import Optional

from sqlmodel import Field, Relationship, SQLModel

__all__ = ["User", "Server", "Session", "ActiveSession"]


class SessionState(str, Enum):
    WORK = "work"
    BREAK = "break"
    FINISHED = "finished"


class UserBase(SQLModel):
    username: str = Field(index=True)
    minutes_worked: int = Field(default=0)
    subscription_expires_at: Optional[datetime] = Field(default=None)
    last_vote_at: Optional[datetime] = Field(default=None)


class User(UserBase, table=True):
    id: int = Field(default=None, primary_key=True)
    sessions: list["Session"] = Relationship(back_populates="started_by_user")
    active_sessions: list["ActiveSession"] = Relationship(back_populates="started_by_user")


class ServerBase(SQLModel):
    name: str = Field(index=True)
    subscription_expires_at: Optional[datetime] = Field(default=None)


class Server(ServerBase, table=True):
    id: int = Field(default=None, primary_key=True)
    sessions: list["Session"] = Relationship(back_populates="server")


class SessionBase(SQLModel):
    name: str = Field(default="Pomodoro")
    guild_id: int = Field(foreign_key="server.id")
    activation_channel_id: int
    work_time: int = Field(default=25)
    break_time: int = Field(default=5)
    repetitions: int = Field(default=4)
    mute_admins: bool = Field(default=True)


class Session(SessionBase, table=True):
    id: int = Field(default=None, primary_key=True)
    started_by_user_id: int = Field(foreign_key="user.id")

    server: Server = Relationship(back_populates="sessions")
    started_by_user: User = Relationship(back_populates="sessions")
    active_sessions: list["ActiveSession"] = Relationship(back_populates="parent")


class ActiveSessionBase(SQLModel):
    work_channel_id: int
    started_at: datetime = Field(default_factory=datetime.utcnow)
    started_by_user_id: int = Field(foreign_key="user.id")
    participants: str = Field(default="[]")  # JSON string of participant IDs
    state: SessionState = Field(default=SessionState.WORK)
    current_repetition: int = Field(default=0)


class ActiveSession(ActiveSessionBase, table=True):
    id: int = Field(default=None, primary_key=True)
    parent_id: int = Field(foreign_key="session.id")

    parent: Session = Relationship(back_populates="active_sessions")
    started_by_user: User = Relationship(back_populates="active_sessions")
