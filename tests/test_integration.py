import pytest
from django.db import connection

from querywatch import QueryCollector, analyze_queries
from querywatch.testing import assert_queries
from tests.testapp.models import Customer, Order


def create_orders() -> None:
    customers = Customer.objects.bulk_create(
        [Customer(name="Ada"), Customer(name="Grace"), Customer(name="Linus")]
    )
    Order.objects.bulk_create([Order(customer=customer) for customer in customers])


@pytest.mark.django_db
def test_integration_detects_django_nplus1_relationship_access() -> None:
    create_orders()
    collector = QueryCollector()

    with collector.capture(connection):
        for order in Order.objects.all():
            assert order.customer.name

    report = analyze_queries(collector.records)

    assert report.summary.query_count == 4
    assert any(finding.rule == "possible-n-plus-one" for finding in report.findings)


@pytest.mark.django_db
def test_integration_select_related_avoids_nplus1_queries() -> None:
    create_orders()

    with assert_queries(max_queries=1):
        orders = list(Order.objects.select_related("customer"))

    assert [order.customer.name for order in orders] == ["Ada", "Grace", "Linus"]
