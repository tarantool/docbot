from dataclasses import dataclass
import ecs_logging


LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': { 
        'ecs': {
            '()': ecs_logging.StdlibFormatter
        },
        'default': {
            'format': '[%(asctime)s] - %(message)s',
        }
    },
    'handlers': {
        'ecs-stdout': {
            'class': 'logging.StreamHandler',
            'formatter': 'ecs'
        }
    },
    'loggers': {
        '': {
            'level': 'INFO',
            'handlers': ['ecs-stdout'],
        },
        'elasticapm': {
            'level': 'WARN',
            'handlers': ['ecs-stdout'],
        },
        'urllib3.connectionpool': {
            'level': 'ERROR',
            'handlers': ['ecs-stdout'],
        },
    }
}
