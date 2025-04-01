"""change first_name to display_name

Revision ID: ad59210acf2a
Revises: dffd9d7db92a
Create Date: 2025-04-01 04:16:46.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ad59210acf2a'
down_revision = 'dffd9d7db92a'
branch_labels = None
depends_on = None


def upgrade():
    # Create a new table with display_name instead of first_name
    op.execute('''
        CREATE TABLE user_new (
            id INTEGER NOT NULL PRIMARY KEY,
            username VARCHAR(80) NOT NULL,
            password VARCHAR(120) NOT NULL,
            display_name VARCHAR(50) NOT NULL
        )
    ''')
    
    # Copy data from the old table, renaming first_name to display_name
    op.execute('''
        INSERT INTO user_new (id, username, password, display_name)
        SELECT id, username, password, first_name FROM user
    ''')
    
    # Drop the old table
    op.execute('DROP TABLE user')
    
    # Rename the new table
    op.execute('ALTER TABLE user_new RENAME TO user')
    
    # Recreate indexes
    op.execute('CREATE UNIQUE INDEX ix_user_username ON user (username)')


def downgrade():
    # Create a new table with first_name instead of display_name
    op.execute('''
        CREATE TABLE user_new (
            id INTEGER NOT NULL PRIMARY KEY,
            username VARCHAR(80) NOT NULL,
            password VARCHAR(120) NOT NULL,
            first_name VARCHAR(50) NOT NULL
        )
    ''')
    
    # Copy data from the old table, renaming display_name to first_name
    op.execute('''
        INSERT INTO user_new (id, username, password, first_name)
        SELECT id, username, password, display_name FROM user
    ''')
    
    # Drop the old table
    op.execute('DROP TABLE user')
    
    # Rename the new table
    op.execute('ALTER TABLE user_new RENAME TO user')
    
    # Recreate indexes
    op.execute('CREATE UNIQUE INDEX ix_user_username ON user (username)')