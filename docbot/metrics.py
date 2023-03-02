from dataclasses import dataclass
from prometheus_client import Histogram


@dataclass
class Metrics:
    github_latency = Histogram(
        name='github',
        documentation='Time spent processing a request from the GitHub service'
    )
