from django.template.loader import render_to_string
from django.test import TestCase


class TestTemplates(TestCase):
    def test_change_tenant_template(self):
        result = render_to_string('occupation/change_tenant.html', {
            'active_tenant': 1,
            'tenant_choices': [
                (0, 'Zero'),
                (1, 'One'),
            ]
        })
        self.assertTrue(b'select name="__tenant"' in result)
