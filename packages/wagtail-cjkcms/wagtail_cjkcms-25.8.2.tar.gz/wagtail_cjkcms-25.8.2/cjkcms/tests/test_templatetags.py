import re

from django.template import engines
from wagtail.models import Site

from cjkcms.models import AdobeApiSettings
from datetime import datetime, timedelta
from django.test import TestCase
from django.template import Template, Context
from cjkcms.templatetags.cjkcms_tags import is_in_future, is_in_past, first_non_empty


django_engine = engines["django"]
html_id_re = re.compile(r"^[A-Za-z][A-Za-z0-9_:.-]*$")

version_re = re.compile(
    r"^(\d+!)?(\d+)(\.\d+)+([\.\-\_])?((a(lpha)?|b(eta)?|c|r(c|ev)?|pre(view)?)\d*)?(\.?(post|dev)\d*)?$"  # noqa: E501
)


class TemplateTagTests(TestCase):
    def test_cjkcms_generate_random_id(self):
        count = 1000
        t = django_engine.from_string(
            "{% load cjkcms_tags %}{% generate_random_id as rid %}{{rid}}"
        )

        ids = set([])
        for _ in range(count):
            ids.add(t.render(None))
        self.assertEqual(len(ids), count)
        for i, value in enumerate(ids, start=1):
            self.assertTrue(
                html_id_re.match(value),
                'ID #%s "%s" did not match regex %r' % (i, value, html_id_re),
            )

    def test_cjkcms_version(self):
        rt = django_engine.from_string(
            "{% load cjkcms_tags %}{% cjkcms_version %}"
        ).render(None)
        self.assertTrue(
            version_re.match(rt),
            "App Version format incorrect: %r" % version_re,
        )

    def test_django_settings_filter(self):
        rt = django_engine.from_string(
            "{% load cjkcms_tags %}{{ 'APPEND_SLASH'|django_settings  }}"
        ).render(None)
        self.assertIn(
            rt,
            ["True", "False"],
            f"Django setting APPEND_SLASH is neither True nor False, instead is {rt}",
        )

    def test_map_to_bootstrap_alert_filter(self):
        rt = django_engine.from_string(
            "{% load cjkcms_tags %}{{ 'error'|map_to_bootstrap_alert }}"
        ).render(None)
        self.assertEqual(
            rt, "danger", "map_to_bootstrap_alert for 'error' did not return 'danger'"
        )

    def test_brand_logo_long_tag(self):
        rt = django_engine.from_string(
            "{% load cjkcms_tags %}{% brand_logo_long %}"
        ).render(None)
        self.assertIn(
            rt[-4:],
            [".png", ".jpg", ".webp", ".svg"],
            f"Django setting BRAND_LOGO_LONG does not seem to return one of [png,jpg,webp,svg]: {rt}",  # noqa: E501
        )

    def test_brand_logo_square_tag(self):
        rt = django_engine.from_string(
            "{% load cjkcms_tags %}{% brand_logo_square %}"
        ).render(None)
        self.assertIn(
            rt[-4:],
            [".png", ".jpg", ".webp", ".svg"],
            f"Django setting BRAND_LOGO_LONG does not seem to return one of [png,jpg,webp,svg]: {rt}",  # noqa: E501
        )

    def test_AdobeApiKeyInTemplate(self):
        site = Site.objects.filter(is_default_site=True)[0]
        adobe_api_key = AdobeApiSettings.for_site(site=site)
        adobe_api_key.adobe_embed_id = "test_key"  # type: ignore
        adobe_api_key.save()

        rt = django_engine.from_string(
            "{% load wagtailsettings_tags %}{% get_settings use_default_site=True %}{{ settings.cjkcms.AdobeApiSettings.adobe_embed_id }}"  # noqa: E501
        ).render(None)
        self.assertEqual(
            rt, "test_key", "Adobe API key not returned in template context"
        )

    def test_current_year(self):
        rt = django_engine.from_string(
            "{% load cjkcms_tags %}{% current_year %}"
        ).render(None)
        self.assertEqual(rt, str(datetime.now().year), "Current year not returned")

    def test_define_tag(self):
        rt = django_engine.from_string(
            "{% load cjkcms_tags %}{% define 'test' %}{{ test }}"
        ).render(None)
        self.assertEqual(rt, "test", "define tag did not return 'test'")

    def test_is_in_future_with_future_date(self):
        future_date = datetime.now() + timedelta(days=1)
        result = is_in_future(future_date)
        self.assertTrue(result)

    def test_is_in_future_with_past_date(self):
        past_date = datetime.now() - timedelta(days=1)
        result = is_in_future(past_date)
        self.assertFalse(result)

    def test_is_in_past_with_future_date(self):
        future_date = datetime.now() + timedelta(days=1)
        result = is_in_past(future_date)
        self.assertFalse(result)

    def test_is_in_past_with_past_date(self):
        past_date = datetime.now() - timedelta(days=1)
        result = is_in_past(past_date)
        self.assertTrue(result)

    def test_is_in_future_template_tag(self):
        template = Template(
            """{% load cjkcms_tags %}{% if the_date|is_in_future %}future{% else %}not future{% endif %}"""  # noqa: E501
        )
        context = Context({"the_date": datetime.now() + timedelta(days=1)})
        result = template.render(context)
        self.assertEqual(result, "future")

    def test_is_in_past_template_tag(self):
        template = Template(
            "{% load cjkcms_tags %}{% if the_date|is_in_past %}past{% else %}not past{% endif %}"
        )
        context = Context({"the_date": datetime.now() - timedelta(days=1)})
        result = template.render(context)
        self.assertEqual(result, "past")

    def test_all_empty(self):
        self.assertEqual(first_non_empty("", None, False, 0), "")

    def test_first_non_empty(self):
        self.assertEqual(first_non_empty("", None, "first", "second"), "first")

    def test_middle_non_empty(self):
        self.assertEqual(first_non_empty("", None, "first", "second"), "first")

    def test_last_non_empty(self):
        self.assertEqual(first_non_empty("", None, "", "last"), "last")

    def test_all_non_empty(self):
        self.assertEqual(first_non_empty("first", "second", "third"), "first")

    def test_no_arguments(self):
        self.assertEqual(first_non_empty(), "")
