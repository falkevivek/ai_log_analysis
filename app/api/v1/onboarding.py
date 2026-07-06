"""
Project Onboarding Router — v1
=============================
Defines endpoint routes for Barclays application configuration onboarding.
"""

from __future__ import annotations

import logging
from fastapi import APIRouter, Request, status
from fastapi.responses import JSONResponse

from app.onboarding.schemas import ProjectOnboardingConfig
from app.onboarding.service import OnboardingService
from app.schemas.base import SuccessResponse, ErrorResponse

logger = logging.getLogger("ai_analysis_engine.api.onboarding")
router = APIRouter(tags=["Project Onboarding"])


@router.post(
    "/onboarding/projects",
    response_model=SuccessResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new project onboarding configuration",
    description="Registers configuration parameters, metadata, and custom rules for a Barclays project."
)
async def register_project(request: Request, config: ProjectOnboardingConfig) -> JSONResponse:
    service = OnboardingService(request.app.state.store)
    saved = await service.register_project(config)
    
    # Extract request ID from state if attached by middleware
    request_id = getattr(request.state, "request_id", None)
    
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=SuccessResponse(
            success=True,
            message=f"Project '{config.project_id}' registered successfully.",
            data=saved.model_dump(),
            request_id=request_id
        ).model_dump()
    )


@router.put(
    "/onboarding/projects/{project_id}",
    response_model=SuccessResponse,
    summary="Update project configuration onboarding details",
    description="Modifies registered metadata, component mapping rules, or custom trigger templates."
)
async def update_project(
    request: Request,
    project_id: str,
    config: ProjectOnboardingConfig
) -> JSONResponse:
    service = OnboardingService(request.app.state.store)
    saved = await service.update_project(project_id, config)
    
    request_id = getattr(request.state, "request_id", None)
    
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=SuccessResponse(
            success=True,
            message=f"Project '{project_id}' updated successfully.",
            data=saved.model_dump(),
            request_id=request_id
        ).model_dump()
    )


@router.get(
    "/onboarding/projects",
    response_model=SuccessResponse,
    summary="List all registered onboarding configurations",
    description="Returns a list of all Barclay application onboarding details registered."
)
async def list_projects(request: Request) -> JSONResponse:
    service = OnboardingService(request.app.state.store)
    projects = await service.list_projects()
    
    request_id = getattr(request.state, "request_id", None)
    
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=SuccessResponse(
            success=True,
            message="Registered projects retrieved successfully.",
            data=[p.model_dump() for p in projects],
            request_id=request_id
        ).model_dump()
    )


@router.get(
    "/onboarding/projects/{project_id}",
    response_model=SuccessResponse,
    summary="Get onboarding details for a single project",
    description="Retrieves the registered details, rules, and configuration map by project slug ID."
)
async def get_project(request: Request, project_id: str) -> JSONResponse:
    service = OnboardingService(request.app.state.store)
    project = await service.get_project(project_id)
    
    request_id = getattr(request.state, "request_id", None)
    
    if not project:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=ErrorResponse(
                success=False,
                message=f"Project configuration '{project_id}' was not found.",
                request_id=request_id,
                error={"project_id": project_id}
            ).model_dump()
        )
        
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=SuccessResponse(
            success=True,
            message=f"Project '{project_id}' retrieved successfully.",
            data=project.model_dump(),
            request_id=request_id
        ).model_dump()
    )


@router.delete(
    "/onboarding/projects/{project_id}",
    response_model=SuccessResponse,
    summary="Delete a registered onboarding configuration",
    description="Deletes project details and metadata rules configurations by project slug ID."
)
async def delete_project(request: Request, project_id: str) -> JSONResponse:
    service = OnboardingService(request.app.state.store)
    deleted = await service.delete_project(project_id)
    
    request_id = getattr(request.state, "request_id", None)
    
    if not deleted:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=ErrorResponse(
                success=False,
                message=f"Project configuration '{project_id}' does not exist.",
                request_id=request_id,
                error={"project_id": project_id}
            ).model_dump()
        )
        
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=SuccessResponse(
            success=True,
            message=f"Project '{project_id}' deleted successfully.",
            data=None,
            request_id=request_id
        ).model_dump()
    )
