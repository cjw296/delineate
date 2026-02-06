import json
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .client import LinearClient
from .queries import (
    ATTACHMENTS,
    COMMENTS,
    CYCLES,
    DOCUMENTS,
    INITIATIVES,
    ISSUE_LABELS,
    ISSUES,
    PROJECT_MILESTONES,
    PROJECTS,
    TEAMS,
    USERS,
    WORKFLOW_STATES,
)


def entity_path(base_dir: Path, entity_type: str, uuid: str) -> Path:
    prefix = uuid[:4]
    path = base_dir / entity_type / prefix / f"{uuid}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def write_entity(base_dir: Path, entity_type: str, entity: dict[str, Any]) -> Path:
    uuid: str = entity["id"]
    path = entity_path(base_dir, entity_type, uuid)
    path.write_text(json.dumps(entity, indent=2) + "\n")
    return path


class LatestData(dict[str, str]):
    @classmethod
    def load(cls, path: Path) -> "LatestData":
        if path.exists():
            return cls(json.loads(path.read_text()))
        return cls()

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(dict(self), indent=2) + "\n")


@dataclass
class Export:
    entity_type: str
    query: str
    connection_path: str
    markdown_fields: tuple[str, ...] = ()

    def items(
        self, client: LinearClient, latest: LatestData | None = None
    ) -> Iterator[dict[str, Any]]:
        variables: dict[str, Any] = {}
        if latest is not None and self.entity_type in latest:
            variables["filter"] = {"updatedAt": {"gt": latest[self.entity_type]}}
        max_updated: str | None = None
        for node in client.paginate(self.query, self.connection_path, variables):
            updated_at: str | None = node.get("updatedAt")
            if updated_at is not None:
                if max_updated is None or updated_at > max_updated:
                    max_updated = updated_at
            yield node
        if latest is not None and max_updated is not None:
            latest[self.entity_type] = max_updated


class StaticExport(Export):
    def items(
        self, client: LinearClient, latest: LatestData | None = None
    ) -> Iterator[dict[str, Any]]:
        yield from client.paginate(self.query, self.connection_path)


EXPORTS: dict[str, Export] = {
    "teams": StaticExport(
        entity_type="teams",
        query=TEAMS,
        connection_path="teams",
    ),
    "users": StaticExport(
        entity_type="users",
        query=USERS,
        connection_path="users",
    ),
    "issues": Export(
        entity_type="issues",
        query=ISSUES,
        connection_path="issues",
        markdown_fields=("description",),
    ),
    "comments": Export(
        entity_type="comments",
        query=COMMENTS,
        connection_path="comments",
        markdown_fields=("body",),
    ),
    "projects": Export(
        entity_type="projects",
        query=PROJECTS,
        connection_path="projects",
        markdown_fields=("description",),
    ),
    "initiatives": StaticExport(
        entity_type="initiatives",
        query=INITIATIVES,
        connection_path="initiatives",
        markdown_fields=("description",),
    ),
    "cycles": StaticExport(
        entity_type="cycles",
        query=CYCLES,
        connection_path="cycles",
        markdown_fields=("description",),
    ),
    "issue_labels": StaticExport(
        entity_type="issue_labels",
        query=ISSUE_LABELS,
        connection_path="issueLabels",
    ),
    "documents": Export(
        entity_type="documents",
        query=DOCUMENTS,
        connection_path="documents",
        markdown_fields=("content",),
    ),
    "workflow_states": StaticExport(
        entity_type="workflow_states",
        query=WORKFLOW_STATES,
        connection_path="workflowStates",
    ),
    "attachments": Export(
        entity_type="attachments",
        query=ATTACHMENTS,
        connection_path="attachments",
    ),
    "project_milestones": StaticExport(
        entity_type="project_milestones",
        query=PROJECT_MILESTONES,
        connection_path="projectMilestones",
        markdown_fields=("description",),
    ),
}
