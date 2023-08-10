from settings import settings


TORTOISE_ORM = {
        'connections': {
            # Dict format for connection
            # 'default': {
            #     'engine': 'tortoise.backends.asyncpg',
            #     'credentials': {
            #         'host': 'localhost',
            #         'port': settings.DATABASE_PORT,
            #         'user': settings.DATABASE_USERNAME,
            #         'password': settings.DATABASE_PASSWORD,
            #         'database': settings.DATABASE_NAME,
            #     }
            # },
            'default': 'postgres://postgres:postgres@db:5432/postgres'
        },
        'apps': {
            'models': {
                'models': ['__main__', 'stt.models', 'aerich.models',],
                # If no default_connection specified, defaults to 'default'
                'default_connection': 'default',
            }
        }
    }