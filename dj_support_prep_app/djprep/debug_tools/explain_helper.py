"""
Helper functions for running EXPLAIN ANALYZE on Django querysets.

Usage in Django shell:
    from debug_tools.explain_helper import explain_query
    from shop.models import Product

    qs = Product.objects.filter(category__name='Electronics')
    explain_query(qs)
"""

from django.db import connection


def explain_query(queryset, analyze=True, verbose=False):
    """
    Run EXPLAIN (ANALYZE) on a Django queryset and print formatted results.

    Args:
        queryset: Django QuerySet to analyze
        analyze: If True, actually executes the query (EXPLAIN ANALYZE)
        verbose: If True, shows additional planning details
    """
    sql, params = queryset.query.sql_with_params()

    explain_cmd = 'EXPLAIN '
    if analyze:
        explain_cmd += 'ANALYZE '
    if verbose:
        explain_cmd += 'VERBOSE '

    full_sql = explain_cmd + sql

    with connection.cursor() as cursor:
        cursor.execute(full_sql, params)
        results = cursor.fetchall()

    print('\n' + '=' * 70)
    print('EXPLAIN ANALYZE OUTPUT')
    print('=' * 70)
    print(f'\nQuery: {sql[:200]}{"..." if len(sql) > 200 else ""}')
    print('\n' + '-' * 70)

    for row in results:
        print(row[0])

    print('-' * 70 + '\n')

    return results


def get_query_sql(queryset):
    """Get the raw SQL for a queryset."""
    sql, params = queryset.query.sql_with_params()
    return sql % tuple(repr(p) for p in params)


def count_queries(func):
    """
    Decorator to count queries executed by a function.

    Usage:
        @count_queries
        def my_view():
            ...
    """
    from django.db import reset_queries

    def wrapper(*args, **kwargs):
        reset_queries()
        result = func(*args, **kwargs)
        queries = connection.queries
        print(f'\n{func.__name__} executed {len(queries)} queries')
        return result

    return wrapper
