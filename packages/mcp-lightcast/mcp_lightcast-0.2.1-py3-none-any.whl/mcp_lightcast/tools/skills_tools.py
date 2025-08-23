"""MCP tools for Lightcast Skills API."""

from typing import Any

from fastmcp import FastMCP

from ..apis.skills import SkillsAPIClient
from ..apis.similarity import SimilarityAPIClient


def register_skills_tools(mcp: FastMCP):
    """Register core skills-related MCP tools."""

    @mcp.tool
    async def search_skills(
        query: str,
        limit: int = 10,
        skill_type: str | None = None,
        category: str | None = None,
        subcategory: str | None = None,
        version: str = "latest"
    ) -> list[dict[str, Any]]:
        """
        Search for skills in the Lightcast skills database.
        
        Args:
            query: Search term for skills
            limit: Maximum number of results to return (default: 10)
            skill_type: Filter by skill type (e.g., "Hard Skill", "Soft Skill")
            category: Filter by skill category
            subcategory: Filter by skill subcategory
            version: API version to use (default: "latest", can specify previous versions like "9.33", "9.32", etc.)
            
        Returns:
            List of matching skills with their details
        """
        async with SkillsAPIClient() as client:
            results = await client.search_skills(
                query, limit, skill_type, category, subcategory, version
            )
            return [
                {
                    "id": result.id,
                    "name": result.name,
                    "type": result.type.name if result.type else None,
                    "type_id": result.type.id if result.type else None,
                    "category": result.category,
                    "subcategory": result.subcategory
                }
                for result in results
            ]

    @mcp.tool
    async def get_skill_details(
        skill_id: str,
        version: str = "latest"
    ) -> dict[str, Any]:
        """
        Get detailed information about a specific skill.
        
        Args:
            skill_id: Lightcast skill ID
            version: API version to use (default: "latest", can specify previous versions like "9.33", "9.32", etc.)
            
        Returns:
            Detailed skill information including description and metadata
        """
        async with SkillsAPIClient() as client:
            result = await client.get_skill_by_id(skill_id, version)
            return {
                "id": result.id,
                "name": result.name,
                "type": result.type,
                "category": result.category,
                "subcategory": result.subcategory,
                "description": result.description,
                "tags": result.tags,
                "info_url": result.infoUrl
            }

    @mcp.tool
    async def bulk_retrieve_skills(
        skill_ids: list[str],
        version: str = "latest"
    ) -> list[dict[str, Any]]:
        """
        Retrieve multiple skills by their IDs in a single efficient request.
        
        Args:
            skill_ids: List of Lightcast skill IDs to retrieve
            version: API version to use (default: "latest", can specify previous versions like "9.33", "9.32", etc.)
            
        Returns:
            List of detailed skill information for all requested skills
        """
        async with SkillsAPIClient() as client:
            results = await client.bulk_retrieve_skills(skill_ids, version)
            return [
                {
                    "id": result.id,
                    "name": result.name,
                    "type": result.type.name if result.type else None,
                    "type_id": result.type.id if result.type else None,
                    "category": result.category,
                    "subcategory": result.subcategory,
                    "description": result.description,
                    "tags": result.tags,
                    "info_url": result.infoUrl
                }
                for result in results
            ]

    @mcp.tool
    async def extract_skills_from_text(
        text: str,
        confidence_threshold: float = 0.5,
        version: str = "latest"
    ) -> list[dict[str, Any]]:
        """
        Extract skills mentioned in a text description.
        
        Args:
            text: Text to analyze for skill mentions
            confidence_threshold: Minimum confidence score for skill extraction (default: 0.5)
            version: API version to use (default: "latest", can specify previous versions like "9.33", "9.32", etc.)
            
        Returns:
            List of extracted skills with confidence scores
        """
        async with SkillsAPIClient() as client:
            return await client.extract_skills_from_text(text, confidence_threshold, version)

    @mcp.tool
    async def get_related_skills(
        skill_id: str,
        limit: int = 10,
        version: str = "latest"
    ) -> list[dict[str, Any]]:
        """
        Get skills related to a specific skill.
        
        Args:
            skill_id: Lightcast skill ID
            limit: Maximum number of related skills to return (default: 10)
            version: API version to use (default: "latest", can specify previous versions like "9.33", "9.32", etc.)
            
        Returns:
            List of related skills with similarity information
        """
        async with SkillsAPIClient() as client:
            results = await client.get_related_skills(skill_id, limit, version)
            return [
                {
                    "id": result.id,
                    "name": result.name,
                    "type": result.type.name if result.type else None,
                    "type_id": result.type.id if result.type else None,
                    "category": result.category,
                    "subcategory": result.subcategory
                }
                for result in results
            ]

    @mcp.tool
    async def find_similar_skills(
        skill_id: str,
        limit: int = 10
    ) -> list[dict[str, Any]]:
        """
        Find similar skills using the Similarity API.
        
        Args:
            skill_id: Lightcast skill ID
            limit: Maximum number of similar skills to return (default: 10)
            
        Returns:
            List of similar skills with similarity scores
        """
        async with SimilarityAPIClient() as client:
            results = await client.get_similar_skills(skill_id, limit)
            return results

    @mcp.tool
    async def get_skills_metadata(
        version: str = "latest"
    ) -> dict[str, Any]:
        """
        Get metadata about the Lightcast skills taxonomy.
        
        Args:
            version: API version to use (default: "latest", can specify previous versions like "9.33", "9.32", etc.)
            
        Returns:
            Metadata about the skills database including statistics and version info
        """
        async with SkillsAPIClient() as client:
            return await client.get_skills_metadata(version)