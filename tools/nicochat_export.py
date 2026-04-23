from __future__ import annotations

import argparse
import json
import os
import sys
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


DEFAULT_BASE_URL = "https://app.nicochat.com.br/api"


@dataclass(frozen=True)
class Endpoint:
    key: str
    path: str
    paginated: bool = True
    pii: bool = False
    notes: str = ""
    params: tuple[tuple[str, str], ...] = ()


SAFE_ENDPOINTS: tuple[Endpoint, ...] = (
    Endpoint("flow_sub_flows", "/flow/sub-flows", notes="Lista de subfluxos. Endpoint mais citado nas docs."),
    Endpoint("flow_subflows_alt", "/flow/subflows", notes="Variação encontrada nos achados iniciais."),
    Endpoint("flow_agents", "/flow/agents", notes="Agentes humanos/operacionais vinculados ao fluxo."),
    Endpoint("flow_ai_agents", "/flow/ai-agents", notes="Agentes de IA configurados no Nicochat."),
    Endpoint("flow_user_fields", "/flow/user-fields", notes="Campos customizados de usuário/lead."),
    Endpoint("flow_bot_fields", "/flow/bot-fields", notes="Campos globais/bot fields do fluxo."),
    Endpoint("flow_tags", "/flow/tags", notes="Tags usadas no atendimento."),
    Endpoint("flow_whatsapp_templates", "/flow/whatsapp-templates", notes="Templates WhatsApp vinculados ao flow."),
    Endpoint("whatsapp_template_list", "/whatsapp-template/list", notes="Variação de listagem de templates WhatsApp."),
    Endpoint("flow_template_installs", "/flow/template-installs", notes="Templates instalados no flow."),
    Endpoint("flow_bot_users_count", "/flow/bot-users-count", paginated=False, notes="Contagem de leads/usuários do bot."),
    Endpoint("flow_custom_events", "/flow/custom-events", notes="Eventos customizados do flow."),
    Endpoint("openai_embeddings", "/openai-embeddings", notes="Base de conhecimento/embeddings, quando disponível."),
)


PII_ENDPOINTS: tuple[Endpoint, ...] = (
    Endpoint("flow_bot_users", "/flow/bot-users", pii=True, notes="Contatos/leads. Pode conter PII."),
    Endpoint("flow_conversations", "/flow/conversations", pii=True, notes="Conversas. Pode conter PII."),
)


def load_env_file(path: Path) -> None:
    if not path.exists():
        return

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


def parse_key_values(values: list[str]) -> dict[str, str]:
    parsed: dict[str, str] = {}
    for item in values:
        if "=" not in item:
            raise SystemExit(f"Parametro invalido: {item}. Use KEY=VALUE.")
        key, value = item.split("=", 1)
        parsed[key.strip()] = value.strip()
    return parsed


def build_url(base_url: str, path: str, params: dict[str, Any] | None = None) -> str:
    url = f"{base_url.rstrip('/')}/{path.lstrip('/')}"
    clean_params = {key: value for key, value in (params or {}).items() if value not in (None, "")}
    if clean_params:
        url = f"{url}?{urlencode(clean_params)}"
    return url


def request_json(base_url: str, path: str, token: str, params: dict[str, Any]) -> dict[str, Any]:
    url = build_url(base_url, path, params)
    request = Request(
        url,
        headers={
            "Accept": "application/json",
            "Authorization": f"Bearer {token}",
            "User-Agent": "sati-ia-nicochat-export/0.1",
        },
        method="GET",
    )

    try:
        with urlopen(request, timeout=30) as response:
            body = response.read().decode("utf-8")
            return {
                "ok": True,
                "status_code": response.status,
                "url": url,
                "body": json.loads(body) if body else None,
            }
    except HTTPError as error:
        error_body = error.read().decode("utf-8", errors="replace")
        return {
            "ok": False,
            "status_code": error.code,
            "url": url,
            "error": error.reason,
            "body": parse_json_or_text(error_body),
        }
    except URLError as error:
        return {
            "ok": False,
            "status_code": None,
            "url": url,
            "error": str(error.reason),
            "body": None,
        }


def parse_json_or_text(value: str) -> Any:
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return value


def extract_items(response_body: Any) -> list[Any]:
    if isinstance(response_body, dict):
        data = response_body.get("data")
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            nested_data = data.get("data")
            if isinstance(nested_data, list):
                return nested_data
            return [data]
        if "items" in response_body and isinstance(response_body["items"], list):
            return response_body["items"]
    if isinstance(response_body, list):
        return response_body
    return []


def export_endpoint(
    endpoint: Endpoint,
    *,
    base_url: str,
    token: str,
    output_dir: Path,
    global_params: dict[str, str],
    limit: int,
    max_pages: int,
    pause_seconds: float,
) -> dict[str, Any]:
    pages: list[dict[str, Any]] = []
    items: list[Any] = []
    status = "ok"

    if endpoint.paginated:
        for page in range(1, max_pages + 1):
            params: dict[str, Any] = {"limit": limit, "page": page}
            params.update(global_params)
            params.update(dict(endpoint.params))
            response = request_json(base_url, endpoint.path, token, params)
            pages.append(response)

            if not response["ok"]:
                status = f"error_{response.get('status_code') or 'network'}"
                break

            page_items = extract_items(response.get("body"))
            items.extend(page_items)

            if len(page_items) < limit:
                break

            time.sleep(pause_seconds)
    else:
        params = dict(global_params)
        params.update(dict(endpoint.params))
        response = request_json(base_url, endpoint.path, token, params)
        pages.append(response)
        if not response["ok"]:
            status = f"error_{response.get('status_code') or 'network'}"
        else:
            items = extract_items(response.get("body"))

    payload = {
        "endpoint": asdict(endpoint),
        "status": status,
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "item_count": len(items),
        "items": items,
        "raw_pages": pages,
    }

    write_json(output_dir / f"{endpoint.key}.json", payload)

    return {
        "key": endpoint.key,
        "path": endpoint.path,
        "status": status,
        "item_count": len(items),
        "pii": endpoint.pii,
        "notes": endpoint.notes,
    }


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def write_summary(output_dir: Path, manifest: dict[str, Any]) -> None:
    rows = [
        "| Endpoint | Status | Itens | PII | Observação |",
        "| --- | --- | ---: | --- | --- |",
    ]
    for result in manifest["results"]:
        rows.append(
            "| {key} | {status} | {item_count} | {pii} | {notes} |".format(
                key=result["key"],
                status=result["status"],
                item_count=result["item_count"],
                pii="sim" if result["pii"] else "não",
                notes=result["notes"].replace("|", "\\|"),
            )
        )

    content = "\n".join(
        [
            f"# Export Nicochat - {manifest['tenant_slug']}",
            "",
            f"- Gerado em: `{manifest['exported_at']}`",
            f"- Base URL: `{manifest['base_url']}`",
            f"- Incluiu PII: `{'sim' if manifest['include_pii'] else 'não'}`",
            f"- Parâmetros globais: `{manifest['global_params']}`",
            "",
            "## Resultado por endpoint",
            "",
            *rows,
            "",
            "## Próximos passos",
            "",
            "1. Abrir os JSONs com status `ok`.",
            "2. Identificar `Main Flow`, `SDR Maju`, funções, tarefas e subfluxos técnicos.",
            "3. Preencher `docs/mapeamento-nicochat-tenda.md` com a matriz Nicochat -> SATI.",
            "4. Não commitar arquivos brutos deste diretório se houver dados de leads/conversas.",
            "",
        ]
    )
    (output_dir / "README.md").write_text(content, encoding="utf-8")


def get_endpoints(include_pii: bool, only: set[str] | None, user_ns_values: list[str]) -> list[Endpoint]:
    endpoints = list(SAFE_ENDPOINTS)
    if include_pii:
        endpoints.extend(PII_ENDPOINTS)
    for user_ns in user_ns_values:
        endpoints.append(
            Endpoint(
                key=f"flow_bot_user_conversation_{sanitize_filename(user_ns)}",
                path="/flow/bot-user-conversation",
                paginated=False,
                pii=True,
                notes=f"Histórico de conversa para user_ns={user_ns}.",
                params=(("user_ns", user_ns),),
            )
        )
    if only:
        endpoints = [endpoint for endpoint in endpoints if endpoint.key in only]
    return endpoints


def sanitize_filename(value: str) -> str:
    return "".join(char if char.isalnum() or char in ("-", "_") else "_" for char in value)[:80]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Exporta dados do Nicochat para mapear fluxos da Tenda RJ para a SATI."
    )
    parser.add_argument("--tenant-slug", default="tenda-rj", help="Slug usado na pasta de export.")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help="Base URL da API Nicochat.")
    parser.add_argument("--token-env", default="NICOCHAT_TOKEN", help="Nome da env var com o Bearer token.")
    parser.add_argument("--token", default=None, help="Bearer token. Prefira env var para não vazar em histórico.")
    parser.add_argument("--env-file", default=".env.nicochat", help="Arquivo local opcional com NICOCHAT_TOKEN=...")
    parser.add_argument("--output-dir", default="exports/nicochat", help="Diretório base de saída.")
    parser.add_argument("--limit", type=int, default=100, help="Itens por página.")
    parser.add_argument("--max-pages", type=int, default=100, help="Máximo de páginas por endpoint.")
    parser.add_argument("--pause-seconds", type=float, default=0.2, help="Pausa entre páginas.")
    parser.add_argument("--include-pii", action="store_true", help="Inclui contatos/conversas. Cuidado com LGPD.")
    parser.add_argument("--param", action="append", default=[], help="Parâmetro global KEY=VALUE para todos os GETs.")
    parser.add_argument("--user-ns", action="append", default=[], help="Exporta conversa de um user_ns específico.")
    parser.add_argument("--only", default="", help="Lista separada por vírgula de endpoint keys para exportar.")
    parser.add_argument("--dry-run", action="store_true", help="Mostra endpoints sem chamar a API.")
    args = parser.parse_args()

    load_env_file(Path(args.env_file))

    token = args.token or os.environ.get(args.token_env)
    if not token and not args.dry_run:
        print(
            f"Token não encontrado. Defina {args.token_env} ou crie {args.env_file} com {args.token_env}=...",
            file=sys.stderr,
        )
        return 2

    global_params = parse_key_values(args.param)
    only = {item.strip() for item in args.only.split(",") if item.strip()} or None
    endpoints = get_endpoints(args.include_pii, only, args.user_ns)

    if args.dry_run:
        for endpoint in endpoints:
            marker = "PII" if endpoint.pii else "safe"
            print(f"{endpoint.key:40} {marker:4} GET {endpoint.path}")
        return 0

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    output_dir = Path(args.output_dir) / args.tenant_slug / timestamp
    output_dir.mkdir(parents=True, exist_ok=True)

    results: list[dict[str, Any]] = []
    for endpoint in endpoints:
        print(f"Exportando {endpoint.key} ({endpoint.path})...")
        results.append(
            export_endpoint(
                endpoint,
                base_url=args.base_url,
                token=token or "",
                output_dir=output_dir,
                global_params=global_params,
                limit=args.limit,
                max_pages=args.max_pages,
                pause_seconds=args.pause_seconds,
            )
        )

    manifest = {
        "tenant_slug": args.tenant_slug,
        "base_url": args.base_url,
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "include_pii": args.include_pii,
        "global_params": global_params,
        "results": results,
    }
    write_json(output_dir / "manifest.json", manifest)
    write_summary(output_dir, manifest)

    print(f"\nExport finalizado: {output_dir}")
    print("Abra o README.md gerado para ver quais endpoints retornaram dados.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
