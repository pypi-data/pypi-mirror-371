from typing import Optional, Annotated, Literal, Union
from pydantic import Field
import os
from mcp.server.fastmcp import FastMCP
from microsoft_drive_mcpserver.drive import AsyncMicrosoftOneDrive

MS_CLIENT_ID = os.environ.get("MS_CLIENT_ID")
if not MS_CLIENT_ID:
    raise ValueError("MS_CLIENT_ID environment variable is required.")
MS_CLIENT_SECRET = os.environ.get("MS_CLIENT_SECRET")
if not MS_CLIENT_SECRET:
    raise ValueError("MS_CLIENT_SECRET environment variable is required.")
MS_ACCESS_TOKEN = os.environ.get("MS_ACCESS_TOKEN")
if not MS_ACCESS_TOKEN:
    raise ValueError("MS_ACCESS_TOKEN environment variable is required.")
MS_REFRESH_TOKEN = os.environ.get("MS_REFRESH_TOKEN")
if not MS_REFRESH_TOKEN:
    raise ValueError("MS_REFRESH_TOKEN environment variable is required.")

onedrive = AsyncMicrosoftOneDrive(
    client_id=MS_CLIENT_ID,
    client_secret=MS_CLIENT_SECRET,
    access_token=MS_ACCESS_TOKEN,
    refresh_token=MS_REFRESH_TOKEN
)

mcp = FastMCP("OneDrive-MCP")


@mcp.tool(description="Search files in Microsoft OneDrive.")
async def search_file(
        q: Annotated[str, Field(description="The query text used to search for items.")],
        next_link: Annotated[Optional[str], Field(description="Next page link for pagination.")] = None,
) -> dict:
    try:
        return await onedrive.file_search(q=q, next_link=next_link)
    except Exception as e:
        return {"status": "error", "message": str(e)}


@mcp.tool(description="Delete a file or a folder in Microsoft OneDrive.")
async def delete_file(item_id: Annotated[str, Field(description="The ID of the file to delete.")]):
    try:
        return await onedrive.file_delete(item_id=item_id)
    except Exception as e:
        return {"status": "error", "message": str(e)}


# rename file
@mcp.tool(description="Rename a file or a folder in Microsoft OneDrive.")
async def file_rename(
        item_id: Annotated[str, Field(description="The ID of the file to rename.")],
        new_name: Annotated[str, Field(description="The new name for the file.")],
):
    try:
        return await onedrive.file_rename(item_id=item_id, new_name=new_name)
    except Exception as e:
        return {"status": "error", "message": str(e)}


# create share link
@mcp.tool(description="Create a share link for drive item in Microsoft OneDrive.")
async def create_share_link(
        item_id: Annotated[str, Field(description="The ID of the file to share.")],
        type_: Annotated[Literal["view", "edit", "embed"], Field(description="The type of sharing link to create.")],
        password: Annotated[Optional[str], Field(
            description="The password of the sharing link that is set by the creator. Optional and OneDrive Personal only.")] = None,
        expirationDateTime: Annotated[Optional[str], Field(
            description="TA String with format of yyyy-MM-ddTHH:mm:ssZ of DateTime indicates the expiration time of the permission.")] = None,
        retainInheritedPermissions: Annotated[Optional[bool], Field(
            description="Optional. If true (default), any existing inherited permissions are retained on the shared item when sharing this item for the first time. If false, all existing permissions are removed when sharing for the first time.")] = None,
        scope: Annotated[Optional[Literal["anonymous", "organization", "users"]], Field(
            description="The scope of link to create.")] = None
) -> dict:
    try:
        return await onedrive.file_share(
            item_id=item_id, type_=type_, password=password, expirationDateTime=expirationDateTime,
            retainInheritedPermissions=retainInheritedPermissions, scope=scope
        )
    except Exception as e:
        return {"status": "error", "message": str(e)}


@mcp.tool(description="Get a short-lived embeddable preview link for a file in Microsoft OneDrive.")
async def preview_item(
        item_id: Annotated[str, Field(description="The ID of the file to preview.")],
        page: Annotated[Optional[Union[str, int]], Field(description="Page number of document to start at, if applicable. Specified as string for future use cases around file types such as ZIP.")] = None,
        zoom: Annotated[Optional[int], Field(description=" Zoom level to start at, if applicable.")] = None
) -> dict:
    try:
        return await onedrive.preview_item(item_id=item_id, page=page, zoom=zoom)
    except Exception as e:
        return {"status": "error", "message": str(e)}


# list children of a folder
@mcp.tool(description="List children of a drive item in Microsoft OneDrive.")
async def list_children(
        item_id: Annotated[str, Field(description="The ID of the item to list children for.")],
        next_link: Annotated[Optional[str], Field(description="Next page link for pagination.")] = None
) -> dict:
    try:
        return await onedrive.list_children(item_id=item_id, next_link=next_link)
    except Exception as e:
        return {"status": "error", "message": str(e)}


# download file content
@mcp.tool(description="Download content of a file in Microsoft OneDrive.")
async def get_file_content(
        item_id: Annotated[str, Field(description="The ID of the file to download content for.")]
) -> dict:
    try:
        return await onedrive.get_file_content(item_id=item_id)
    except Exception as e:
        return {"status": "error", "message": str(e)}


# folder_create
@mcp.tool(description="Create a folder in Microsoft OneDrive.")
async def folder_create(
        name: Annotated[str, Field(description="The name of the folder to create.")],
        parent_item_id: Annotated[Optional[str], Field(description="The ID of the parent folder. If not provided, the folder will be created in the root directory.")] = None
) -> dict:
    try:
        return await onedrive.folder_create(name=name, parent_item_id=parent_item_id)
    except Exception as e:
        return {"status": "error", "message": str(e)}



def main():
    mcp.run()


if __name__ == '__main__':
    main()
