from __future__ import annotations

from typing import Optional, Sequence

import trafaret as t

from ai.backend.common.types import AccessKey, AgentId, ResourceSlot, SessionId

from ..models import AgentRow, SessionRow
from .types import AbstractScheduler, KernelInfo


class MOFScheduler(AbstractScheduler):
    """Minimum Occupied slot First Scheduler"""

    config_iv = t.Dict({}).allow_extra("*")

    def pick_session(
        self,
        total_capacity: ResourceSlot,
        pending_sessions: Sequence[SessionRow],
        existing_sessions: Sequence[SessionRow],
    ) -> Optional[SessionId]:
        # Just pick the first pending session.
        return SessionId(pending_sessions[0].id)

    def _assign_agent(
        self,
        agents: Sequence[AgentRow],
        access_key: AccessKey,
        requested_slots: ResourceSlot,
    ) -> Optional[AgentId]:
        # return min occupied slot agent or None
        return next(
            (
                one_agent.id
                for one_agent in (
                    sorted(
                        (
                            agent
                            for agent in agents
                            if ((agent.available_slots - agent.occupied_slots) >= requested_slots)
                        ),
                        key=lambda a: a.occupied_slots,
                    )
                )
            ),
            None,
        )

    def assign_agent_for_session(
        self,
        agents: Sequence[AgentRow],
        pending_session: SessionRow,
    ) -> Optional[AgentId]:
        return self._assign_agent(
            agents,
            pending_session.access_key,
            pending_session.requested_slots,
        )

    def assign_agent_for_kernel(
        self,
        agents: Sequence[AgentRow],
        pending_kernel: KernelInfo,
    ) -> Optional[AgentId]:
        return self._assign_agent(
            agents,
            pending_kernel.access_key,
            pending_kernel.requested_slots,
        )
