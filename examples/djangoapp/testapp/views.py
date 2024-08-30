import hashlib
import subprocess
import os
import requests
import hmac
from django.http import HttpResponse
import json
from django.views.decorators.csrf import csrf_exempt
from testapp import urllibutils
from urllib.parse import urlparse
from django.db import connection
from django.utils.html import format_html
from django.shortcuts import redirect, render
from django.utils.html import escape
from django.core.validators import EmailValidator
from django.core.exceptions import ValidationError
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.safestring import mark_safe
import re

WEBHOOK_SECRET = "very-secret-and-random-value"


def simple_xss(request):
    name = request.GET.get("name", "world")
    return HttpResponse(f"<p>Hello, {name}!</p>")


def simple_xss_fixed(request):
    name = request.GET.get("name", "world")
    return HttpResponse(f"<p>Hello, {escape(name)}!</p>")


def simple_xss_format_html(request):
    name = request.GET.get("name", "world")
    return HttpResponse(format_html(f"<p>Hello, {name}!</p>"))


def simple_xss_format_html_fixed(request):
    name = request.GET.get("name", "world")
    return HttpResponse(format_html("<p>Hello, {name}!</p>", name=name))


def simple_xss_fixed_with_template(request):
    name = request.GET.get("name", "world")
    return render(request, "xss/fixed-with-template.html", {"name": name})


def xss_with_email(request):
    email = request.GET.get("email", "test@example.com")
    valid = False
    try:
        EmailValidator()(email)
        valid = True
    except ValidationError:
        pass

    return render(request, "xss/email.html", {"email": email, "valid": valid})


def xss_with_json(request):
    name = request.GET.get("name", "world")
    json_dump = mark_safe(json.dumps({"name": name}))
    return render(request, "xss/json.html", {"json": json_dump, "name": name})


def xss_with_json_fixed(request):
    name = request.GET.get("name", "world")
    json_dump = json.dumps({"name": name})
    return render(request, "xss/json-fixed.html", {"json": json_dump, "name": name})


def xss_in_tag_attribute(request):
    name = request.GET.get("name", "world")
    return render(request, "xss/tag-attribute.html", {"name": name})


def xss_in_tag_attribute_fixed(request):
    name = request.GET.get("name", "world")
    return render(request, "xss/tag-attribute-fixed.html", {"name": name})


def xss_in_raw_response(request):
    name = request.GET.get("name", "world")
    return HttpResponse(f"Name not found: {name}", status=404)


def xss_in_raw_response_fixed(request):
    name = request.GET.get("name", "world")
    return HttpResponse(
        f"Name not found: {name}", status=404, content_type="text/plain"
    )


def simple_sqli(request):
    """
    Example show how SQL injection works
    """
    username = request.GET.get("username", "admin")
    cursor = connection.cursor()
    results = cursor.execute(
        f"SELECT username FROM auth_user WHERE username='{username}'"
    )
    return render(request, "sqli/list.html", {"results": results, "username": username})


def simple_sqli_bad_escaping(request):
    username = request.GET.get("username", "admin")
    cursor = connection.cursor()
    results = cursor.execute(
        "SELECT username FROM auth_user WHERE username='%s'" % (username,)
    )
    return render(request, "sqli/list.html", {"results": results, "username": username})


def simple_sqli_fixed(request):
    username = request.GET.get("username", "admin")
    cursor = connection.cursor()
    results = cursor.execute(
        "SELECT username FROM auth_user WHERE username=%s", [username]
    )
    return render(request, "sqli/list.html", {"results": results, "username": username})


def test_urllib(request):
    url = request.GET.get("url", "https://example.com")
    parsed = urlparse(url)
    return render(request, "urllib/index.html", {"parsed": parsed, "url": url})


def open_redirect_index(request):
    url = request.GET.get("url", "https://example.com")
    return render(request, "urllib/open-redirect.html", {"url": url})


def open_redirect(request):
    url = request.GET.get("url", "https://example.com")
    return redirect(url)


def is_url_from_same_domain(request):
    functions = {
        "is_allowed_domain_in": urllibutils.is_allowed_domain_in,
        "is_allowed_domain_regex": urllibutils.is_allowed_domain_regex,
        "is_allowed_domain_regex2": urllibutils.is_allowed_domain_regex2,
        "is_allowed_domain_protocol_check": urllibutils.is_allowed_domain_protocol_check,
        "is_allowed_domain_backslashes": urllibutils.is_allowed_domain_backslashes,
        "django": lambda url: url_has_allowed_host_and_scheme(
            url, allowed_hosts=["example.com"]
        ),
    }
    function_name = request.GET.get("function", "is_allowed_domain_in")
    function_to_test = functions[function_name]
    url = request.GET.get("url", "https://example.com")
    return render(
        request,
        "urllib/same-domain-check.html",
        {
            "url": url,
            "selected_function": function_name,
            "result": function_to_test(url),
            "functions": functions.keys(),
        },
    )


def is_url_relative(request):
    url = request.GET.get("url", "/path/to/file")
    parsed = urlparse(url)
    return render(
        request,
        "urllib/is-url-relative.html",
        {"result": not parsed.hostname, "url": url},
    )


def make_url_relative(request):
    url = request.GET.get("url", "https://example.com")
    current_host = request.get_host()
    protocol = "https" if request.is_secure() else "http"
    relative_url = f"{protocol}://{current_host}" + "/" + url
    return render(
        request,
        "urllib/make-url-relative.html",
        {"url": url, "relative_url": relative_url},
    )


def is_path_under_directory(request):
    url = request.GET.get("url", "https://example.com/static/file")
    functions = {
        "is_allowed_path_startswith": urllibutils.is_allowed_path_startswith,
        "is_allowed_path_normalize_path": urllibutils.is_allowed_path_normalize_path,
    }
    function_name = request.GET.get("function", "is_allowed_path_startswith")
    function_to_test = functions[function_name]
    result = function_to_test(url)
    return render(
        request,
        "urllib/is-path-under-directory.html",
        {
            "url": url,
            "selected_function": function_name,
            "result": result,
            "functions": functions.keys(),
        },
    )


@csrf_exempt
def webhook_without_verification(request):
    if request.method != "POST":
        return HttpResponse(status=405)
    json_data = json.loads(request.body)
    # Do stuff
    return HttpResponse(json.dumps({"result": "ok"}), content_type="application/json")


@csrf_exempt
def webhook_with_verification(request):
    if request.method != "POST":
        return HttpResponse(status=405)

    payload = request.body.decode()
    digest = hmac.new(
        key=WEBHOOK_SECRET.encode(),
        msg=payload.encode(),
        digestmod=hashlib.sha256,
    )
    expected_signature = digest.hexdigest()
    x_hub_signature = request.headers.get("X-Hub-Signature", "")
    if not x_hub_signature:
        return HttpResponse(
            json.dumps({"result": "missing signature"}),
            status=403,
            content_type="application/json",
        )
    is_valid = hmac.compare_digest(
        x_hub_signature.encode(),
        expected_signature.encode(),
    )
    if not is_valid:
        return HttpResponse(
            json.dumps({"result": "invalid signature"}),
            status=403,
            content_type="application/json",
        )
    # Do stuff
    return HttpResponse(json.dumps({"result": "ok"}), content_type="application/json")


def get_webhook_secret(request):
    return HttpResponse(WEBHOOK_SECRET, content_type="text/plain")


def outcomming_webhook(request):
    url = request.GET.get("url", "https://cataas.com/cats")
    response = requests.get(url)
    return render(
        request,
        "ssrf.html",
        {"url": url, "content": response.text},
    )


def simple_command_injection(request):
    domain = request.GET.get("domain", "example.com")
    success = os.system(f"ping -c 2 {domain}") == 0
    return render(
        request,
        "cmdi/simple-command-injection.html",
        {"success": success, "domain": domain},
    )


def simple_command_injection_fixed(request):
    domain = request.GET.get("domain", "example.com")
    success = subprocess.run(["ping", "-c", "2", domain]).returncode == 0
    return render(
        request,
        "cmdi/simple-command-injection.html",
        {"success": success, "domain": domain},
    )


def command_injection_with_options(request):
    """
    Test with:

    - --html=touch /tmp/test/man
    """
    section = request.GET.get("section", "1")
    page = request.GET.get("page", "nvim")
    result = subprocess.run(["man", section, page], stdout=subprocess.PIPE)
    content = result.stdout.decode()
    return render(
        request,
        "cmdi/command-injection-with-options.html",
        {"content": content, "section": section, "page": page},
    )


def redos_find_word(request):
    """
    Test with:

    - word: (a|a)+b
    - text: aaaaaaaaaaaaaa!
    """
    word = request.GET.get("word", "world")
    text = request.GET.get("text", "Hello World")
    pattern = re.compile(word, re.IGNORECASE)
    found = pattern.search(text)
    return render(
        request, "redos/find-word.html", {"found": found, "word": word, "text": text}
    )


def redos_find_word_escaped(request):
    word = request.GET.get("word", "world")
    text = request.GET.get("text", "Hello World")
    escaped_word = re.escape(word)
    pattern = re.compile(escaped_word, re.IGNORECASE)
    found = pattern.search(text)
    return render(
        request, "redos/find-word.html", {"found": found, "word": word, "text": text}
    )


def redos_find_word_no_regex(request):
    word = request.GET.get("word", "world")
    text = request.GET.get("text", "Hello World")
    found = word.lower() in text.lower()
    return render(
        request, "redos/find-word.html", {"found": found, "word": word, "text": text}
    )
