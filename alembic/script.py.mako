<%
import re
import datetime
timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M")
%>
"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision}
Create Date: ${timestamp}

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '${up_revision}'
down_revision = ${repr(down_revision)}
branch_labels = None
depends_on = None


def upgrade() -> None:
    ${upgrades if upgrades else "pass"}


def downgrade() -> None:
    ${downgrades if downgrades else "pass"}
