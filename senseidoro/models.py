from datetime import datetime
from enum import Enum
from typing import Optional

from sqlmodel import Field, Relationship, SQLModel


class SessionState(str, Enum):
    ACTIVE = "active"
    WORK = "work"
    BREAK = "break"
    DONE = "done"


class User(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)

    username: str = Field(index=True)
    minutes_worked: int = Field(default=0)
    subscription_expires_at: Optional[datetime] = Field(default=None)
    last_vote_at: Optional[datetime] = Field(default=None)


class Server(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)

    name: str = Field(index=True)
    subscription_expires_at: Optional[datetime] = Field(default=None)

    sessions: list["Session"] = Relationship(back_populates="server")


class Session(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)

    name: str = Field(default="Pomodoro")
    guild_id: int = Field(foreign_key="server.id")
    activation_channel_id: int
    work_time: int = Field(default=25)
    break_time: int = Field(default=5)
    repetitions: int = Field(default=4)
    mute_admins: bool = Field(default=True)

    server: Server = Relationship(back_populates="sessions")
    session_instances: list["SessionInstance"] = Relationship(back_populates="parent")


class SessionInstance(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)

    work_channel_id: Optional[int] = None
    started_at: datetime = Field(default_factory=datetime.utcnow)
    state: SessionState = Field(default=SessionState.WORK)
    current_repetition: int = Field(default=0)

    parent_id: int = Field(foreign_key="session.id")
    parent: "Session" = Relationship(back_populates="session_instances")
