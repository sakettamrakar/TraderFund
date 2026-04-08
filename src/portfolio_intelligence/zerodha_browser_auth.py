from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Optional
from urllib.parse import parse_qs, urlparse

import pyotp
from dotenv import find_dotenv, set_key
from kiteconnect import KiteConnect
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright


def login_url(api_key: str) -> str:
    return f"https://kite.zerodha.com/connect/login?v=3&api_key={api_key}"


def capture_request_token(
    api_key: str,
    *,
    headless: bool = False,
    timeout_seconds: int = 300,
) -> str:
    user_id = os.getenv("KITE_USER_ID", "").strip()
    password = os.getenv("KITE_PASSWORD", "").strip()
    pin = os.getenv("KITE_PIN", "").strip()
    totp_secret = os.getenv("KITE_TOTP_SECRET", "").strip()

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=headless)
        context = browser.new_context()
        page = context.new_page()
        token_state = {"request_token": ""}
        _attach_request_token_watchers(page, token_state)
        page.goto(login_url(api_key), wait_until="domcontentloaded")

        if user_id and password:
            _attempt_login(page, user_id=user_id, password=password, pin=pin, totp_secret=totp_secret)
        elif headless:
            browser.close()
            raise RuntimeError(
                "Headless Zerodha auth requires KITE_USER_ID and KITE_PASSWORD in the environment."
            )
        else:
            print("Complete Zerodha login in the opened browser window. Waiting for redirect with request_token...")

        request_token = _wait_for_request_token(page, token_state=token_state, timeout_seconds=timeout_seconds)
        browser.close()
        return request_token


def exchange_access_token(api_key: str, api_secret: str, request_token: str) -> str:
    kite = KiteConnect(api_key=api_key)
    session = kite.generate_session(request_token, api_secret=api_secret)
    token = session.get("access_token", "")
    if not token:
        raise RuntimeError("Zerodha session exchange did not return an access token.")
    return token


def persist_access_token(access_token: str, *, env_path: Optional[Path] = None) -> None:
    target = env_path or Path(find_dotenv(usecwd=True) or ".env")
    if not target.exists():
        target.touch()
    set_key(str(target), "KITE_ACCESS_TOKEN", access_token)


def obtain_access_token_via_browser(
    api_key: str,
    api_secret: str,
    *,
    headless: bool = False,
    timeout_seconds: int = 300,
    persist_env: bool = True,
) -> str:
    request_token = capture_request_token(api_key, headless=headless, timeout_seconds=timeout_seconds)
    access_token = exchange_access_token(api_key, api_secret, request_token)
    if persist_env:
        persist_access_token(access_token)
    return access_token


def _attempt_login(page, *, user_id: str, password: str, pin: str, totp_secret: str) -> None:
    try:
        page.locator("input[type='text']").first.fill(user_id)
        page.locator("input[type='password']").first.fill(password)
        page.get_by_role("button", name="Login").click()
        time.sleep(1)

        otp_value = ""
        if totp_secret:
            otp_value = pyotp.TOTP(totp_secret).now()
        elif pin:
            otp_value = pin

        if otp_value:
            otp_input = page.locator("input[type='password'], input[inputmode='numeric']").last
            otp_input.fill(otp_value)
            continue_button = page.get_by_role("button", name="Continue")
            if continue_button.count():
                continue_button.click()
    except Exception:
        # Fall back to manual completion if the login page markup differs.
        print("Automatic field fill did not complete cleanly. Finish auth in the browser window.")


def _wait_for_request_token(page, *, token_state: dict[str, str], timeout_seconds: int) -> str:
    deadline = time.time() + timeout_seconds
    try:
        page.wait_for_url("**request_token=**", timeout=timeout_seconds * 1000)
    except PlaywrightTimeoutError:
        pass
    except Exception:
        pass

    while time.time() < deadline:
        if token_state.get("request_token"):
            return token_state["request_token"]
        url = page.url
        token = _extract_request_token_from_url(url)
        if token:
            return token
        time.sleep(1)
    raise TimeoutError("Timed out waiting for Zerodha redirect with request_token.")


def _extract_request_token_from_url(url: str) -> str:
    if "request_token=" not in url:
        return ""
    parsed = urlparse(url)
    values = parse_qs(parsed.query).get("request_token")
    return values[0] if values else ""


def _attach_request_token_watchers(page, token_state: dict[str, str]) -> None:
    def capture_from_url(url: str) -> None:
        token = _extract_request_token_from_url(url)
        if token and not token_state.get("request_token"):
            token_state["request_token"] = token

    page.on("framenavigated", lambda frame: capture_from_url(frame.url))
    page.on("request", lambda request: capture_from_url(request.url))
    page.on("response", lambda response: capture_from_url(response.url))
    page.on("requestfailed", lambda request: capture_from_url(request.url))