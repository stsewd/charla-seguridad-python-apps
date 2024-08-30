"""
URL configuration for testapp project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from testapp import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path(
        "urllib/",
        include(
            [
                path("playground/", views.test_urllib),
                path("open-redirect/", views.open_redirect_index),
                path("redirect/", views.open_redirect, name="redirect"),
                path("is-url-from-same-domain/", views.is_url_from_same_domain),
                path("is-url-relative/", views.is_url_relative),
                path("make-url-relative/", views.make_url_relative),
                path("is-path-under-directory/", views.is_path_under_directory),
            ]
        ),
    ),
    path(
        "xss/",
        include(
            [
                path("simple-xss/", views.simple_xss),
                path("simple-xss-fixed/", views.simple_xss_fixed),
                path("simple-xss-format-html/", views.simple_xss_format_html),
                path(
                    "simple-xss-format-html-fixed/", views.simple_xss_format_html_fixed
                ),
                path(
                    "simple-xss-fixed-with-template/",
                    views.simple_xss_fixed_with_template,
                ),
                path("email/", views.xss_with_email),
                path("json/", views.xss_with_json),
                path("json-fixed/", views.xss_with_json_fixed),
                path("tag-attribute/", views.xss_in_tag_attribute),
                path("tag-attribute-fixed/", views.xss_in_tag_attribute_fixed),
                path("raw-response/", views.xss_in_raw_response),
                path("raw-response-fixed/", views.xss_in_raw_response_fixed),
            ]
        ),
    ),
    path(
        "sqli/",
        include(
            [
                path("simple-sqli/", views.simple_sqli),
                path("simple-sqli-bad-escaping/", views.simple_sqli_bad_escaping),
                path("simple-sqli-fixed/", views.simple_sqli_fixed),
            ]
        ),
    ),
    path(
        "ssrf/",
        include(
            [
                path(
                    "webhook-without-verification/", views.webhook_without_verification
                ),
                path("webhook-with-verification/", views.webhook_with_verification),
                path("outcomming-webhhook/", views.outcomming_webhook),
                path("webhook-secret/", views.get_webhook_secret),
            ]
        ),
    ),
    path(
        "cmdi/",
        include(
            [
                path("simple-command-injection/", views.simple_command_injection),
                path(
                    "simple-command-injection-fixed/",
                    views.simple_command_injection_fixed,
                ),
                path(
                    "command-injection-with-options/",
                    views.command_injection_with_options,
                ),
            ]
        ),
    ),
    path(
        "redos/",
        include(
            [
                path("simple-redos/", views.redos_find_word),
                path("simple-redos-escaped/", views.redos_find_word_escaped),
                path("simple-redos-no-regex/", views.redos_find_word_no_regex),
            ]
        ),
    ),
]
