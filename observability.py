"""Opt-in OpenTelemetry tracing, with safe no-op fallback."""
from contextlib import nullcontext
import os

_configured = False


def configure_local_tracing():
    """Enable console spans only when explicitly requested."""
    global _configured
    if _configured or os.getenv("OTEL_CONSOLE_TRACES") != "1":
        return
    from opentelemetry import trace
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter

    provider = TracerProvider(resource=Resource.create({"service.name": "financial-research"}))
    provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))
    trace.set_tracer_provider(provider)
    _configured = True


def traced_span(name):
    """Trace using Langfuse only with explicit opt-in and complete credentials.

    Neither inputs, outputs nor credentials are attached to spans by default.
    Existing local OpenTelemetry and no-op behavior remains the fallback.
    """
    if (
        os.getenv("LANGFUSE_TRACING_ENABLED") == "1"
        and os.getenv("LANGFUSE_PUBLIC_KEY")
        and os.getenv("LANGFUSE_SECRET_KEY")
        and os.getenv("LANGFUSE_BASE_URL")
    ):
        try:
            from langfuse import get_client

            return get_client().start_as_current_observation(
                name=name, as_type="span"
            )
        except Exception:
            # Monitoring must never interrupt a financial-analysis response.
            pass

    try:
        configure_local_tracing()
        from opentelemetry import trace
        return trace.get_tracer("financial-research").start_as_current_span(name)
    except ImportError:
        return nullcontext()
