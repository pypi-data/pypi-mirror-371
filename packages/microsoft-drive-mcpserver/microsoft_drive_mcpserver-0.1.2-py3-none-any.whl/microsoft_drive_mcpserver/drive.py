import httpx
import mimetypes
import os
import time
from typing import Any, Dict, List


class AsyncMicrosoftOneDrive:
    def __init__(self, client_id: str, client_secret: str, access_token: str, refresh_token: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.token_expires_at = time.time() + 3500

    # ---------------- Token 刷新 ----------------
    async def _refresh_token(self):
        url = "https://login.microsoftonline.com/common/oauth2/v2.0/token"
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "refresh_token": self.refresh_token,
            "grant_type": "refresh_token",
        }
        async with httpx.AsyncClient() as client:
            r = await client.post(url, data=data)
        if not r.status_code == 200:
            raise Exception(f"refresh token failed: {r.status_code} {r.text}")
        token_data = r.json()
        self.access_token = token_data["access_token"]
        self.refresh_token = token_data.get("refresh_token", self.refresh_token)
        self.token_expires_at = time.time() + token_data.get("expires_in", 3600) - 10

    # ---------------- 通用请求 ----------------
    async def request(
            self, method: str,
            endpoint: str = None,
            next_link: str = None,
            **kwargs) -> Any:
        if time.time() > self.token_expires_at:
            await self._refresh_token()

        headers = kwargs.pop("headers", {})
        headers["Authorization"] = f"Bearer {self.access_token}"
        headers.setdefault("Content-Type", "application/json")

        if next_link:
            url = next_link
        else:
            url = f"https://graph.microsoft.com/v1.0/me{endpoint}"

        async with httpx.AsyncClient() as client:
            r = await client.request(method, url, headers=headers, **kwargs)
            if r.status_code == 401:
                await self._refresh_token()
                headers["Authorization"] = f"Bearer {self.access_token}"
                r = await client.request(method, url, headers=headers, **kwargs)

        if not r.is_success:
            raise Exception(f"API 错误 {r.status_code}: {r.text}")

        if r.content:
            try:
                return r.json()
            except:
                return r.content
        return None

    # ---------------- File 操作 ----------------

    async def file_search(self, q: str, next_link: str = None) -> Dict:
        if next_link:
            return await self.request("GET", next_link=next_link)
        items = await self.request("GET", endpoint=f"/drive/root/search(q='{q}')")
        return items

    async def file_delete(self, item_id: str):
        res = await self.request("DELETE", f"/drive/items/{item_id}")
        return res

    async def file_rename(self, item_id: str, new_name: str):
        return await self.request("PATCH", f"/drive/items/{item_id}", json={"name": new_name})

    async def file_share(
            self, item_id: str, type_: str, password: str = None,
            expirationDateTime: str = None, retainInheritedPermissions=None, scope: str = None
    ) -> Dict:
        body = {
            "type": type_, "scope": scope, "password": password,
            "expirationDateTime": expirationDateTime, "retainInheritedPermissions": retainInheritedPermissions
        }
        body = {k: v for k, v in body.items() if v is not None}
        return await self.request("POST", f"/drive/items/{item_id}/createLink", json=body)

    async def preview_item(
            self, item_id: str, page = None, zoom = None
    ) -> Dict:
        body = {
            "page": page, "zoom": zoom
        }
        body = {k: v for k, v in body.items() if v is not None}
        return await self.request("POST", f"/drive/items/{item_id}/preview", json=body)

    async def list_children(self, item_id: str, next_link: str = None):
        if next_link:
            return await self.request("GET", next_link=next_link)
        return await self.request("GET", f"/drive/items/{item_id}/children")

    async def get_file_content(self, item_id: str):
        info = await self.request("GET", f"/drive/items/{item_id}")
        download_url = info.get("@microsoft.graph.downloadUrl")
        if not download_url:
            return info

        async with httpx.AsyncClient() as client:
            r = await client.get(download_url)
        if not r.status_code == 200:
            return info
        try:
            info['content'] = r.content.decode("utf-8", errors="ignore")
        except:
            return info
        return info

    # ---------------- Folder 操作 ----------------
    async def folder_create(self, name: str, parent_item_id: str = None):
        endpoint = "/drive/root/children" if not parent_item_id else f"/drive/items/{parent_item_id}/children"
        body = {"name": name, "folder": {}}
        return await self.request("POST", endpoint, json=body)


