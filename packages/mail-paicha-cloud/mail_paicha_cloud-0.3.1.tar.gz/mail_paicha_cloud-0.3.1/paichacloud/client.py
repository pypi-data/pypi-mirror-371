# paichacloud.py
# -*- coding: utf-8 -*-
"""
Paicha Cloud Python client (domain auto-pick edition)

仕様:
  - 初期化時に domain 未指定がデフォルト。
  - 最初の change_mailbox は「ドメイン一覧を得るためだけ」に叩き、
    その new_email は捨てる（メールボックスは確保しない）。
  - 得られた domain 一覧からランダムに 1 つ選び、改めて change_mailbox を叩いて
    本命の new_email を取得。
  - ドメイン一覧の取得・整形表示・CLI も用意。

依存: requests
"""

from __future__ import annotations

import json
import random
import time
import urllib.parse
from dataclasses import dataclass
from typing import Any, Callable, Dict, Iterable, List, Optional

import requests


__all__ = [
    "PaichaCloudClient",
    "PaichaCloudError",
    "MailboxChange",
]
__version__ = "0.2.0"

MAIL_BASE = "https://mail.paicha.cloud"
MAIL_CHANGE = f"{MAIL_BASE}/change_mailbox"
API_BASE = "https://mail.paicha.cloud/api"

# ドメイン一覧を得るための「プローブ用ドメイン」。
# サーバ仕様上 change_mailbox は domain パラメータが必要なため、
# 例として paicharm.tokyo を使うが、この呼び出しで返る new_email は破棄する。
DEFAULT_PROBE_DOMAIN = "paicharm.tokyo"


class PaichaCloudError(Exception):
    """Client-level exception for Paicha Cloud operations."""


@dataclass
class MailboxChange:
    new_email: str
    domains: List[str]


class PaichaCloudClient:
    """
    Minimal yet comfy client for paicha.cloud mail endpoints.

    Parameters
    ----------
    domain : Optional[str]
        指定しなければ、まず「ドメイン一覧の取得のみ」を行い、その後ランダム選択した
        ドメインで本命の new_email を作成する。指定した場合はそのドメインで直に new_email を作成。
    email : Optional[str]
        既存のメールアドレスを直接使う場合に指定（change_mailbox をスキップ）。
    session : Optional[requests.Session]
        使い回しの Session（省略時は内部で作成）。
    timeout : float
        HTTP タイムアウト（秒）。デフォルト 30。
    allow_redirects : bool
        初回アクセス時のリダイレクト許可。
    rng : Optional[random.Random]
        乱数生成器を差し替えたい場合（テスト等）。省略時は random モジュールを使用。
    probe_domain : str
        ドメイン一覧を得るためのプローブ用ドメイン。デフォルトは "paicharm.tokyo"。
    """

    def __init__(
        self,
        domain: Optional[str] = None,
        *,
        email: Optional[str] = None,
        session: Optional[requests.Session] = None,
        timeout: float = 30.0,
        allow_redirects: bool = True,
        rng: Optional[random.Random] = None,
        probe_domain: str = DEFAULT_PROBE_DOMAIN,
    ) -> None:
        self.s = session or requests.Session()
        self.timeout = timeout
        self.allow_redirects = allow_redirects
        self.email: Optional[str] = None
        self.domains: List[str] = []
        self._rng = rng or random.Random()
        self._probe_domain = probe_domain

        # 初回アクセスでクッキー等を整える
        self._prime()

        if email:
            # 既存メールを使う場合は即セット
            self.email = email
            # ドメイン一覧が必要なら明示的に fetch_domains() を呼んでね
            return

        if domain:
            # ドメイン明示: そのドメインで直接 new_email を作る
            self._apply_change(self._change_mailbox_raw(domain))
        else:
            # デフォルト: まずは「一覧だけ」取りに行く（new_email は捨てる）
            domains = self.fetch_domains()
            if not domains:
                raise PaichaCloudError("Failed to obtain domain list (empty).")
            chosen = self._rng.choice(domains)
            # 本命のメールアドレス発行
            self._apply_change(self._change_mailbox_raw(chosen))

    # -----------------------------
    # Core HTTP helpers
    # -----------------------------
    def _prime(self) -> None:
        try:
            self.s.get(MAIL_BASE, allow_redirects=self.allow_redirects, timeout=self.timeout)
        except requests.RequestException as e:
            raise PaichaCloudError(f"Failed to reach {MAIL_BASE}: {e}") from e

    def _post_json(self, url: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        try:
            r = self.s.post(url, json=payload, timeout=self.timeout)
            r.raise_for_status()
            return r.json()
        except (requests.RequestException, json.JSONDecodeError) as e:
            raise PaichaCloudError(f"POST {url} failed: {e}") from e

    def _get_json(self, url: str) -> Any:
        try:
            r = self.s.get(url, timeout=self.timeout)
            r.raise_for_status()
            return r.json()
        except (requests.RequestException, json.JSONDecodeError) as e:
            raise PaichaCloudError(f"GET {url} failed: {e}") from e

    # -----------------------------
    # Mailbox / Domains
    # -----------------------------
    def _change_mailbox_raw(self, domain: str) -> MailboxChange:
        data = self._post_json(MAIL_CHANGE, {"domain": domain})
        new_email = data.get("new_email")
        domains = data.get("domains") or []
        if not new_email:
            raise PaichaCloudError("No 'new_email' returned from change_mailbox.")
        return MailboxChange(new_email=new_email, domains=list(domains))

    def _apply_change(self, result: MailboxChange) -> None:
        self.email = result.new_email
        self.domains = result.domains

    def fetch_domains(self) -> List[str]:
        """
        ドメイン一覧だけ取得する（この時の new_email は破棄する）。
        Returns
        -------
        List[str]
        """
        probe = self._change_mailbox_raw(self._probe_domain)
        self.domains = probe.domains[:]  # キャッシュ更新
        return self.domains[:]

    def list_domains(self) -> List[str]:
        """
        取得済みのドメイン一覧（キャッシュ）を返す。
        最新を取りたい場合は fetch_domains() を呼ぶ。
        """
        return list(self.domains)

    def format_domains(self, columns: int = 2, padding: int = 2) -> str:
        """
        ドメイン一覧を整形文字列で返す（簡易表示用）。
        """
        if not self.domains:
            return "(no domains cached)"
        colw = max(len(d) for d in self.domains) + padding
        chunks = []
        for i, d in enumerate(self.domains, 1):
            chunks.append(d.ljust(colw))
            if i % columns == 0:
                chunks.append("\n")
        s = "".join(chunks).rstrip()
        return s

    def change_mailbox(self, domain: str) -> MailboxChange:
        """
        明示的にドメインを指定して new_email を作る。
        成功したら self.email / self.domains を更新。
        """
        result = self._change_mailbox_raw(domain)
        self._apply_change(result)
        return result

    # -----------------------------
    # Mail retrieval
    # -----------------------------
    def inbox(self) -> List[Dict[str, Any]]:
        """
        現在のメールアドレスの受信一覧（サマリー）を返す。
        """
        if not self.email:
            raise PaichaCloudError("Email address is not set. Initialize or set email=.")
        quoted = urllib.parse.quote(self.email, safe="")
        url = f"{API_BASE}/{quoted}"
        data = self._get_json(url)
        if isinstance(data, dict):
            return [data]
        return data or []

    def get_mail(self, mail_id: str) -> Dict[str, Any]:
        """
        個別メールの詳細 JSON を返す。
        """
        if not self.email:
            raise PaichaCloudError("Email address is not set. Initialize or set email=.")
        quoted_email = urllib.parse.quote(self.email, safe="")
        quoted_id = urllib.parse.quote(str(mail_id), safe="")
        url = f"{API_BASE}/mailbox/{quoted_email}/mail/{quoted_id}"
        return self._get_json(url)

    # -----------------------------
    # Convenience filters & waiting
    # -----------------------------
    @staticmethod
    def _contains(hay: Optional[str], needle: Optional[str]) -> bool:
        if hay is None or needle is None:
            return False
        return needle.lower() in hay.lower()

    def filter_inbox(
        self,
        inbox_items: Iterable[Dict[str, Any]],
        *,
        subject_contains: Optional[str] = None,
        sender_contains: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        results: List[Dict[str, Any]] = []
        for item in inbox_items:
            subject = item.get("subject") or item.get("Subject") or item.get("title")
            sender = (
                item.get("from")
                or item.get("sender")
                or item.get("From")
                or item.get("Sender")
            )
            ok = True
            if subject_contains:
                ok = ok and self._contains(subject, subject_contains)
            if sender_contains:
                ok = ok and self._contains(sender, sender_contains)
            if ok:
                results.append(item)
        return results

    def wait_for(
        self,
        *,
        subject_contains: Optional[str] = None,
        sender_contains: Optional[str] = None,
        timeout: float = 60.0,
        interval: float = 2.0,
        return_detail: bool = True,
    ) -> Optional[Dict[str, Any]]:
        """
        条件に合うメールが来るまでポーリング。
        """
        deadline = time.monotonic() + max(0.0, timeout)
        while True:
            items = self.inbox()
            filtered = self.filter_inbox(
                items,
                subject_contains=subject_contains,
                sender_contains=sender_contains,
            )
            if filtered:
                first = filtered[0]
                if return_detail and "id" in first:
                    try:
                        return self.get_mail(first["id"])
                    except PaichaCloudError:
                        return first
                return first

            if time.monotonic() >= deadline or timeout <= 0:
                return None

            time.sleep(max(0.1, interval))

    # -----------------------------
    # Context manager & cleanup
    # -----------------------------
    def close(self) -> None:
        try:
            self.s.close()
        except Exception:
            pass

    def __enter__(self) -> "PaichaCloudClient":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()


# -----------------------------
# Simple CLI (optional)
# -----------------------------
def _cli() -> None:
    import argparse
    parser = argparse.ArgumentParser(description="Paicha Cloud mail client")
    parser.add_argument("--domain", type=str, default=None, help="指定すればそのドメインで即 new_email 作成")
    parser.add_argument("--email", type=str, default=None, help="既存 email を直指定（API呼び出しをスキップ）")
    parser.add_argument("--probe-domain", type=str, default=DEFAULT_PROBE_DOMAIN, help="ドメイン一覧の取得に使うプローブ用ドメイン")
    parser.add_argument("--seed", type=int, default=None, help="ランダム選択のシード（テスト/再現用）")
    parser.add_argument("--list-domains", action="store_true", help="ドメイン一覧を表示して終了（最新取得）")
    parser.add_argument("--print-inbox", action="store_true", help="受信一覧（JSON）を表示")
    parser.add_argument("--subject-contains", type=str, default=None, help="件名フィルタ")
    parser.add_argument("--sender-contains", type=str, default=None, help="送信者フィルタ")
    parser.add_argument("--wait", action="store_true", help="条件に合う新着を待機")
    parser.add_argument("--timeout", type=float, default=60.0, help="待機タイムアウト秒")
    parser.add_argument("--interval", type=float, default=2.0, help="ポーリング間隔秒")
    args = parser.parse_args()

    rng = random.Random(args.seed) if args.seed is not None else None

    if args.email and args.domain:
        raise SystemExit("--email と --domain は同時指定できません（挙動が競合します）")

    client = PaichaCloudClient(
        domain=args.domain,
        email=args.email,
        rng=rng,
        probe_domain=args.probe_domain,
    )

    # --list-domains が指定されたら最新取得して表示して終了
    if args.list_domains:
        doms = client.fetch_domains()
        print("[domains] (latest)")
        print(client.format_domains())
        client.close()
        return

    print(f"[email] {client.email}")
    print("[domains] (cached)")
    print(client.format_domains())

    if args.print_inbox:
        data = client.inbox()
        print(json.dumps(data, ensure_ascii=False, indent=2))

    if args.subject_contains or args.sender_contains:
        items = client.filter_inbox(
            client.inbox(),
            subject_contains=args.subject_contains,
            sender_contains=args.sender_contains,
        )
        print("[filtered inbox]")
        print(json.dumps(items, ensure_ascii=False, indent=2))

    if args.wait:
        msg = client.wait_for(
            subject_contains=args.subject_contains,
            sender_contains=args.sender_contains,
            timeout=args.timeout,
            interval=args.interval,
            return_detail=True,
        )
        print("[wait result]")
        print(json.dumps(msg, ensure_ascii=False, indent=2))

    client.close()


if __name__ == "__main__":
    _cli()
