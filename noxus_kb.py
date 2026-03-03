import requests
import pandas as pd
from io import BytesIO
from config import BASE_URL, API_KEY, KB_ID
import json

def base_name_from_input(text: str) -> str:
    return text.split(" - ")[0].strip()


def kb_list_documents(status: str = "trained") -> list[dict]:
    items = []
    page = 1
    page_size = 100

    while True:
        url = f"{BASE_URL.rstrip('/')}/v1/knowledge-bases/{KB_ID}/documents/{status}"
        resp = requests.get(
            url,
            headers={"X-API-KEY": API_KEY},
            params={"page": page, "size": page_size},
            timeout=30,
            verify=False,
        )
        resp.raise_for_status()
        data = resp.json()
        items.extend(data.get("items", []))

        pages = data.get("pages") or 1
        if page >= pages:
            break
        page += 1

    return items


def kb_download_document(doc: dict) -> bytes:
    file_id = doc.get("file_id") or doc.get("fileId")
    if not file_id:
        raise Exception("Documento não tem file_id.")

    base = BASE_URL.rstrip("/")
    candidates = [
        f"{base}/v1/files/{file_id}/download",
        f"{base}/v1/files/{file_id}",
        f"{base}/v1/file/{file_id}/download",
        f"{base}/v1/file/{file_id}",
        f"{base}/v1/storage/files/{file_id}/download",
        f"{base}/v1/storage/files/{file_id}",
    ]

    for url in candidates:
        resp = requests.get(url, headers={"X-API-KEY": API_KEY}, verify=False, timeout=60)
        if resp.status_code == 200:
            ctype = (resp.headers.get("Content-Type") or "").lower()
            # ✅ se NÃO for JSON, já devolve bytes direto (csv/xlsx/png/html etc.)
            if "application/json" not in ctype:
                return resp.content

            body = resp.content or b""
            body_stripped = body.lstrip()

            # ✅ Se o header diz JSON mas o corpo não parece JSON, devolve bytes mesmo assim
            if not (body_stripped.startswith(b"{") or body_stripped.startswith(b"[")):
                return body

            j = resp.json()

            signed = j.get("url") or j.get("downloadUrl") or j.get("download_url") or j.get("signed_url")
            if signed:
                r2 = requests.get(signed, verify=False, timeout=60)
                r2.raise_for_status()
                return r2.content

            # ✅ JSON inline (seu caso do upload_train)
            if all(k in j for k in ("location", "year", "data")):
                import json
                return json.dumps(j, ensure_ascii=False).encode("utf-8")

            raise Exception(f"200 JSON mas sem url e sem conteúdo inline. keys={list(j.keys())}")

    raise Exception("Não consegui baixar o arquivo em nenhuma rota.")


def _bytes_to_df(file_bytes: bytes) -> pd.DataFrame:
    # 1) tenta JSON primeiro (se for)
    b = file_bytes.lstrip()
    if b.startswith(b"{") or b.startswith(b"["):
        try:
            obj = json.loads(file_bytes.decode("utf-8", errors="replace"))

            # formato do teu agente: {"location","year","data":[...]}
            if isinstance(obj, dict) and isinstance(obj.get("data"), list):
                df = pd.DataFrame(obj["data"])
                # normaliza nomes de coluna pro Analysis.py
                if "month" in df.columns and "Month" not in df.columns:
                    df = df.rename(columns={"month": "Month"})
                if "year" in df.columns and "Year" not in df.columns:
                    df = df.rename(columns={"year": "Year"})
                df["Year"] = obj.get("year")
                df["Location"] = obj.get("location")
                return df

            # fallback: lista de dicts
            if isinstance(obj, list):
                return pd.DataFrame(obj)

            # fallback geral
            return pd.json_normalize(obj)

        except Exception:
            pass  # cai para excel/csv

    # 2) excel/csv como antes
    try:
        return pd.read_excel(BytesIO(file_bytes))
    except Exception:
        return pd.read_csv(BytesIO(file_bytes))


def load_df_by_base_name(input_text: str) -> tuple[pd.DataFrame, str]:
    target = base_name_from_input(input_text)
    docs = kb_list_documents(status="trained")
    match = next((d for d in docs if (d.get("name") or "").strip() == target), None)
    if not match:
        raise Exception(f"Não encontrei documento com nome: {target}")

    file_bytes = kb_download_document(match)
    df = _bytes_to_df(file_bytes)
    return df, target


def load_df_by_exact_name(doc_name: str) -> tuple[pd.DataFrame | None, str | None]:
    docs = kb_list_documents(status="trained")
    names = [(d.get("name") or "").strip() for d in docs]

    wanted = doc_name.strip()

    # gera candidatos prováveis (mantém compat com antigos + novos)
    candidates = [
        wanted,
        f"{wanted}.json",
        wanted.replace(", ", "_ "),
        wanted.replace(",", "_"),
        wanted.replace(", ", "__"),
        wanted.replace(",", "__"),
        wanted.replace("  ", " "),
    ]

    match = None
    for c in candidates:
        match = next((d for d in docs if (d.get("name") or "").strip() == c), None)
        if match:
            wanted = c
            break

    if not match:
        return None, None

    file_bytes = kb_download_document(match)
    df = _bytes_to_df(file_bytes)
    return df, wanted