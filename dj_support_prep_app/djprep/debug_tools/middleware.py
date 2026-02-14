import time
from django.db import connection, reset_queries
from django.conf import settings


class SQLLoggingMiddleware:
    """
    Middleware that logs SQL query statistics for each request.
    Shows query count, total time, and highlights potential issues.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        reset_queries()
        start_time = time.time()

        response = self.get_response(request)

        if settings.DEBUG and connection.queries:
            total_time = time.time() - start_time
            queries = connection.queries

            print('\n' + '=' * 60)
            print(f'REQUEST: {request.method} {request.path}')
            print('=' * 60)
            print(f'Total Queries: {len(queries)}')
            print(f'Total Time: {total_time:.3f}s')

            # Detect duplicates
            query_counts = {}
            for q in queries:
                sql = q['sql']
                query_counts[sql] = query_counts.get(sql, 0) + 1

            duplicates = {k: v for k, v in query_counts.items() if v > 1}
            if duplicates:
                print(f'\nDUPLICATE QUERIES DETECTED: {len(duplicates)}')
                for sql, count in list(duplicates.items())[:3]:
                    print(f'  [{count}x] {sql[:100]}...')

            # Show slow queries
            slow = [q for q in queries if float(q['time']) > 0.1]
            if slow:
                print(f'\nSLOW QUERIES (>100ms): {len(slow)}')
                for q in slow[:3]:
                    print(f'  [{q["time"]}s] {q["sql"][:100]}...')

            print('=' * 60 + '\n')

        return response
