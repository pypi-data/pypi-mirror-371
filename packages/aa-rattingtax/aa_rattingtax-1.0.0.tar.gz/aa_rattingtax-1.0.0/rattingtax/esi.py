from typing import Iterable, Tuple, Optional
from esi.clients import EsiClientProvider
from decimal import Decimal
from datetime import datetime, timezone as dt_tz

# Try to get (data, response). If lib returns only data, fall back gracefully.
esi = EsiClientProvider()  # nie wymuszamy also_return_response – obsłużymy obie ścieżki
client = esi.client


def fetch_corp_public(corp_id: int) -> dict:
    """Fetch public corporation info."""
    return esi.client.Corporation.get_corporations_corporation_id(
        corporation_id=corp_id
    ).result()


def corp_logo_url(corp_id: int, size: int = 128) -> str:
    """Build CCP image server URL for corp logo."""
    return f"https://images.evetech.net/corporations/{corp_id}/logo?size={size}"


def _result_with_optional_response(op) -> Tuple[list, Optional[object]]:
    """
    Return (data, response) if the client supports it, otherwise (data, None).
    Works across different django-esi/bravado versions.
    """
    # 1) Spróbuj parametru with_response (niektóre wersje go wspierają)
    try:
        data, resp = op.result(with_response=True)  # type: ignore
        return data, resp
    except TypeError:
        # metoda nie przyjmuje with_response
        pass
    except ValueError:
        # zwróciła samą listę, ale próbowaliśmy rozpakować
        pass

    # 2) Spróbuj bez żadnych parametrów – może provider globalnie zwraca (data, response)
    try:
        out = op.result()
        if isinstance(out, tuple) and len(out) == 2:
            data, resp = out
            return data, resp
        # w przeciwnym wypadku to najpewniej sama lista
        return out, None
    except Exception:
        # przekaż dalej – wyższa warstwa złapie i potraktuje brak danych
        raise


def iter_corp_wallet_journal(token, corporation_id: int, division: int = 1) -> Iterable[dict]:
    """
    Iterate over corporation wallet journal entries for a given division.
    Tries to use X-Pages if available; otherwise probes pages until empty/404.
    """
    headers = {"Authorization": f"Bearer {token.valid_access_token()}"}

    # --- First page ---
    try:
        op = esi.client.Wallet.get_corporations_corporation_id_wallets_division_journal(
            corporation_id=corporation_id,
            division=division,
            page=1,
            _request_options={"headers": headers},
        )
        data, resp = _result_with_optional_response(op)
    except Exception:
        # brak uprawnień/pusty/dowolny błąd – traktujemy jak brak danych
        return

    if not data:
        return

    # Yield page 1
    for row in data:
        yield row

    # If we have X-Pages header, use it
    total_pages = None
    try:
        if resp is not None and hasattr(resp, "headers"):
            xpages = resp.headers.get("X-Pages")
            if xpages is not None:
                total_pages = int(xpages)
    except Exception:
        total_pages = None  # fallback poniżej

    # --- Remaining pages ---
    if total_pages and total_pages > 1:
        # Stricte po X-Pages
        for page in range(2, total_pages + 1):
            try:
                op = esi.client.Wallet.get_corporations_corporation_id_wallets_division_journal(
                    corporation_id=corporation_id,
                    division=division,
                    page=page,
                    _request_options={"headers": headers},
                )
                data, _ = _result_with_optional_response(op)
            except Exception:
                break
            if not data:
                break
            for row in data:
                yield row
    else:
        page = 2
        while True:
            try:
                op = esi.client.Wallet.get_corporations_corporation_id_wallets_division_journal(
                    corporation_id=corporation_id,
                    division=division,
                    page=page,
                    _request_options={"headers": headers},
                )
                data, _ = _result_with_optional_response(op)
            except Exception:
                break
            if not data:
                break
            for row in data:
                yield row
            page += 1


def sum_corp_bounty_tax_for_month(token, corporation_id: int, year: int, month: int):
    """
    Sum bounty_prizes amounts that actually landed in the corp wallet for
    the requested (year, month). Returns (total_decimal, seen_rows_count).
    """
    total = Decimal("0")
    seen = 0

    for row in iter_corp_wallet_journal(token, corporation_id, division=1):
        # row["date"] is ISO8601, e.g. "2025-08-19T13:37:00Z"
        try:
            dt = datetime.fromisoformat(row["date"].replace("Z", "+00:00")).astimezone(dt_tz.utc)
        except Exception:
            continue

        if dt.year != year or dt.month != month:
            continue

        if row.get("ref_type") == "bounty_prizes":
            amt = row.get("amount")
            if amt is not None:
                total += Decimal(str(amt))
                seen += 1

    return total, seen
