"""
:mod:`occupation.management.commands.loaddata`

This replaces the ``loaddata`` command with one that takes a new
option: ``--tenant``. This tenant will be "active" when executing the
query, and RLS should apply to that.
"""
from django.core.management.commands import loaddata

from occupation.utils import activate_tenant


class Command(loaddata.Command):
    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)
        parser.add_argument(
            '--tenant',
            action='store',
            dest='tenant',
            help='Specify which tenant should be active',
        )

    def handle(self, *fixture_labels, **options):
        tenant = options.get('tenant')
        if tenant:
            activate_tenant(tenant)

        # We should wrap this in a try/except, and present a reasonable
        # error message if we think we tried to load data without a schema
        # that required one.
        super(Command, self).handle(*fixture_labels, **options)

        if tenant:
            activate_tenant('')
