"""
Main entry point for API Service.
"""
from datetime import datetime, timedelta
from typing import Optional
from fastapi import FastAPI, Depends, HTTPException, status, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from prometheus_fastapi_instrumentator import Instrumentator
from config import settings
from logger import configure_logging, get_logger
from auth import (
    authenticate_user,
    create_access_token,
    get_current_active_user,
    User,
)
from opensearch_service import OpenSearchService
from models import (
    LoginRequest,
    TokenResponse,
    LogSearchRequest,
    LogSearchResponse,
    StatisticsResponse,
    HealthResponse,
    ErrorResponse,
)

# Configure logging
configure_logging(settings.log_level)
logger = get_logger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="CyberSentinel SyslogServer API",
    description="REST API for querying and managing syslog data",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Prometheus instrumentation
instrumentator = Instrumentator(
    should_group_status_codes=True,
    should_ignore_untemplated=True,
    should_respect_env_var=True,
    should_instrument_requests_inprogress=True,
    excluded_handlers=["/health", "/metrics"],
    env_var_name="ENABLE_METRICS",
    inprogress_name="fastapi_inprogress",
    inprogress_labels=True,
)
instrumentator.instrument(app).expose(app, endpoint="/metrics")

# OpenSearch service instance
opensearch_service: Optional[OpenSearchService] = None


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    global opensearch_service

    logger.info("api_service_starting", version="1.0.0")

    # Initialize OpenSearch service
    opensearch_service = OpenSearchService(
        host=settings.opensearch_host,
        port=settings.opensearch_port,
        scheme=settings.opensearch_scheme,
        user=settings.opensearch_user,
        password=settings.opensearch_password,
        index_prefix=settings.opensearch_index_prefix,
    )

    logger.info("api_service_started")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("api_service_stopping")

    if opensearch_service:
        opensearch_service.close()

    logger.info("api_service_stopped")


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    logger.error("unhandled_exception", error=str(exc), path=request.url.path)
    return JSONResponse(
        status_code=500,
        content={
            "error": "InternalServerError",
            "message": "An unexpected error occurred",
            "detail": str(exc) if settings.environment == "development" else None,
        },
    )


@app.get("/", include_in_schema=False)
async def root():
    """Root endpoint."""
    return {
        "service": "CyberSentinel SyslogServer API",
        "version": "1.0.0",
        "status": "operational",
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "system_info": "/system/info",
            "login": "/auth/login",
            "logs_search": "/logs/search",
            "statistics": "/logs/statistics",
            "threats": "/logs/threats",
        },
        "message": "Welcome to CyberSentinel API - Secure Syslog Monitoring System"
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint.

    Returns service health status and dependency status.
    """
    dependencies = {
        "opensearch": "unknown",
        "redis": "unknown",
    }

    # Check OpenSearch
    try:
        if opensearch_service:
            opensearch_service.client.cluster.health()
            dependencies["opensearch"] = "healthy"
    except Exception:
        dependencies["opensearch"] = "unhealthy"

    # Check Redis
    try:
        import redis
        redis_client = redis.Redis(
            host=settings.redis_host,
            port=settings.redis_port,
            socket_connect_timeout=2
        )
        redis_client.ping()
        dependencies["redis"] = "healthy"
    except Exception:
        dependencies["redis"] = "unhealthy"

    overall_status = "healthy" if all(
        status == "healthy" for status in dependencies.values()
    ) else "degraded"

    return HealthResponse(
        status=overall_status,
        timestamp=datetime.utcnow(),
        version="1.0.0",
        dependencies=dependencies,
    )


@app.post("/auth/login", response_model=TokenResponse)
async def login(login_data: LoginRequest):
    """
    Authenticate user and return access token.

    - **username**: Username
    - **password**: Password
    """
    user = authenticate_user(login_data.username, login_data.password)
    if not user:
        logger.warning("login_failed", username=login_data.username)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=settings.api_access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.username, "scopes": user.scopes},
        expires_delta=access_token_expires,
    )

    logger.info("login_success", username=login_data.username)

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.api_access_token_expire_minutes * 60,
    )


@app.get("/auth/me", response_model=User)
async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """
    Get current user information.

    Requires authentication.
    """
    return current_user


@app.post("/logs/search", response_model=LogSearchResponse)
async def search_logs(
    search_request: LogSearchRequest,
    current_user: User = Depends(get_current_active_user),
):
    """
    Search logs with filters.

    Requires authentication.

    - **query**: Full-text search query
    - **severity**: Severity levels to filter (emergency, alert, critical, error, warning, notice, informational, debug)
    - **facility**: Facilities to filter
    - **hostname**: Hostname to filter
    - **start_time**: Start time for time range
    - **end_time**: End time for time range
    - **page**: Page number (default: 1)
    - **page_size**: Number of results per page (default: 100, max: 1000)
    - **sort_by**: Field to sort by (default: received_at)
    - **sort_order**: Sort order - asc or desc (default: desc)
    """
    try:
        results = await opensearch_service.search_logs(
            query=search_request.query,
            severity=search_request.severity,
            facility=search_request.facility,
            hostname=search_request.hostname,
            start_time=search_request.start_time,
            end_time=search_request.end_time,
            page=search_request.page,
            page_size=search_request.page_size,
            sort_by=search_request.sort_by,
            sort_order=search_request.sort_order,
        )

        logger.info(
            "logs_searched",
            username=current_user.username,
            total_results=results["total"],
            page=search_request.page,
        )

        return LogSearchResponse(**results)

    except Exception as e:
        logger.error("log_search_failed", error=str(e), username=current_user.username)
        raise HTTPException(status_code=500, detail="Log search failed")


@app.get("/logs/statistics", response_model=StatisticsResponse)
async def get_statistics(
    start_time: Optional[datetime] = Query(None, description="Start time for statistics"),
    end_time: Optional[datetime] = Query(None, description="End time for statistics"),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get log statistics.

    Requires authentication.

    Returns aggregated statistics including:
    - Total log count
    - Distribution by severity
    - Distribution by facility
    - Top hosts by log volume
    - Timeline of log volume
    - Threat indicator count
    """
    try:
        stats = await opensearch_service.get_statistics(
            start_time=start_time,
            end_time=end_time,
        )

        logger.info("statistics_retrieved", username=current_user.username)

        return StatisticsResponse(**stats)

    except Exception as e:
        logger.error("statistics_failed", error=str(e), username=current_user.username)
        raise HTTPException(status_code=500, detail="Statistics retrieval failed")


@app.get("/logs/threats")
async def get_threat_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get logs with threat indicators.

    Requires authentication.
    """
    try:
        # Search for logs with threat indicators
        results = await opensearch_service.search_logs(
            page=page,
            page_size=page_size,
            sort_by="threat_score",
            sort_order="desc",
        )

        # Filter for threat indicators
        threat_logs = [
            log for log in results["logs"]
            if log.get("has_threat_indicators", False)
        ]

        logger.info(
            "threat_logs_retrieved",
            username=current_user.username,
            count=len(threat_logs),
        )

        return {
            "total": len(threat_logs),
            "page": page,
            "page_size": page_size,
            "logs": threat_logs,
        }

    except Exception as e:
        logger.error("threat_logs_failed", error=str(e), username=current_user.username)
        raise HTTPException(status_code=500, detail="Threat log retrieval failed")


@app.get("/system/info")
async def get_system_info(current_user: User = Depends(get_current_active_user)):
    """
    Get system information and statistics.

    Requires authentication.
    """
    try:
        # Get OpenSearch cluster stats
        cluster_stats = opensearch_service.client.cluster.stats()
        cluster_health = opensearch_service.client.cluster.health()

        # Get index information
        indices_stats = opensearch_service.client.indices.stats(
            index=f"{settings.opensearch_index_prefix}-*"
        )

        system_info = {
            "api_version": "1.0.0",
            "environment": settings.environment,
            "cluster": {
                "name": cluster_stats.get("cluster_name"),
                "status": cluster_health.get("status"),
                "nodes": cluster_stats.get("nodes", {}).get("count", {}).get("total", 0),
                "indices": cluster_health.get("number_of_data_nodes", 0),
            },
            "storage": {
                "total_size": indices_stats.get("_all", {}).get("primaries", {}).get("store", {}).get("size_in_bytes", 0),
                "document_count": indices_stats.get("_all", {}).get("primaries", {}).get("docs", {}).get("count", 0),
            },
            "cors_enabled": True,
            "cors_origins": settings.cors_origins_list,
        }

        logger.info("system_info_retrieved", username=current_user.username)
        return system_info

    except Exception as e:
        logger.error("system_info_failed", error=str(e), username=current_user.username)
        raise HTTPException(status_code=500, detail="System info retrieval failed")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        workers=settings.api_workers,
        log_level=settings.log_level.lower(),
        access_log=True,
    )
