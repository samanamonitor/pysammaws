from .query import AwsQuery

class AwsWorkspacesQuery(AwsQuery):
	_service_queries = {
		"describe_workspaces": "Workspaces",
		"describe_workspaces_connection_status": "WorkspacesConnectionStatus",
		"describe_workspace_directories": "Directories"
	}
	_service_name = "workspaces"
