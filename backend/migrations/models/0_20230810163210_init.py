from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "stttask" (
    "uid" UUID NOT NULL  PRIMARY KEY,
    "user_uid" UUID,
    "name" TEXT NOT NULL,
    "status" VARCHAR(20) NOT NULL  DEFAULT 'created',
    "percentage_of_transcribe" INT NOT NULL,
    "audio_url" TEXT NOT NULL,
    "text" TEXT,
    "created_at" DATE NOT NULL
);
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSONB NOT NULL
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
