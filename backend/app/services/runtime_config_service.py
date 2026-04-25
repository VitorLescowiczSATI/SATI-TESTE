from __future__ import annotations

from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.runtime_config import AgentConfig, KnowledgeProject, RuntimeConfigVersion, ToolDefinition


def get_published_runtime_config(db: Session, tenant_id: str) -> RuntimeConfigVersion:
    config = db.scalar(
        select(RuntimeConfigVersion)
        .options(joinedload(RuntimeConfigVersion.agent_config))
        .where(
            RuntimeConfigVersion.tenant_id == tenant_id,
            RuntimeConfigVersion.status == "published",
        )
        .order_by(RuntimeConfigVersion.updated_at.desc())
        .limit(1)
    )
    if config is None:
        raise HTTPException(
            status_code=503,
            detail="Nenhuma configuracao runtime publicada para este workspace.",
        )
    return config


def build_runtime_prompt(db: Session, runtime_config: RuntimeConfigVersion) -> str:
    prompt = runtime_config.agent_config.system_prompt.replace(
        "{current_moment}",
        datetime.now(timezone.utc).isoformat(),
    )
    projects = db.scalars(
        select(KnowledgeProject)
        .where(
            KnowledgeProject.tenant_id == runtime_config.tenant_id,
            KnowledgeProject.is_active.is_(True),
        )
        .order_by(KnowledgeProject.region.asc(), KnowledgeProject.name.asc())
    ).all()

    if not projects:
        return prompt

    catalog_lines = [
        "\n# Catalogo configurado do workspace",
        "Use apenas estes empreendimentos quando precisar citar opcoes:",
    ]
    for project in projects:
        min_income = f"R$ {project.min_income:,.0f}".replace(",", ".") if project.min_income else "nao informado"
        catalog_lines.append(
            "- "
            f"{project.name}: regiao {project.region}, bairro/cidade {project.city_neighborhood or 'nao informado'}, "
            f"status {project.status or 'nao informado'}, renda minima {min_income}, tipologia {project.typology or 'nao informada'}."
        )
    return f"{prompt}\n" + "\n".join(catalog_lines)


def list_enabled_tools(db: Session, tenant_id: str) -> list[ToolDefinition]:
    return db.scalars(
        select(ToolDefinition)
        .where(
            ToolDefinition.tenant_id == tenant_id,
            ToolDefinition.is_enabled.is_(True),
        )
        .order_by(ToolDefinition.key.asc())
    ).all()


def get_runtime_config_payload(db: Session, tenant_id: str) -> dict:
    config = get_published_runtime_config(db, tenant_id)
    tools = db.scalars(
        select(ToolDefinition)
        .where(ToolDefinition.tenant_id == tenant_id)
        .order_by(ToolDefinition.key.asc())
    ).all()
    projects = db.scalars(
        select(KnowledgeProject)
        .where(KnowledgeProject.tenant_id == tenant_id)
        .order_by(KnowledgeProject.region.asc(), KnowledgeProject.name.asc())
    ).all()

    return {
        "id": config.id,
        "key": config.key,
        "name": config.name,
        "version": config.version,
        "status": config.status,
        "channel_mode": config.channel_mode,
        "notes": config.notes,
        "agent": {
            "id": config.agent_config.id,
            "key": config.agent_config.key,
            "name": config.agent_config.name,
            "description": config.agent_config.description,
            "model": config.agent_config.model,
            "max_tokens": config.agent_config.max_tokens,
            "temperature": config.agent_config.temperature,
            "status": config.agent_config.status,
            "system_prompt": config.agent_config.system_prompt,
        },
        "tools": [
            {
                "id": tool.id,
                "key": tool.key,
                "name": tool.name,
                "description": tool.description,
                "is_enabled": tool.is_enabled,
                "is_core": tool.is_core,
            }
            for tool in tools
        ],
        "projects": [
            {
                "id": project.id,
                "slug": project.slug,
                "name": project.name,
                "region": project.region,
                "city_neighborhood": project.city_neighborhood,
                "status": project.status,
                "min_income": project.min_income,
                "typology": project.typology,
                "highlights": project.highlights or [],
                "is_active": project.is_active,
            }
            for project in projects
        ],
    }


def update_runtime_config(
    db: Session,
    tenant_id: str,
    *,
    model: str | None = None,
    max_tokens: int | None = None,
    temperature: float | None = None,
    system_prompt: str | None = None,
    enabled_tools: dict[str, bool] | None = None,
) -> RuntimeConfigVersion:
    config = get_published_runtime_config(db, tenant_id)
    agent: AgentConfig = config.agent_config

    if model is not None:
        agent.model = model.strip()
    if max_tokens is not None:
        agent.max_tokens = max_tokens
    if temperature is not None:
        agent.temperature = temperature
    if system_prompt is not None:
        agent.system_prompt = system_prompt.strip()

    if enabled_tools:
        tools = db.scalars(
            select(ToolDefinition).where(ToolDefinition.tenant_id == tenant_id)
        ).all()
        for tool in tools:
            if tool.key in enabled_tools:
                tool.is_enabled = bool(enabled_tools[tool.key])

    db.add(agent)
    db.add(config)
    db.commit()
    db.refresh(config)
    return config
