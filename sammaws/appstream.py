from .query import AwsQuery
import logging

log = logging.getLogger(__name__)

class AwsAppstreamQuery(AwsQuery):
	_service_queries = {
		"describe_stacks": "Stacks",
		"describe_fleets": "Fleets",
		"describe_sessions": "Sessions",
		"describe_directory_configs": "DirectoryConfigs",
		"describe_applications": "Applications",
		"list_associated_fleets": "Names"
	}
	_service_name = "appstream"

class AwsAppstreamStackFleet:
	def __init__(self, **kwargs):
		self.q = AwsAppstreamQuery("describe_stacks", **kwargs)
		self.client = self.q.client

	def __iter__(self):
		self.iter = iter(self.q)
		return self

	def __next__(self):
		while True:
			stack = next(self.iter)
			q = AwsAppstreamQuery("list_associated_fleets", client=self.client, StackName=stack['Name'])
			try:
				fleet = next(iter(q))
			except StopIteration:
				log.debug("AwsAppstreamStackFleet: no fleets in stack %s", stack['Name'])
				continue
			out = { "StackName": stack['Name'], "FleetName": fleet }
			log.debug(str(out))
			return out

class AwsAppstreamSessions:
	def __init__(self, **kwargs):
		self.q = AwsAppstreamStackFleet(**kwargs)
		self.client = self.q.client
		self.session_iter = iter([])

	def __iter__(self):
		self.stack_fleet_iter = iter(self.q)
		return self

	def __next__(self):
		try:
			return next(self.session_iter)
		except StopIteration:
			while True:
				stack_fleet = next(self.stack_fleet_iter)
				sessions = AwsAppstreamQuery("describe_sessions", client=self.client,
					**stack_fleet)

				self.session_iter = iter(sessions)
				try:
					return next(self.session_iter)
				except StopIteration:
					pass

