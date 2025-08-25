"""Django Mercury Performance Testing Framework

A performance testing framework for Django that helps you understand and fix performance issues,
not just detect them.

Basic Usage:
    from django_mercury import DjangoMercuryAPITestCase

    class MyAPITestCase(DjangoMercuryAPITestCase):
        def test_performance(self):
            response = self.client.get('/api/endpoint/')
            self.assertEqual(response.status_code, 200)
            # Performance is automatically monitored and analyzed
"""

__version__ = "0.0.8"
__author__ = "Django Mercury Team"


# Lazy imports to avoid Django configuration issues during installation
def __getattr__(name):
    """Lazy loading of Django-dependent modules."""

    # Django test cases
    if name == "DjangoMercuryAPITestCase":
        try:
            from .python_bindings.django_integration_mercury import DjangoMercuryAPITestCase

            return DjangoMercuryAPITestCase
        except Exception as e:
            # If Django isn't configured, return a placeholder that explains the issue
            import warnings

            # Only show warning if it's not a Django configuration issue
            if "ImproperlyConfigured" not in str(e.__class__.__name__):
                warnings.warn(f"Could not import DjangoMercuryAPITestCase: {e}")

            class DjangoMercuryAPITestCasePlaceholder:
                def __init__(self, *args, **kwargs):
                    raise ImportError(
                        "DjangoMercuryAPITestCase requires Django to be configured. "
                        "Make sure DJANGO_SETTINGS_MODULE is set before importing."
                    )

            return DjangoMercuryAPITestCasePlaceholder
    elif name == "DjangoPerformanceAPITestCase":
        try:
            from .python_bindings.django_integration import DjangoPerformanceAPITestCase

            return DjangoPerformanceAPITestCase
        except Exception as e:
            # If Django isn't configured, return a placeholder that explains the issue
            import warnings

            # Only show warning if it's not a Django configuration issue
            if "ImproperlyConfigured" not in str(e.__class__.__name__):
                warnings.warn(f"Could not import DjangoPerformanceAPITestCase: {e}")

            class DjangoPerformanceAPITestCasePlaceholder:
                def __init__(self, *args, **kwargs):
                    raise ImportError(
                        "DjangoPerformanceAPITestCase requires Django to be configured. "
                        "Make sure DJANGO_SETTINGS_MODULE is set before importing."
                    )

            return DjangoPerformanceAPITestCasePlaceholder

    # Monitor functions
    elif name == "monitor_django_view":
        try:
            from .python_bindings.monitor import monitor_django_view

            return monitor_django_view
        except Exception as e:
            import warnings

            if "ImproperlyConfigured" not in str(e.__class__.__name__):
                warnings.warn(f"Could not import monitor_django_view: {e}")

            def monitor_django_view_placeholder(*args, **kwargs):
                raise ImportError(
                    "monitor_django_view requires Django to be configured. "
                    "Make sure DJANGO_SETTINGS_MODULE is set before importing."
                )

            return monitor_django_view_placeholder
    elif name == "monitor_django_model":
        try:
            from .python_bindings.monitor import monitor_django_model

            return monitor_django_model
        except Exception as e:
            import warnings

            if "ImproperlyConfigured" not in str(e.__class__.__name__):
                warnings.warn(f"Could not import monitor_django_model: {e}")

            def monitor_django_model_placeholder(*args, **kwargs):
                raise ImportError(
                    "monitor_django_model requires Django to be configured. "
                    "Make sure DJANGO_SETTINGS_MODULE is set before importing."
                )

            return monitor_django_model_placeholder
    elif name == "monitor_serializer":
        try:
            from .python_bindings.monitor import monitor_serializer

            return monitor_serializer
        except Exception as e:
            import warnings

            if "ImproperlyConfigured" not in str(e.__class__.__name__):
                warnings.warn(f"Could not import monitor_serializer: {e}")

            def monitor_serializer_placeholder(*args, **kwargs):
                raise ImportError(
                    "monitor_serializer requires Django to be configured. "
                    "Make sure DJANGO_SETTINGS_MODULE is set before importing."
                )

            return monitor_serializer_placeholder
    elif name == "EnhancedPerformanceMonitor":
        from .python_bindings.monitor import EnhancedPerformanceMonitor

        return EnhancedPerformanceMonitor
    elif name == "EnhancedPerformanceMetrics_Python":
        from .python_bindings.monitor import EnhancedPerformanceMetrics_Python

        return EnhancedPerformanceMetrics_Python

    # Constants
    elif name == "RESPONSE_TIME_THRESHOLDS":
        from .python_bindings.constants import RESPONSE_TIME_THRESHOLDS

        return RESPONSE_TIME_THRESHOLDS
    elif name == "MEMORY_THRESHOLDS":
        from .python_bindings.constants import MEMORY_THRESHOLDS

        return MEMORY_THRESHOLDS
    elif name == "QUERY_COUNT_THRESHOLDS":
        from .python_bindings.constants import QUERY_COUNT_THRESHOLDS

        return QUERY_COUNT_THRESHOLDS
    elif name == "N_PLUS_ONE_THRESHOLDS":
        from .python_bindings.constants import N_PLUS_ONE_THRESHOLDS

        return N_PLUS_ONE_THRESHOLDS

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def enable_educational_testing(level="beginner"):
    """
    Enable Django Mercury Educational Testing Mode programmatically.

    This function configures Django to use Mercury's educational test runner
    and sets the appropriate environment variables for educational mode.

    Args:
        level: Educational difficulty level ('beginner', 'intermediate', 'advanced')

    Example:
        In your Django settings.py or manage.py:

        from django_mercury import enable_educational_testing
        enable_educational_testing('intermediate')

    Returns:
        str: The test runner class path that was configured
    """
    import os
    from django.conf import settings

    # Set environment variables
    os.environ["MERCURY_EDU"] = "1"
    os.environ["MERCURY_EDUCATIONAL_MODE"] = "true"
    os.environ["MERCURY_EDU_LEVEL"] = level

    # Configure Django to use educational test runner
    test_runner = "django_mercury.test_runner.EducationalTestRunner"

    # Update Django settings if they're already configured
    if settings.configured:
        settings.TEST_RUNNER = test_runner

    return test_runner


__all__ = [
    "DjangoMercuryAPITestCase",
    "DjangoPerformanceAPITestCase",
    "monitor_django_view",
    "monitor_django_model",
    "monitor_serializer",
    "EnhancedPerformanceMonitor",
    "EnhancedPerformanceMetrics_Python",
    "RESPONSE_TIME_THRESHOLDS",
    "MEMORY_THRESHOLDS",
    "QUERY_COUNT_THRESHOLDS",
    "N_PLUS_ONE_THRESHOLDS",
    "enable_educational_testing",
]
