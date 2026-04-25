from __future__ import annotations

from sqlalchemy import select

from app.core.config import get_settings
from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.membership import Membership
from app.models.runtime_config import AgentConfig, KnowledgeProject, PromptSection, RuntimeConfigVersion, ToolDefinition
from app.models.tenant import Tenant
from app.models.user import User
from app.runtime.strategies.mcmv_tenda_rj import MCMVTendaRJStrategy
from app.runtime.tools import ScheduleTimeTool, SendMediaTool, SimulaCompletoTool, SimulaTool


def main() -> None:
    settings = get_settings()
    if not settings.seed_admin_email or not settings.seed_admin_password:
        print("Seed skipped: SEED_ADMIN_EMAIL or SEED_ADMIN_PASSWORD not configured.")
        return

    email = settings.seed_admin_email.lower().strip()

    with SessionLocal() as db:
        tenant = db.scalar(select(Tenant).where(Tenant.slug == "tenda-rj"))
        if tenant is None:
            tenant = Tenant(
                slug="tenda-rj",
                name="Tenda RJ",
                operation_type="MCMV",
                city="Rio de Janeiro",
                crm_provider="facilita",
                status="active",
            )
            db.add(tenant)
            db.flush()

        user = db.scalar(select(User).where(User.email == email))
        if user is None:
            user = User(
                email=email,
                full_name=settings.seed_admin_name,
                password_hash=hash_password(settings.seed_admin_password),
                status="active",
            )
            db.add(user)
            db.flush()
        else:
            user.full_name = settings.seed_admin_name
            # Demo seed: keep the Render secret as the source of truth while we iterate.
            user.password_hash = hash_password(settings.seed_admin_password)
            user.status = "active"

        membership = db.scalar(
            select(Membership).where(
                Membership.user_id == user.id,
                Membership.tenant_id == tenant.id,
            )
        )
        if membership is None:
            membership = Membership(
                user_id=user.id,
                tenant_id=tenant.id,
                role="sati_admin",
                is_default=True,
                status="active",
            )
            db.add(membership)
        else:
            membership.role = "sati_admin"
            membership.is_default = True
            membership.status = "active"

        seed_tenda_runtime_config(db, tenant)

        db.commit()
        print(f"Seed ready: {email} -> {tenant.slug}")


def seed_tenda_runtime_config(db, tenant: Tenant) -> None:
    agent = db.scalar(
        select(AgentConfig).where(
            AgentConfig.tenant_id == tenant.id,
            AgentConfig.key == "sdr_maju",
        )
    )
    system_prompt = MCMVTendaRJStrategy.build_system_prompt("{current_moment}")
    if agent is None:
        agent = AgentConfig(
            tenant_id=tenant.id,
            key="sdr_maju",
            name="SDR Maju",
            description=(
                "Assistente virtual da Tenda Rio de Janeiro para atendimento MCMV, "
                "simulacao inicial e pre-agendamento."
            ),
            model=MCMVTendaRJStrategy.config.model,
            system_prompt=system_prompt,
            max_tokens=MCMVTendaRJStrategy.config.max_tokens,
            temperature=0.3,
            status="active",
        )
        db.add(agent)
        db.flush()
    else:
        agent.name = "SDR Maju"
        agent.description = (
            "Assistente virtual da Tenda Rio de Janeiro para atendimento MCMV, "
            "simulacao inicial e pre-agendamento."
        )
        agent.model = MCMVTendaRJStrategy.config.model
        agent.system_prompt = system_prompt
        agent.max_tokens = MCMVTendaRJStrategy.config.max_tokens
        agent.temperature = 0.3
        agent.status = "active"

    runtime_version = db.scalar(
        select(RuntimeConfigVersion).where(
            RuntimeConfigVersion.tenant_id == tenant.id,
            RuntimeConfigVersion.key == "tenda_rj_maju_v1",
        )
    )
    if runtime_version is None:
        runtime_version = RuntimeConfigVersion(
            tenant_id=tenant.id,
            agent_config_id=agent.id,
            key="tenda_rj_maju_v1",
            name="TendaRJ / Maju v1",
            version="v1",
            status="published",
            channel_mode="playground",
            notes="Primeira configuracao publicada: Playground GPT antes do WhatsApp.",
        )
        db.add(runtime_version)
    else:
        runtime_version.agent_config_id = agent.id
        runtime_version.name = "TendaRJ / Maju v1"
        runtime_version.version = "v1"
        runtime_version.status = "published"
        runtime_version.channel_mode = "playground"
        runtime_version.notes = "Primeira configuracao publicada: Playground GPT antes do WhatsApp."

    prompt_sections = [
        ("persona", "Persona e objetivo", "Maju, SDR virtual da Tenda RJ para atendimento MCMV.", 10),
        ("memoria", "Memoria continua", "Nao reiniciar atendimento; retomar do ponto onde parou.", 20),
        ("simulacao", "Simulacao inicial", "Coletar comprovacao de renda, FGTS e renda familiar.", 30),
        ("agendamento", "Agendamento", "Pre-agendar data/horario e nao reagendar sem necessidade.", 40),
        ("restricoes", "Restricoes", "Nao inventar, nao negociar diretamente, uma pergunta por mensagem.", 50),
    ]
    for key, title, content, sort_order in prompt_sections:
        section = db.scalar(
            select(PromptSection).where(
                PromptSection.tenant_id == tenant.id,
                PromptSection.agent_config_id == agent.id,
                PromptSection.key == key,
            )
        )
        if section is None:
            section = PromptSection(
                tenant_id=tenant.id,
                agent_config_id=agent.id,
                key=key,
                title=title,
                content=content,
                sort_order=sort_order,
                is_active=True,
            )
            db.add(section)
        else:
            section.title = title
            section.content = content
            section.sort_order = sort_order
            section.is_active = True

    for tool in (SimulaTool, SimulaCompletoTool, ScheduleTimeTool, SendMediaTool):
        definition = db.scalar(
            select(ToolDefinition).where(
                ToolDefinition.tenant_id == tenant.id,
                ToolDefinition.key == tool.name,
            )
        )
        if definition is None:
            definition = ToolDefinition(
                tenant_id=tenant.id,
                key=tool.name,
                name=tool.name,
                description=tool.description,
                schema=tool.json_schema(),
                is_enabled=True,
                is_core=True,
            )
            db.add(definition)
        else:
            definition.name = tool.name
            definition.description = tool.description
            definition.schema = tool.json_schema()
            definition.is_enabled = True
            definition.is_core = True

    projects = [
        ("aurora_iguacu", "Aurora Iguacu", "Baixada Fluminense", "Nova Iguacu", "Lancamento", 1800, "2 quartos"),
        ("solar_trindade", "Solar Trindade", "Baixada Fluminense", "Sao Goncalo", "Em obra", 2000, "2 quartos"),
        ("soul_taqua_clube", "Soul Taqua Clube", "Jacarepagua", "Taquara", "Lancamento", 4500, "2 quartos"),
        ("soul_taqua_i", "Soul Taqua I", "Jacarepagua", "Taquara", "Pronto para morar", 4000, "2 quartos"),
        ("bosque_jacarepagua", "Bosque Jacarepagua", "Jacarepagua", "Tanque", "Disponivel", 2400, "2 quartos"),
        ("parque_hortensia", "Parque Hortensia", "Zona Oeste", "Campo Grande", "Disponivel", 2300, "2 quartos"),
        ("parque_orquidea", "Parque Orquidea", "Zona Oeste", "Campo Grande", "Ultimas unidades", 2300, "2 quartos"),
        ("porto_valencia", "Porto Valencia", "Zona Oeste", "Campo Grande", "Disponivel", 2300, "2 quartos"),
        ("estacao_rio_cordovil", "Estacao Rio - Cordovil", "Zona Norte", "Cordovil", "Disponivel", 2100, "2 quartos"),
        ("elevato_bonsucesso", "Elevato Bonsucesso", "Zona Norte", "Bonsucesso", "Disponivel", 3000, "2 quartos com elevador"),
    ]
    for slug, name, region, neighborhood, status, min_income, typology in projects:
        project = db.scalar(
            select(KnowledgeProject).where(
                KnowledgeProject.tenant_id == tenant.id,
                KnowledgeProject.slug == slug,
            )
        )
        highlights = ["Minha Casa Minha Vida", "Atendimento Tenda RJ", "Simulacao inicial"]
        if project is None:
            project = KnowledgeProject(
                tenant_id=tenant.id,
                slug=slug,
                name=name,
                region=region,
                city_neighborhood=neighborhood,
                status=status,
                min_income=min_income,
                typology=typology,
                highlights=highlights,
                is_active=True,
            )
            db.add(project)
        else:
            project.name = name
            project.region = region
            project.city_neighborhood = neighborhood
            project.status = status
            project.min_income = min_income
            project.typology = typology
            project.highlights = highlights
            project.is_active = True


if __name__ == "__main__":
    main()
