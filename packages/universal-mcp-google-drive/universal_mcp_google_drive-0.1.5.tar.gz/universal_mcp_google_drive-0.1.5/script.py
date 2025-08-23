from universal_mcp.integrations import AgentRIntegration
from universal_mcp.utils.agentr import AgentrClient
from universal_mcp.tools import ToolManager
from universal_mcp_google_drive.app import GoogleDriveApp
import anyio
from pprint import pprint

integration = AgentRIntegration(name="google-drive", api_key="sk_416e4f88-3beb-4a79-a0ef-fb1d2c095aee", base_url="https://api.agentr.dev")
app_instance = GoogleDriveApp(integration=integration)
tool_manager = ToolManager()
tool_manager.add_tool(app_instance.move_files)


async def main():
    # Get a specific tool by name
    tool = tool_manager.get_tool("move_files")

    if tool:
        pprint(f"Tool Name: {tool.name}")
        pprint(f"Tool Description: {tool.description}")
        pprint(f"Arguments Description: {tool.args_description}")
        pprint(f"Returns Description: {tool.returns_description}")
        pprint(f"Raises Description: {tool.raises_description}")
        pprint(f"Tags: {tool.tags}")
        pprint(f"Parameters Schema: {tool.parameters}")
        
        # You can also get the JSON schema for parameters
    
    # Get all tools
    all_tools = tool_manager.get_tools_by_app()
    print(f"\nTotal tools registered: {len(all_tools)}")
    
    # List tools in different formats
    mcp_tools = tool_manager.list_tools()
    print(f"MCP format tools: {len(mcp_tools)}")
    
    # Execute the tool
    # result = await tool_manager.call_tool(name="list_messages", arguments={"max_results": 2})
    # result = await tool_manager.call_tool(name="get_message", arguments={"message_id": "1985f5a3d2a6c3c8"})
    # result = await tool_manager.call_tool(
    #     name="send_email",
    #     arguments={
    #         "to": "rishabh@agentr.dev",
    #         "subject": " Email",
    #         "body": "<html><body><h1>Hello!</h1><p>This is a <b>test email</b> sent from the script.</p></body></html>",
    #         "body_type": "html"
    #     }
    # )
    # result = await tool_manager.call_tool(name="create_draft", arguments={"to": "rishabh@agentr.dev", "subject": " Draft Email", "body": " test email"})
    # result = await tool_manager.call_tool(name="send_draft", arguments={"draft_id": "r354126479467734631"})
    # result = await tool_manager.call_tool(name="get_draft", arguments={"draft_id": "r5764319286899776116"})
    # result = await tool_manager.call_tool(name="get_profile",arguments={})
    # result = await tool_manager.call_tool(name="list_drafts", arguments={"max_results": 2})
    # result = await tool_manager.call_tool(name="list_labels",arguments={})
    # result = await tool_manager.call_tool(name="create_label",arguments={"name": "test_label"})
    # Example: Send new email
    # result = await tool_manager.call_tool(name="send_email", arguments={"to": "rishabh@agentr.dev", "subject": "Meeting Tomorrow", "body": "Let's meet at 2pm"})
    # result = await tool_manager.call_tool(name="list_messages", arguments={"max_results": 2})
    result=await tool_manager.call_tool(name="move_files",arguments={"file_id":"1fCRt5kVCeHp8dnd3EkI3GTDLCnsgJfJ-oRZn5A5KfLw","add_parents":"1RMqezmw5cCXwLFEeUbqw8PiZPuTCCnim","remove_parents":"1hwlO-RjPccgKPcZ1v7-hSRwiNy-XAwhG"})
    # Example: Reply to thread (using thread_id)
    # result = await tool_manager.call_tool(name="send_email", arguments={"to": "rishabh@agentr.dev", "subject": "Meeting Tomorrow", "body": "I will attend the meeting"})
    print(result)
    print(type(result))

if __name__ == "__main__":
    anyio.run(main)