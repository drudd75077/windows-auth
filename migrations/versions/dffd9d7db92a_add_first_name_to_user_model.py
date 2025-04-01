"""add first_name to User model

Revision ID: dffd9d7db92a
Revises: 37d597a8be44
Create Date: 2025-03-29 22:38:35.699951

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'dffd9d7db92a'
down_revision = '37d597a8be44'
branch_labels = None
depends_on = None


def upgrade():
    # Create a new table with the desired schema
    op.execute('''
        CREATE TABLE user_new (
            id INTEGER NOT NULL PRIMARY KEY,
            username VARCHAR(80) NOT NULL,
            password VARCHAR(120) NOT NULL,
            first_name VARCHAR(50) NOT NULL DEFAULT 'User'
        )
    ''')
    
    # Copy data from the old table
    op.execute('''
        INSERT INTO user_new (id, username, password)
        SELECT id, username, password FROM user
    ''')
    
    # Update first_name with a default value
    op.execute('''
        UPDATE user_new SET first_name = username
    ''')
    
    # Drop the old table
    op.execute('DROP TABLE user')
    
    # Rename the new table
    op.execute('ALTER TABLE user_new RENAME TO user')
    
    # Recreate indexes
    op.execute('CREATE UNIQUE INDEX ix_user_username ON user (username)')


def downgrade():
    # Create a new table without first_name
    op.execute('''
        CREATE TABLE user_new (
            id INTEGER NOT NULL PRIMARY KEY,
            username VARCHAR(80) NOT NULL,
            password VARCHAR(120) NOT NULL
        )
    ''')
    
    # Copy data excluding first_name
    op.execute('''
        INSERT INTO user_new (id, username, password)
        SELECT id, username, password FROM user
    ''')
    
    # Drop the old table
    op.execute('DROP TABLE user')
    
    # Rename the new table
    op.execute('ALTER TABLE user_new RENAME TO user')
    
    # Recreate indexes
    op.execute('CREATE UNIQUE INDEX ix_user_username ON user (username)')