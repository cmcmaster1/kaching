"""
Research Agent for KaChing Project

This agent specializes in keyword research, competitor analysis, and content opportunity
discovery using multiple MCP servers for comprehensive market research.
"""

import asyncio
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from loguru import logger

from smolagents import CodeAgent, tool
from ..tools.mcp_integration import MCPToolManager
from ..config import KaChingConfig


@dataclass
class ResearchTask:
    """Represents a research task for the agent"""
    niche: str
    keywords: List[str]
    competitor_urls: List[str]
    research_depth: str = "medium"  # shallow, medium, deep
    focus_areas: List[str] = None  # seo, products, content_gaps, etc.


class ResearchAgent:
    """
    Specialized agent for affiliate content research using MCP servers.
    
    Capabilities:
    - Keyword research and analysis
    - Competitor content analysis  
    - Product research and trends
    - Content gap identification
    - SERP analysis
    """
    
    def __init__(self, config: KaChingConfig):
        self.config = config
        self.mcp_manager = MCPToolManager()
        self.agent = None
        self._setup_agent()
    
    async def _internal_keyword_research(
        self,
        seed_keywords: List[str],
        search_volume_min: int = 100,
        difficulty_max: int = 30,
        intent_filter: str = "commercial"
    ) -> Dict[str, Any]:
        """Core logic for keyword research using MCP tools"""
        try:
            results = []
            
            async with self.mcp_manager.get_search_tools() as search_tools_dict:
                if not isinstance(search_tools_dict, dict):
                    logger.error(f"_internal_keyword_research: search_tools was not a dict, but {type(search_tools_dict)}. Bailing out.")
                    return {"keywords": [], "analysis": "Error: Could not access search tools"}

                for keyword in seed_keywords[:3]:  # Limit to 3 keywords to avoid context explosion
                    for server_name, tool_collection in search_tools_dict.items():
                        if not hasattr(tool_collection, 'tools'):
                            logger.warning(f"Tool collection for {server_name} has no 'tools' attribute. Skipping.")
                            continue
                        
                        for tool in tool_collection.tools:
                            if hasattr(tool, 'name') and tool.name == "brave_web_search" and "brave" in server_name.lower():
                                try:
                                    # Search for keyword variations and related terms
                                    search_query = f"{keyword} {intent_filter} intent keywords variations"
                                    logger.debug(f"Researching keyword '{keyword}' with query: {search_query}")
                                    
                                    # Tool is synchronous for Brave Search
                                    result = tool({"query": search_query})
                                    
                                    results.append({
                                        "keyword": keyword,
                                        "server": server_name,
                                        "tool": tool.name,
                                        "results": result
                                    })
                                    
                                    # Add delay to avoid rate limiting
                                    time.sleep(1)
                                    
                                except Exception as e:
                                    logger.warning(f"Error researching keyword {keyword}: {e}")
                                break
                        
                        if results:  # Stop after first successful server
                            break
            
            # Analyze and format results
            analysis = self._analyze_keyword_results(results, search_volume_min, difficulty_max)
            
            return {
                "keywords": [r["keyword"] for r in results],
                "analysis": analysis,
                "raw_results": results
            }
            
        except Exception as e:
            logger.error(f"Error in _internal_keyword_research: {e}")
            return {"keywords": [], "analysis": f"Error in keyword research: {str(e)}"}
    
    async def _internal_competitor_analysis(
        self,
        competitor_urls: List[str],
        analysis_depth: str = "medium"
    ) -> Dict[str, Any]:
        """Core logic for competitor analysis using MCP tools"""
        try:
            results = []
            
            async with self.mcp_manager.get_content_tools() as content_tools_dict:
                if not isinstance(content_tools_dict, dict):
                    logger.error(f"_internal_competitor_analysis: content_tools was not a dict. Bailing out.")
                    return {"competitors": [], "analysis": "Error: Could not access content tools"}

                for url in competitor_urls[:2]:  # Limit to 2 URLs to avoid context explosion
                    for server_name, tool_collection in content_tools_dict.items():
                        if not hasattr(tool_collection, 'tools'):
                            continue
                        
                        for tool in tool_collection.tools:
                            if hasattr(tool, 'name') and "fetch" in tool.name.lower():
                                try:
                                    logger.debug(f"Analyzing competitor: {url}")
                                    
                                    # Try both async and sync calls
                                    try:
                                        content = await tool({"url": url})
                                    except TypeError:
                                        content = tool({"url": url})
                                    
                                    results.append({
                                        "url": url,
                                        "server": server_name,
                                        "content": content,
                                        "analysis_depth": analysis_depth
                                    })
                                    
                                    # Add delay
                                    time.sleep(2)
                                    
                                except Exception as e:
                                    logger.warning(f"Error analyzing competitor {url}: {e}")
                                break
                        
                        if results:  # Stop after first successful server
                            break
            
            # Analyze competitor strategies
            analysis = self._analyze_competitor_content(results, analysis_depth)
            
            return {
                "competitors": [r["url"] for r in results],
                "analysis": analysis,
                "raw_results": results
            }
            
        except Exception as e:
            logger.error(f"Error in _internal_competitor_analysis: {e}")
            return {"competitors": [], "analysis": f"Error in competitor analysis: {str(e)}"}
    
    def _setup_agent(self):
        """Initialize the research agent with simplified tools"""
        
        @tool
        def keyword_research(
            seed_keywords: str,
            search_volume_min: int = 100,
            difficulty_max: int = 30,
            intent_filter: str = "commercial"
        ) -> str:
            """
            Perform keyword research for affiliate content.
            
            Args:
                seed_keywords: Comma-separated list of seed keywords
                search_volume_min: Minimum monthly search volume
                difficulty_max: Maximum keyword difficulty (0-100)
                intent_filter: commercial, informational, navigational, transactional
            """
            try:
                keyword_list = [k.strip() for k in seed_keywords.split(",") if k.strip()]
                
                # Call the internal async method
                result = asyncio.run(self._internal_keyword_research(
                    keyword_list, search_volume_min, difficulty_max, intent_filter
                ))
                
                return result["analysis"]
                
            except Exception as e:
                logger.error(f"Error in keyword_research tool: {e}")
                return f"Error in keyword research: {str(e)}"
        
        @tool
        def competitor_analysis(
            competitor_urls: str,
            analysis_depth: str = "medium"
        ) -> str:
            """
            Analyze competitor content and strategies.
            
            Args:
                competitor_urls: Comma-separated list of competitor URLs
                analysis_depth: shallow, medium, deep
            """
            try:
                url_list = [url.strip() for url in competitor_urls.split(",") if url.strip()]
                
                # Call the internal async method
                result = asyncio.run(self._internal_competitor_analysis(
                    url_list, analysis_depth
                ))
                
                return result["analysis"]
                
            except Exception as e:
                logger.error(f"Error in competitor_analysis tool: {e}")
                return f"Error in competitor analysis: {str(e)}"
        
        research_tools = [keyword_research, competitor_analysis]
        
        # Initialize the agent with no planning to avoid context explosion
        self.agent = CodeAgent(
            tools=research_tools,
            model=self.config.get_model(),
            planning_interval=None,  # Disable planning to prevent context explosion
            additional_authorized_imports=['asyncio']
        )
    
    def _analyze_keyword_results(self, results: List[Dict], min_volume: int, max_difficulty: int) -> str:
        """Analyze keyword research results"""
        analysis = "# Keyword Research Analysis\n\n"
        
        if not results:
            return analysis + "No keyword data found. Please check your search tools configuration.\n"
        
        keyword_opportunities = []
        
        for result in results:
            keyword = result["keyword"]
            server = result["server"]
            search_results = result["results"]
            
            analysis += f"## {keyword}\n\n"
            analysis += f"**Source**: {server}\n"
            
            # Basic analysis of search results
            if isinstance(search_results, str):
                # Extract insights from string results
                result_text = search_results.lower()
                
                # Look for commercial intent indicators
                commercial_indicators = ["buy", "best", "review", "price", "compare", "deal"]
                commercial_score = sum(1 for indicator in commercial_indicators if indicator in result_text)
                
                analysis += f"**Commercial Intent Score**: {commercial_score}/6\n"
                
                # Estimate competition level
                if "amazon" in result_text or "shopping" in result_text:
                    competition = "High"
                elif commercial_score >= 3:
                    competition = "Medium"
                else:
                    competition = "Low"
                
                analysis += f"**Competition Level**: {competition}\n"
                
                # Generate keyword variations
                variations = self._generate_keyword_variations(keyword)
                analysis += f"**Suggested Variations**:\n"
                for variation in variations[:5]:
                    analysis += f"- {variation}\n"
                
                # Add to opportunities if it meets criteria
                if commercial_score >= 2 and competition in ["Low", "Medium"]:
                    keyword_opportunities.append({
                        "keyword": keyword,
                        "commercial_score": commercial_score,
                        "competition": competition,
                        "priority": "High" if competition == "Low" else "Medium"
                    })
            
            analysis += "\n"
        
        # Summary section
        analysis += "## Summary & Recommendations\n\n"
        analysis += f"**Keywords Analyzed**: {len(results)}\n"
        analysis += f"**Opportunities Found**: {len(keyword_opportunities)}\n\n"
        
        if keyword_opportunities:
            analysis += "**Top Opportunities**:\n"
            for opp in keyword_opportunities[:5]:
                analysis += f"- **{opp['keyword']}** (Priority: {opp['priority']}, Competition: {opp['competition']})\n"
        
        analysis += "\n**Next Steps**:\n"
        analysis += "1. Create content for high-priority keywords\n"
        analysis += "2. Research affiliate products for these keywords\n"
        analysis += "3. Analyze competitor content for content gaps\n"
        
        return analysis
    
    def _generate_keyword_variations(self, keyword: str) -> List[str]:
        """Generate keyword variations for better targeting"""
        variations = []
        
        # Common modifiers for affiliate content
        modifiers = [
            "best", "top", "review", "guide", "comparison", 
            "buying guide", "vs", "alternative", "cheap", "affordable"
        ]
        
        # Add modifiers to the keyword
        for modifier in modifiers:
            if modifier not in keyword.lower():
                variations.append(f"{modifier} {keyword}")
                variations.append(f"{keyword} {modifier}")
        
        # Long-tail variations
        long_tail_suffixes = [
            "for arthritis", "for seniors", "easy to use", 
            "with ergonomic design", "for limited mobility"
        ]
        
        for suffix in long_tail_suffixes:
            variations.append(f"{keyword} {suffix}")
        
        return variations[:10]  # Return top 10 variations
    
    def _analyze_competitor_content(self, results: List[Dict], depth: str) -> str:
        """Analyze competitor content and strategies"""
        analysis = "# Competitor Analysis\n\n"
        
        if not results:
            return analysis + "No competitor data found. Please check URLs and content tools.\n"
        
        for result in results:
            url = result["url"]
            content = result["content"]
            
            analysis += f"## {url}\n\n"
            
            # Extract key insights from content
            if isinstance(content, str) and len(content) > 100:
                analysis += f"**Content Preview**: {content[:200]}...\n\n"
                
                # Basic content analysis
                word_count = len(content.split())
                analysis += f"**Metrics**:\n"
                analysis += f"- Word count: ~{word_count}\n"
                analysis += f"- Content type: {'Long-form' if word_count > 1500 else 'Short-form'}\n"
                
                # Look for affiliate indicators
                content_lower = content.lower()
                if "amazon" in content_lower or "affiliate" in content_lower:
                    analysis += "- **Affiliate content detected** ✓\n"
                
                if "review" in content_lower:
                    analysis += "- **Product review content** ✓\n"
                
                if "buy" in content_lower or "purchase" in content_lower:
                    analysis += "- **Commercial intent** ✓\n"
                
                # Content quality indicators
                if word_count > 1000:
                    analysis += "- **Comprehensive content** ✓\n"
                
                analysis += "\n"
            else:
                analysis += "**Status**: Content could not be analyzed (too short or invalid format)\n\n"
        
        analysis += "## Strategic Insights\n\n"
        analysis += "**Content Opportunities**:\n"
        analysis += "- Create more comprehensive content than competitors\n"
        analysis += "- Target long-tail keywords competitors miss\n"
        analysis += "- Focus on user experience and practical advice\n"
        analysis += "- Add comparison tables and buying guides\n\n"
        
        analysis += "**Competitive Advantages**:\n"
        analysis += "- Better SEO optimization\n"
        analysis += "- More detailed product analysis\n"
        analysis += "- User-focused content approach\n"
        analysis += "- Regular content updates\n"
        
        return analysis
    
    async def quick_keyword_research(self, seed_keywords: List[str]) -> Dict[str, Any]:
        """Quick keyword research for immediate insights without context explosion"""
        logger.info(f"Starting quick keyword research for: {seed_keywords}")
        
        try:
            # Use internal method directly to avoid planning system
            result = await self._internal_keyword_research(
                seed_keywords=seed_keywords,
                search_volume_min=100,
                difficulty_max=30,
                intent_filter="commercial"
            )
            
            # Generate keyword opportunities from the analysis
            keyword_opportunities = []
            for keyword in seed_keywords:
                # Create basic opportunity structure
                keyword_opportunities.append({
                    "keyword": keyword,
                    "priority": "High",
                    "competition": "Medium",
                    "content_type": "review"
                })
                
                # Add variations
                variations = self._generate_keyword_variations(keyword)
                for variation in variations[:3]:  # Top 3 variations per keyword
                    keyword_opportunities.append({
                        "keyword": variation,
                        "priority": "Medium",
                        "competition": "Low",
                        "content_type": "guide"
                    })
            
            logger.success("Quick keyword research completed")
            return {
                "status": "success",
                "keyword_opportunities": keyword_opportunities,
                "analysis": result["analysis"],
                "total_keywords": len(keyword_opportunities)
            }
            
        except Exception as e:
            logger.error(f"Quick keyword research failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "keyword_opportunities": []
            }
    
    async def simple_competitor_analysis(self, competitor_urls: List[str]) -> Dict[str, Any]:
        """Simple competitor analysis without context explosion"""
        logger.info(f"Starting simple competitor analysis for: {competitor_urls}")
        
        try:
            # Use internal method directly
            result = await self._internal_competitor_analysis(
                competitor_urls=competitor_urls,
                analysis_depth="shallow"  # Keep it simple
            )
            
            logger.success("Simple competitor analysis completed")
            return {
                "status": "success",
                "competitors_analyzed": result["competitors"],
                "analysis": result["analysis"]
            }
            
        except Exception as e:
            logger.error(f"Simple competitor analysis failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "competitors_analyzed": []
            }
    
    def get_agent_description(self) -> str:
        """Get description of this agent for the orchestrator"""
        return """
Research Agent - Specialized in market research and keyword analysis

Capabilities:
- Keyword research with commercial intent analysis
- Competitor content analysis and gap identification
- Product research and affiliate opportunity discovery
- SERP analysis and ranking opportunities

Tools:
- keyword_research: Find profitable keywords with low competition
- competitor_analysis: Analyze competitor strategies and content

Status: Ready for research tasks (optimized for reduced context)
""" 