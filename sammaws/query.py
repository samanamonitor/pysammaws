import boto3
from botocore.client import BaseClient
from botocore.exceptions import ClientError
import logging
import time

log = logging.getLogger(__name__)

def setLevel(level):
	log.setLevel(level)

class AwsObject(dict):
	def __init__(self, data=None):
		if data is None:
			return
		if not isinstance(data, dict):
			raise TypeError("Invalid data type")
		for k, v in data.items():
			_ = self.setdefault(k, v)

	def get(self, key, default=None):
		temp = key
		get = super(AwsObject, self).get
		while True:
			l, _, temp = temp.partition(".")
			val = get(l)
			if temp == '':
				return val
			if val is None:
				raise KeyError(key)
			if not isinstance(val, dict):
				raise KeyError
			get = val.get

class AwsQuery:
	_service_queries = {}
	_service_name = ""
	def __init__(self, query_name, client=None,
			aws_access_key_id=None, aws_secret_access_key=None,
			aws_session_token=None, region_name='us-east-1', log_level="WARNING", query_throttle=0.1, **kwargs):
		if client is None:
			self.client = boto3.client(self._service_name, aws_access_key_id=None, 
				aws_secret_access_key=None, aws_session_token=None,
				region_name=region_name)
		else:
			self.client = client
		if not isinstance(self.client, BaseClient):
			raise TypeError("Invalid client type")

		self._kwargs = kwargs.copy()
		self._query_name = query_name
		self._func = getattr(self.client, self._query_name)
		self._object_name = self._service_queries[self._query_name]
		self._query_throttle = float(query_throttle)
		log.debug("(%s) query_name=%s query_throttle=%f", self.__class__, query_name, query_throttle)

	def _get_data(self):
		log.debug("before %s", self._query_name)
		try:
			log.debug("sleeping %f seconds", self._query_throttle)
			time.sleep(self._query_throttle)
			self._first_dataset = self._func(**self._kwargs)
		except ClientError as e:
			log.error("Error class: %s, %s", e.__class__.__name__, str(e))
			raise
		log.debug("after %s", self._query_name)
		if "NextToken" in self._first_dataset:
			self._kwargs["NextToken"] = self._first_dataset.get("NextToken")
		else:
			_ = self._kwargs.pop("NextToken", None)
		self._iter = iter(self._first_dataset.get(self._object_name))

	def __next__(self):
		while True:
			try:
				data = next(self._iter)
				if isinstance(data, str):
					return data
				else:
					return AwsObject(data)
			except StopIteration:
				log.debug("No items in local cache. Getting from AWS. object_name=%s service_name=%s query_name=%s kwargs=%s", 
					self._object_name, self._service_name, self._query_name, str(self._kwargs))
				if self._kwargs.get("NextToken") is None:
					raise
				self._get_data()

	def __iter__(self):
		self._get_data()
		return self

