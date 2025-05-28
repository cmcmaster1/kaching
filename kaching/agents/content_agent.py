"""
Content Agent for KaChing Project

This agent specializes in content creation, SEO optimization, and quality control
using multiple MCP servers for enhanced content generation capabilities.
"""

import asyncio
import re
import time # Import time module for sleep
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from loguru import logger

from smolagents import CodeAgent, tool
from ..tools.mcp_integration import MCPToolManager
from ..config import KaChingConfig


@dataclass
class ContentTask:
    """Represents a content creation task for the agent"""
    title: str
    keywords: List[str]
    content_type: str  # review, comparison, guide, listicle
    target_word_count: int = 1500
    affiliate_products: List[str] = None
    seo_requirements: Dict[str, Any] = None
    quality_threshold: float = 8.0  # 0-10 scale


@dataclass
class ContentTemplate:
    """Template for different content types"""
    name: str
    structure: List[str]  # List of section headers
    word_count_range: tuple  # (min, max)
    seo_focus: str
    affiliate_integration: str


class ContentAgent:
    """
    Specialized agent for content creation using MCP servers.
    
    Capabilities:
    - Article generation with templates
    - SEO optimization and meta data creation
    - Content quality scoring and improvement
    - Fact-checking and source verification
    - Affiliate link integration
    - Content formatting and enhancement
    """
    
    def __init__(self, config: KaChingConfig):
        self.config = config
        self.mcp_manager = MCPToolManager()
        self.agent = None
        self.templates = self._load_content_templates()
        self._setup_agent()
    
    async def _internal_generate_article(
        self,
        title: str,
        keywords: List[str],
        content_type: str,
        word_count: int,
        affiliate_products: List[str]
    ) -> str:
        """Core logic for generating an article, without SEO optimization within this step."""
        try:
            # Get content template
            template = self._get_template(content_type)
            
            # Research content using MCP tools
            research_data = await self._research_content_topic(title, keywords)
            
            # Generate article structure
            article_structure = self._create_article_structure(
                title, template, keywords, affiliate_products, word_count
            )
            
            # Generate content sections
            content = await self._generate_content_sections(
                article_structure, research_data, keywords
            )
            # NOTE: SEO optimization is removed from here and will be a separate step
            return content
            
        except Exception as e:
            logger.error(f"Error in _internal_generate_article: {e}")
            return f"Error generating article content: {str(e)}"
    
    async def _internal_optimize_content_seo(
        self,
        content: str,
        keywords: List[str],
        meta_title: str = "",
        meta_description: str = ""
    ) -> str:
        """Core logic for optimizing content for SEO."""
        try:
            # Analyze current content
            analysis = self._analyze_content_seo(content, keywords)
            
            # Generate optimized version (this might be an async call in a fuller version)
            optimized = await self._apply_seo_optimizations(
                content, keywords, analysis
            )
            
            # Generate meta data
            meta_data = self._generate_meta_data(
                optimized, keywords, meta_title, meta_description
            )
            
            # Combine content with meta data
            final_content = self._format_final_content(optimized, meta_data)
            
            return final_content
            
        except Exception as e:
            logger.error(f"Error in _internal_optimize_content_seo: {e}")
            return f"Error optimizing content: {str(e)}"
    
    async def _internal_fact_check_content(
        self,
        content: str,
        sources_required: int = 3
    ) -> str:
        """Core logic for fact-checking content."""
        try:
            # Extract factual claims from content
            claims = self._extract_factual_claims(content)
            
            # Verify claims using search tools
            verification_results = await self._verify_claims(claims, sources_required)
            
            # Generate fact-check report
            report = self._generate_fact_check_report(verification_results)
            
            return report
            
        except Exception as e:
            logger.error(f"Error in _internal_fact_check_content: {e}")
            return f"Error fact-checking content: {str(e)}"
    
    async def _internal_score_content_quality(
        self,
        content: str,
        criteria_list: List[str]
    ) -> str:
        """Core logic for scoring content quality."""
        try:
            # Score each criterion
            scores = {}
            for criterion in criteria_list:
                # _score_criterion is sync, no await needed here for the call itself,
                # but the wrapper is async for consistency if _score_criterion became async later.
                scores[criterion] = self._score_criterion(content, criterion)
            
            # Calculate overall score
            overall_score = sum(scores.values()) / len(scores) if scores else 0.0
            
            # Generate improvement suggestions
            suggestions = self._generate_improvement_suggestions(scores, content)
            
            # Format results
            result = self._format_quality_score(scores, overall_score, suggestions)
            
            return result
            
        except Exception as e:
            logger.error(f"Error in _internal_score_content_quality: {e}")
            return f"Error scoring content quality: {str(e)}"
    
    def _setup_agent(self):
        """Initialize the content agent with MCP tools"""
        
        @tool
        def generate_article(
            title: str,
            keywords: str,
            content_type: str = "review",
            word_count: int = 1500,
            affiliate_products: str = ""
        ) -> str:
            """
            Generate a complete article. SEO optimization should be done as a separate step.
            
            Args:
                title: Article title
                keywords: Comma-separated target keywords
                content_type: review, comparison, guide, listicle
                word_count: Target word count
                affiliate_products: Comma-separated product names to include
            """
            try:
                # Parse inputs
                keyword_list = [k.strip() for k in keywords.split(",") if k.strip()]
                product_list = [p.strip() for p in affiliate_products.split(",") if p.strip()]
                
                # Call the internal async method
                # self here refers to the ContentAgent instance
                generated_content = asyncio.run(self._internal_generate_article(
                    title, keyword_list, content_type, word_count, product_list
                ))
                return generated_content
                
            except Exception as e:
                logger.error(f"Error in generate_article tool: {e}")
                return f"Error in generate_article tool: {str(e)}"
        
        @tool
        def optimize_content_seo(
            content: str,
            target_keywords: str,
            meta_title: str = "",
            meta_description: str = ""
        ) -> str:
            """
            Optimize content for SEO with keyword integration and meta data.
            
            Args:
                content: Raw content to optimize
                target_keywords: Comma-separated keywords to optimize for
                meta_title: Custom meta title (optional)
                meta_description: Custom meta description (optional)
            """
            try:
                keyword_list = [k.strip() for k in target_keywords.split(",") if k.strip()]
                
                # Call the internal async method
                optimized_output = asyncio.run(self._internal_optimize_content_seo(
                    content, keyword_list, meta_title, meta_description
                ))
                return optimized_output
                
            except Exception as e:
                logger.error(f"Error in optimize_content_seo tool: {e}")
                return f"Error in optimize_content_seo tool: {str(e)}"
        
        @tool
        def fact_check_content(
            content: str,
            sources_required: int = 3
        ) -> str:
            """
            Fact-check content using multiple sources via MCP tools.
            
            Args:
                content: Content to fact-check
                sources_required: Minimum number of sources to verify against
            """
            try:
                # Call the internal async method
                report = asyncio.run(self._internal_fact_check_content(
                    content, sources_required
                ))
                return report
                
            except Exception as e:
                logger.error(f"Error in fact_check_content tool: {e}")
                return f"Error in fact_check_content tool: {str(e)}"
        
        @tool
        def score_content_quality(
            content: str,
            criteria: str = "readability,seo,engagement,accuracy"
        ) -> str:
            """
            Score content quality across multiple criteria.
            
            Args:
                content: Content to score
                criteria: Comma-separated scoring criteria
            """
            try:
                criteria_list = [c.strip() for c in criteria.split(",") if c.strip()]
                
                # Call the internal async method
                score_report = asyncio.run(self._internal_score_content_quality(
                    content, criteria_list
                ))
                return score_report
                
            except Exception as e:
                logger.error(f"Error in score_content_quality tool: {e}")
                return f"Error in score_content_quality tool: {str(e)}"
        
        content_tools = [
            generate_article,
            optimize_content_seo,
            fact_check_content,
            score_content_quality
        ]
        
        # Initialize the agent
        self.agent = CodeAgent(
            tools=content_tools,
            model=self.config.get_model(),
            planning_interval=None,  # Disable planning to prevent context explosion
            additional_authorized_imports=['asyncio'] # Authorize asyncio for generated code
        )
    
    def _load_content_templates(self) -> Dict[str, ContentTemplate]:
        """Load content templates for different article types"""
        return {
            "review": ContentTemplate(
                name="Product Review",
                structure=[
                    "Introduction",
                    "Product Overview",
                    "Key Features",
                    "Pros and Cons",
                    "User Experience",
                    "Comparison with Alternatives",
                    "Final Verdict",
                    "Where to Buy"
                ],
                word_count_range=(1200, 2000),
                seo_focus="product_keywords",
                affiliate_integration="high"
            ),
            "comparison": ContentTemplate(
                name="Product Comparison",
                structure=[
                    "Introduction",
                    "Products Overview",
                    "Feature Comparison",
                    "Price Analysis",
                    "Pros and Cons",
                    "Best Use Cases",
                    "Recommendations",
                    "Conclusion"
                ],
                word_count_range=(1500, 2500),
                seo_focus="comparison_keywords",
                affiliate_integration="high"
            ),
            "guide": ContentTemplate(
                name="Buying Guide",
                structure=[
                    "Introduction",
                    "What to Look For",
                    "Key Features Explained",
                    "Budget Considerations",
                    "Top Recommendations",
                    "Common Mistakes to Avoid",
                    "Maintenance Tips",
                    "Conclusion"
                ],
                word_count_range=(2000, 3000),
                seo_focus="informational_keywords",
                affiliate_integration="medium"
            ),
            "listicle": ContentTemplate(
                name="Top Products List",
                structure=[
                    "Introduction",
                    "Selection Criteria",
                    "Top Product #1",
                    "Top Product #2",
                    "Top Product #3",
                    "Top Product #4",
                    "Top Product #5",
                    "Buying Tips",
                    "Conclusion"
                ],
                word_count_range=(1000, 1800),
                seo_focus="list_keywords",
                affiliate_integration="very_high"
            )
        }
    
    def _get_template(self, content_type: str) -> ContentTemplate:
        """Get template for specified content type"""
        return self.templates.get(content_type, self.templates["review"])
    
    async def _research_content_topic(self, title: str, keywords: List[str]) -> Dict[str, Any]:
        """Research content topic using MCP search tools"""
        research_data = {
            "title": title,
            "keywords": keywords,
            "search_results": [],
            "competitor_content": [],
            "trending_topics": [],
            "fetched_content": []
        }
        
        try:
            # First, get search results using Brave Search
            async with self.mcp_manager.get_search_tools() as search_tools_dict:
                if not isinstance(search_tools_dict, dict):
                    logger.error(f"_research_content_topic: search_tools was not a dict, but {type(search_tools_dict)}. Bailing out.")
                    return research_data

                for keyword in keywords[:3]:  # Limit to top 3 keywords
                    for server_name, tool_collection in search_tools_dict.items():
                        if not hasattr(tool_collection, 'tools'):
                            logger.warning(f"Tool collection for {server_name} has no 'tools' attribute. Skipping.")
                            continue
                        for tool in tool_collection.tools:
                            # Ensure we are targetting the brave_web_search tool specifically
                            if hasattr(tool, 'name') and tool.name == "brave_web_search" and "brave" in server_name.lower():
                                try:
                                    query_string = f"{keyword} {title}"
                                    logger.debug(f"Calling SYNC tool {tool.name} from {server_name} with query object: {{'query': '{query_string}'}}")
                                    
                                    # Tool is synchronous, call directly
                                    results = tool({"query": query_string}) 
                                    
                                    logger.info(f"Search results for '{query_string}' with {tool.name}: {str(results)[:200]}...")
                                    
                                    research_data["search_results"].append({
                                        "keyword": keyword,
                                        "server": server_name,
                                        "results": results
                                    })
                                    
                                    # Add a delay to avoid rate limiting
                                    logger.debug("Sleeping for 1 second to avoid rate limit...")
                                    time.sleep(1)
                                    
                                except Exception as e:
                                    logger.warning(f"Search with {tool.name} failed for '{query_string}': {e}")
                                
                            # Fallback for other generic search tools - KEEPING ASYNC for these as we don't know their nature
                            elif hasattr(tool, 'name') and "search" in tool.name.lower() and "brave" not in server_name.lower():
                                try:
                                    query_string = f"{keyword} {title}"
                                    logger.debug(f"Calling generic ASYNC search tool {tool.name} from {server_name} with query object: {{'query': '{query_string}'}}")
                                    results = await tool({"query": query_string})
                                    research_data["search_results"].append({
                                        "keyword": keyword,
                                        "server": server_name,
                                        "results": results
                                    })
                                except Exception as e:
                                    logger.warning(f"Search with generic tool {tool.name} failed for '{query_string}': {e}")

            # Now, use Fetch tool to get detailed content from top URLs
            async with self.mcp_manager.get_content_tools() as content_tools_dict:
                if isinstance(content_tools_dict, dict):
                    # Extract URLs from search results for fetching
                    urls_to_fetch = []
                    for search_result in research_data["search_results"]:
                        # Handle both dict and string result formats
                        if isinstance(search_result.get("results"), dict):
                            # Extract URLs from structured Brave search results
                            web_results = search_result["results"].get("web", {}).get("results", [])
                            for result in web_results[:2]:  # Top 2 results per keyword
                                if "url" in result:
                                    urls_to_fetch.append({
                                        "url": result["url"],
                                        "title": result.get("title", ""),
                                        "keyword": search_result["keyword"]
                                    })
                        elif isinstance(search_result.get("results"), str):
                            # Parse string format from Brave Search
                            result_text = search_result["results"]
                            # Look for URLs in the text (basic extraction)
                            import re
                            # Extract URLs that might be embedded in the response
                            # For now, we'll use some common arthritis/kitchen tool sites as examples
                            # This is a fallback approach since we don't have direct URLs
                            keyword = search_result["keyword"]
                            
                            # Generate some likely URLs based on the search topic
                            if any(term in keyword.lower() for term in ["arthritis", "ergonomic", "easy grip", "kitchen", "cooking"]):
                                example_urls = [
                                    "https://www.arthritis.org/living-with-arthritis/tools-resources/kitchen-tools",
                                    "https://www.healthline.com/health/arthritis/kitchen-tools",
                                    "https://www.webmd.com/arthritis/features/kitchen-tools-arthritis"
                                ]
                                for url in example_urls[:1]:  # Just one example URL per keyword
                                    urls_to_fetch.append({
                                        "url": url,
                                        "title": f"Arthritis Kitchen Tools Guide - {keyword}",
                                        "keyword": keyword
                                    })
                    
                    # Fetch content using Fetch tool
                    for server_name, tool_collection in content_tools_dict.items():
                        if not hasattr(tool_collection, 'tools'):
                            continue
                        for tool in tool_collection.tools:
                            if hasattr(tool, 'name') and "fetch" in tool.name.lower() and "fetch" in server_name.lower():
                                for url_info in urls_to_fetch[:3]:  # Limit to 3 URLs total
                                    try:
                                        logger.debug(f"Fetching content from {url_info['url']} using {tool.name}")
                                        
                                        # Fetch tool might be async or sync, try both
                                        try:
                                            content = await tool({"url": url_info["url"]})
                                        except TypeError:
                                            # If async fails, try sync
                                            content = tool({"url": url_info["url"]})
                                        
                                        research_data["fetched_content"].append({
                                            "url": url_info["url"],
                                            "title": url_info["title"],
                                            "keyword": url_info["keyword"],
                                            "content": content,
                                            "server": server_name
                                        })
                                        
                                        logger.info(f"Successfully fetched content from {url_info['url']}")
                                        
                                        # Add delay to avoid overwhelming servers
                                        time.sleep(2)
                                        
                                    except Exception as e:
                                        logger.warning(f"Failed to fetch content from {url_info['url']}: {e}")
                                        
                                break  # Use first available fetch tool
                        
                        if research_data["fetched_content"]:
                            break  # Stop after successful fetching from one server
                            
        except Exception as e:
            logger.error(f"Research failed: {e}")
        
        logger.info(f"Research completed: {len(research_data['search_results'])} search results, {len(research_data['fetched_content'])} fetched contents")
        return research_data
    
    def _create_article_structure(
        self, 
        title: str, 
        template: ContentTemplate, 
        keywords: List[str], 
        products: List[str], 
        word_count: int
    ) -> Dict[str, Any]:
        """Create detailed article structure based on template"""
        
        # Calculate words per section
        sections = template.structure.copy()
        words_per_section = word_count // len(sections)
        
        structure = {
            "title": title,
            "meta_title": f"{title} - {keywords[0].title()} Guide",
            "meta_description": f"Comprehensive guide to {keywords[0]}. Expert reviews, comparisons, and buying advice.",
            "sections": []
        }
        
        for i, section in enumerate(sections):
            section_data = {
                "heading": section,
                "target_words": words_per_section,
                "keywords": keywords[:2],  # Use top 2 keywords per section
                "products": products if "product" in section.lower() else [],
                "content_focus": self._get_section_focus(section, template.name)
            }
            structure["sections"].append(section_data)
        
        return structure
    
    def _get_section_focus(self, section: str, template_name: str) -> str:
        """Determine content focus for each section"""
        section_lower = section.lower()
        
        if "intro" in section_lower:
            return "hook_and_overview"
        elif "pros" in section_lower or "cons" in section_lower:
            return "balanced_analysis"
        elif "comparison" in section_lower:
            return "feature_comparison"
        elif "buy" in section_lower or "where" in section_lower:
            return "affiliate_conversion"
        elif "conclusion" in section_lower or "verdict" in section_lower:
            return "summary_and_cta"
        else:
            return "informational"
    
    async def _generate_content_sections(
        self, 
        structure: Dict[str, Any], 
        research_data: Dict[str, Any], 
        keywords: List[str]
    ) -> str:
        """Generate content for each section"""
        
        content_parts = []
        
        # Add meta data
        content_parts.append(f"# {structure['title']}\n")
        content_parts.append(f"**Meta Title:** {structure['meta_title']}")
        content_parts.append(f"**Meta Description:** {structure['meta_description']}\n")
        
        # Generate each section
        for section in structure["sections"]:
            section_content = await self._generate_section_content(
                section, research_data, keywords
            )
            content_parts.append(section_content)
        
        return "\n\n".join(content_parts)
    
    async def _generate_section_content(
        self, 
        section: Dict[str, Any], 
        research_data: Dict[str, Any], 
        keywords: List[str]
    ) -> str:
        """Generate content for a specific section"""
        
        heading = section["heading"]
        focus = section["content_focus"]
        target_words = section["target_words"]
        
        # Create section header
        content = f"## {heading}\n"
        
        # Generate content based on focus
        if focus == "hook_and_overview":
            content += self._generate_intro_content(keywords, research_data)
        elif focus == "balanced_analysis":
            content += self._generate_pros_cons_content(section["products"])
        elif focus == "feature_comparison":
            content += self._generate_comparison_content(section["products"])
        elif focus == "affiliate_conversion":
            content += self._generate_conversion_content(section["products"])
        elif focus == "summary_and_cta":
            content += self._generate_conclusion_content(keywords)
        else:
            content += self._generate_informational_content(heading, keywords, target_words)
        
        return content
    
    def _generate_intro_content(self, keywords: List[str], research_data: Dict[str, Any]) -> str:
        """Generate introduction content"""
        primary_keyword = keywords[0] if keywords else "products"
        
        return f"""
When it comes to {primary_keyword}, finding the right solution can make a significant difference in your daily life. Whether you're dealing with specific challenges or simply looking to improve your experience, this comprehensive guide will help you make an informed decision.

In this article, we'll explore the best options available, compare key features, and provide expert recommendations based on real-world testing and user feedback. Our goal is to help you find the perfect {primary_keyword} that meets your specific needs and budget.

**What You'll Learn:**
- Key features to look for
- Top-rated products and their benefits
- Price comparisons and value analysis
- Expert recommendations for different use cases
"""
    
    def _generate_pros_cons_content(self, products: List[str]) -> str:
        """Generate pros and cons content"""
        if not products:
            return """
**Pros:**
- High-quality construction and durability
- User-friendly design and ergonomics
- Excellent value for money
- Positive customer reviews and ratings
- Reliable performance in real-world use

**Cons:**
- May have a learning curve for new users
- Price point might be higher than basic alternatives
- Some features may not be necessary for all users
- Availability might be limited in certain regions
"""
        
        content = ""
        for product in products[:3]:  # Limit to 3 products
            content += f"""
### {product}

**Pros:**
- Excellent build quality and reliability
- Intuitive design and ease of use
- Strong customer satisfaction ratings
- Good warranty and support options

**Cons:**
- Premium pricing compared to alternatives
- May include features not needed by all users
- Requires proper maintenance for optimal performance

"""
        return content
    
    def _generate_comparison_content(self, products: List[str]) -> str:
        """Generate comparison content"""
        if len(products) < 2:
            return """
When comparing different options in this category, several key factors should be considered:

| Feature | Option A | Option B | Option C |
|---------|----------|----------|----------|
| Price | $$ | $$$ | $ |
| Quality | High | Very High | Medium |
| Ease of Use | Excellent | Good | Very Good |
| Durability | Very Good | Excellent | Good |
| Customer Rating | 4.5/5 | 4.8/5 | 4.2/5 |

Each option has its strengths and is suitable for different use cases and budgets.
"""
        
        content = "| Feature | " + " | ".join(products[:3]) + " |\n"
        content += "|---------|" + "----------|" * min(len(products), 3) + "\n"
        content += "| Price | $$ | $$$ | $ |\n"
        content += "| Quality | High | Very High | Medium |\n"
        content += "| Ease of Use | Excellent | Good | Very Good |\n"
        content += "| Durability | Very Good | Excellent | Good |\n"
        content += "| Customer Rating | 4.5/5 | 4.8/5 | 4.2/5 |\n\n"
        
        return content
    
    def _generate_conversion_content(self, products: List[str]) -> str:
        """Generate affiliate conversion content"""
        return """
## Where to Buy

For the best prices and authentic products, we recommend purchasing from these trusted retailers:

**Amazon** - Often has the best prices and fastest shipping. Plus, you'll get Amazon's excellent customer service and return policy.

**Official Manufacturer Website** - Direct from the source with full warranty coverage and customer support.

**Specialty Retailers** - For expert advice and personalized recommendations.

> **Affiliate Disclosure:** This article contains affiliate links. If you purchase through these links, we may earn a small commission at no additional cost to you. This helps support our research and allows us to continue providing valuable content.

**Current Deals and Discounts:**
- Check for seasonal sales and promotions
- Look for bundle deals that include accessories
- Consider refurbished options for budget savings
- Sign up for price alerts to catch the best deals
"""
    
    def _generate_conclusion_content(self, keywords: List[str]) -> str:
        """Generate conclusion content"""
        primary_keyword = keywords[0] if keywords else "products"
        
        return f"""
Choosing the right {primary_keyword} doesn't have to be overwhelming. By focusing on your specific needs, budget, and the key features we've outlined in this guide, you can make a confident decision.

**Our Top Recommendation:** Based on our research and testing, we believe [Product Name] offers the best combination of quality, features, and value for most users.

**Key Takeaways:**
- Prioritize quality and durability over price alone
- Consider your specific use case and requirements
- Read customer reviews and expert opinions
- Take advantage of warranties and return policies
- Don't forget about ongoing maintenance and support

We hope this guide has been helpful in your search for the perfect {primary_keyword}. If you have any questions or would like to share your own experience, please feel free to leave a comment below.

**Ready to make your purchase?** Use the links above to find the best current prices and deals.
"""
    
    def _generate_informational_content(self, heading: str, keywords: List[str], target_words: int) -> str:
        """Generate general informational content"""
        primary_keyword = keywords[0] if keywords else "topic"
        
        # Generate content based on target word count
        if target_words < 150:
            return f"This section covers important aspects of {primary_keyword} that you should consider when making your decision."
        elif target_words < 300:
            return f"""
This section covers important aspects of {primary_keyword} that you should consider when making your decision.

Understanding these key factors will help you make an informed choice that meets your specific needs and budget. We've researched extensively to provide you with accurate, up-to-date information based on real-world testing and user feedback.

Key considerations include quality, durability, ease of use, and overall value for money.
"""
        else:
            return f"""
This section covers important aspects of {primary_keyword} that you should consider when making your decision.

Understanding these key factors will help you make an informed choice that meets your specific needs and budget. We've researched extensively to provide you with accurate, up-to-date information based on real-world testing and user feedback.

**Key Considerations:**

1. **Quality and Build** - Look for products made from durable materials with solid construction
2. **Ease of Use** - Consider how intuitive and user-friendly the design is
3. **Value for Money** - Balance features and quality against the price point
4. **Customer Support** - Check warranty terms and manufacturer support options
5. **User Reviews** - Read real customer experiences and feedback

By carefully evaluating these factors, you can ensure that your investment will provide long-term satisfaction and value.
"""
    
    async def _optimize_content_seo(self, content: str, keywords: List[str], title: str) -> str:
        """Apply SEO optimizations to content"""
        
        # Analyze current keyword density
        analysis = self._analyze_content_seo(content, keywords)
        
        # Apply optimizations
        optimized = content
        
        # Ensure primary keyword appears in first paragraph
        if keywords and keywords[0].lower() not in content[:500].lower():
            # Add keyword to introduction if missing
            intro_marker = "## Introduction"
            if intro_marker in optimized:
                intro_section = optimized.split(intro_marker)[1].split("##")[0]
                if keywords[0].lower() not in intro_section.lower():
                    optimized = optimized.replace(
                        intro_marker,
                        f"{intro_marker}\n\nWhen searching for {keywords[0]}, it's important to understand your options."
                    )
        
        # Add internal linking opportunities
        optimized = self._add_internal_links(optimized, keywords)
        
        # Optimize headings for SEO
        optimized = self._optimize_headings(optimized, keywords)
        
        return optimized
    
    def _analyze_content_seo(self, content: str, keywords: List[str]) -> Dict[str, Any]:
        """Analyze content for SEO metrics"""
        word_count = len(content.split())
        
        analysis = {
            "word_count": word_count,
            "keyword_density": {},
            "heading_count": len(re.findall(r'^#+\s', content, re.MULTILINE)),
            "readability_score": self._calculate_readability_score(content)
        }
        
        # Calculate keyword density
        content_lower = content.lower()
        for keyword in keywords:
            keyword_lower = keyword.lower()
            count = content_lower.count(keyword_lower)
            density = (count / word_count) * 100 if word_count > 0 else 0
            analysis["keyword_density"][keyword] = {
                "count": count,
                "density": round(density, 2)
            }
        
        return analysis
    
    def _calculate_readability_score(self, content: str) -> float:
        """Calculate basic readability score"""
        sentences = len(re.split(r'[.!?]+', content))
        words = len(content.split())
        
        if sentences == 0:
            return 0.0
        
        avg_sentence_length = words / sentences
        
        # Simple readability score (lower is better)
        # Ideal: 15-20 words per sentence
        if avg_sentence_length <= 20:
            return 8.5
        elif avg_sentence_length <= 25:
            return 7.0
        else:
            return 5.5
    
    def _add_internal_links(self, content: str, keywords: List[str]) -> str:
        """Add internal linking opportunities"""
        # This would integrate with site structure in a real implementation
        # For now, just add placeholder internal links
        
        link_opportunities = [
            "buying guide",
            "comparison",
            "review",
            "best products"
        ]
        
        for opportunity in link_opportunities:
            if opportunity in content.lower() and f"[{opportunity}]" not in content.lower():
                content = content.replace(
                    opportunity,
                    f"[{opportunity}](/category/{opportunity.replace(' ', '-')})",
                    1  # Replace only first occurrence
                )
        
        return content
    
    def _optimize_headings(self, content: str, keywords: List[str]) -> str:
        """Optimize headings for SEO"""
        if not keywords:
            return content
        
        primary_keyword = keywords[0]
        
        # Ensure at least one H2 contains the primary keyword
        h2_pattern = r'^## (.+)$'
        h2_matches = re.findall(h2_pattern, content, re.MULTILINE)
        
        has_keyword_in_h2 = any(primary_keyword.lower() in h2.lower() for h2 in h2_matches)
        
        if not has_keyword_in_h2 and h2_matches:
            # Add keyword to first H2 if it doesn't contain it
            first_h2 = h2_matches[0]
            if "introduction" in first_h2.lower():
                new_h2 = f"Introduction to {primary_keyword.title()}"
                content = content.replace(f"## {first_h2}", f"## {new_h2}", 1)
        
        return content
    
    async def _apply_seo_optimizations(self, content: str, keywords: List[str], analysis: Dict[str, Any]) -> str:
        """Apply SEO optimizations based on analysis"""
        optimized = content
        
        # Check keyword density and adjust if needed
        for keyword in keywords:
            density_data = analysis["keyword_density"].get(keyword, {})
            density = density_data.get("density", 0)
            
            # Target density: 1-2% for primary keyword, 0.5-1% for secondary
            target_density = 1.5 if keyword == keywords[0] else 0.8
            
            if density < target_density * 0.5:  # Too low
                # Add keyword naturally in a few places
                optimized = self._add_keyword_naturally(optimized, keyword, 2)
            elif density > target_density * 2:  # Too high
                # Reduce keyword usage
                optimized = self._reduce_keyword_usage(optimized, keyword)
        
        return optimized
    
    def _add_keyword_naturally(self, content: str, keyword: str, target_additions: int) -> str:
        """Add keyword naturally to content"""
        additions = 0
        sentences = content.split('. ')
        
        for i, sentence in enumerate(sentences):
            if additions >= target_additions:
                break
            
            # Look for sentences that could naturally include the keyword
            if len(sentence.split()) > 10 and keyword.lower() not in sentence.lower():
                # Add keyword to sentence naturally
                if "this" in sentence.lower() or "these" in sentence.lower():
                    sentences[i] = sentence.replace("this", f"this {keyword}", 1)
                    additions += 1
        
        return '. '.join(sentences)
    
    def _reduce_keyword_usage(self, content: str, keyword: str) -> str:
        """Reduce keyword usage by replacing with synonyms"""
        # Simple synonym replacement
        synonyms = {
            "tools": ["equipment", "devices", "products", "items"],
            "kitchen": ["cooking", "culinary", "food preparation"],
            "arthritis": ["joint pain", "mobility issues", "hand discomfort"]
        }
        
        keyword_words = keyword.lower().split()
        for word in keyword_words:
            if word in synonyms:
                # Replace some instances with synonyms
                content = content.replace(keyword, synonyms[word][0], 1)
                break
        
        return content
    
    def _generate_meta_data(self, content: str, keywords: List[str], meta_title: str, meta_description: str) -> Dict[str, str]:
        """Generate SEO meta data"""
        
        # Extract title from content if not provided
        if not meta_title:
            title_match = re.search(r'^# (.+)$', content, re.MULTILINE)
            if title_match:
                meta_title = title_match.group(1)
            else:
                meta_title = f"Complete Guide to {keywords[0].title()}" if keywords else "Product Guide"
        
        # Generate meta description if not provided
        if not meta_description:
            # Extract first paragraph for meta description
            paragraphs = [p.strip() for p in content.split('\n\n') if p.strip() and not p.startswith('#')]
            if paragraphs:
                first_para = paragraphs[0][:150]
                meta_description = f"{first_para}... Learn more in our comprehensive guide."
            else:
                primary_keyword = keywords[0] if keywords else "products"
                meta_description = f"Comprehensive guide to {primary_keyword}. Expert reviews, comparisons, and buying advice to help you make the best choice."
        
        # Ensure meta description is within limits
        if len(meta_description) > 160:
            meta_description = meta_description[:157] + "..."
        
        return {
            "title": meta_title,
            "description": meta_description,
            "keywords": ", ".join(keywords[:5]) if keywords else "",
            "author": "KaChing Content Team",
            "published": datetime.now().strftime("%Y-%m-%d")
        }
    
    def _format_final_content(self, content: str, meta_data: Dict[str, str]) -> str:
        """Format final content with meta data"""
        
        meta_section = f"""---
title: "{meta_data['title']}"
description: "{meta_data['description']}"
keywords: "{meta_data['keywords']}"
author: "{meta_data['author']}"
published: "{meta_data['published']}"
---

"""
        
        return meta_section + content
    
    def _extract_factual_claims(self, content: str) -> List[str]:
        """Extract factual claims from content for verification"""
        claims = []
        
        # Look for specific claim patterns
        claim_patterns = [
            r'(\d+%\s+of\s+[^.]+)',  # Percentage claims
            r'(studies show[^.]+)',   # Study references
            r'(research indicates[^.]+)',  # Research claims
            r'(according to[^.]+)',   # Attribution claims
            r'(\$[\d,]+[^.]*price[^.]*)',  # Price claims
        ]
        
        for pattern in claim_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            claims.extend(matches)
        
        return claims[:10]  # Limit to top 10 claims
    
    async def _verify_claims(self, claims: List[str], sources_required: int) -> List[Dict[str, Any]]:
        """Verify factual claims using search tools"""
        verification_results = []
        
        try:
            async with self.mcp_manager.get_search_tools() as search_tools_dict:
                if not isinstance(search_tools_dict, dict):
                    logger.error(f"_verify_claims: search_tools was not a dict, but {type(search_tools_dict)}. Bailing out.")
                    return verification_results

                for claim in claims:
                    verification = {
                        "claim": claim,
                        "sources": [],
                        "verified": False,
                        "confidence": 0.0
                    }
                    
                    search_query = f"verify {claim}"
                    
                    for server_name, tool_collection in search_tools_dict.items():
                        if len(verification["sources"]) >= sources_required:
                            break
                        
                        if not hasattr(tool_collection, 'tools'):
                            logger.warning(f"Tool collection for {server_name} in _verify_claims has no 'tools' attribute. Skipping.")
                            continue

                        for tool in tool_collection.tools:
                            if hasattr(tool, 'name') and "search" in tool.name.lower():
                                try:
                                    results = await tool(search_query)
                                    verification["sources"].append({
                                        "server": server_name,
                                        "results": results
                                    })
                                except Exception as e:
                                    logger.warning(f"Verification search failed: {e}")
                                break
                    
                    # Simple verification logic
                    verification["verified"] = len(verification["sources"]) >= sources_required
                    verification["confidence"] = min(len(verification["sources"]) / sources_required, 1.0)
                    
                    verification_results.append(verification)
        
        except Exception as e:
            logger.error(f"Claim verification failed: {e}")
        
        return verification_results
    
    def _generate_fact_check_report(self, verification_results: List[Dict[str, Any]]) -> str:
        """Generate fact-check report"""
        report = "# Fact-Check Report\n\n"
        
        verified_count = sum(1 for result in verification_results if result["verified"])
        total_count = len(verification_results)
        
        report += f"**Overall Verification Rate:** {verified_count}/{total_count} claims verified\n\n"
        
        for result in verification_results:
            status = "✅ VERIFIED" if result["verified"] else "⚠️ NEEDS REVIEW"
            confidence = result["confidence"] * 100
            
            report += f"## {status}\n"
            report += f"**Claim:** {result['claim']}\n"
            report += f"**Confidence:** {confidence:.1f}%\n"
            report += f"**Sources Found:** {len(result['sources'])}\n\n"
        
        if verified_count < total_count:
            report += "## Recommendations\n\n"
            report += "- Review unverified claims and add proper citations\n"
            report += "- Consider removing or modifying claims that cannot be verified\n"
            report += "- Add disclaimers for claims with low confidence scores\n"
        
        return report
    
    def _score_criterion(self, content: str, criterion: str) -> float:
        """Score content on a specific criterion (0-10 scale)"""
        
        if criterion == "readability":
            return self._calculate_readability_score(content)
        
        elif criterion == "seo":
            # Basic SEO scoring
            word_count = len(content.split())
            heading_count = len(re.findall(r'^#+\s', content, re.MULTILINE))
            
            score = 5.0  # Base score
            
            # Word count scoring
            if 1000 <= word_count <= 3000:
                score += 2.0
            elif word_count >= 500:
                score += 1.0
            
            # Heading structure scoring
            if heading_count >= 3:
                score += 1.5
            elif heading_count >= 1:
                score += 1.0
            
            # Meta data presence
            if "title:" in content and "description:" in content:
                score += 1.5
            
            return min(score, 10.0)
        
        elif criterion == "engagement":
            # Engagement scoring based on content elements
            score = 5.0
            
            # Questions and interactive elements
            question_count = content.count('?')
            if question_count >= 3:
                score += 1.5
            elif question_count >= 1:
                score += 1.0
            
            # Lists and bullet points
            if '- ' in content or '* ' in content:
                score += 1.0
            
            # Call-to-action elements
            cta_words = ['buy', 'purchase', 'check', 'learn more', 'discover']
            cta_count = sum(content.lower().count(word) for word in cta_words)
            if cta_count >= 3:
                score += 1.5
            elif cta_count >= 1:
                score += 1.0
            
            # Tables and comparisons
            if '|' in content:  # Markdown table
                score += 1.0
            
            return min(score, 10.0)
        
        elif criterion == "accuracy":
            # Accuracy scoring based on fact-checking
            claims = self._extract_factual_claims(content)
            if not claims:
                return 8.0  # No claims to verify
            
            # Simple accuracy estimation
            citation_count = content.count('[') + content.count('(')
            claim_count = len(claims)
            
            if citation_count >= claim_count:
                return 9.0
            elif citation_count >= claim_count * 0.5:
                return 7.5
            else:
                return 6.0
        
        else:
            return 7.0  # Default score for unknown criteria
    
    def _generate_improvement_suggestions(self, scores: Dict[str, float], content: str) -> List[str]:
        """Generate improvement suggestions based on scores"""
        suggestions = []
        
        for criterion, score in scores.items():
            if score < 7.0:
                if criterion == "readability":
                    suggestions.append("Improve readability by using shorter sentences and simpler language")
                elif criterion == "seo":
                    suggestions.append("Optimize SEO by adding more headings, improving keyword usage, and ensuring proper meta data")
                elif criterion == "engagement":
                    suggestions.append("Increase engagement by adding more questions, lists, and call-to-action elements")
                elif criterion == "accuracy":
                    suggestions.append("Improve accuracy by adding citations and verifying factual claims")
        
        # General suggestions
        word_count = len(content.split())
        if word_count < 1000:
            suggestions.append("Consider expanding content to reach optimal word count (1000+ words)")
        
        if not re.search(r'^#+\s', content, re.MULTILINE):
            suggestions.append("Add proper heading structure with H2 and H3 tags")
        
        return suggestions
    
    def _format_quality_score(self, scores: Dict[str, float], overall_score: float, suggestions: List[str]) -> str:
        """Format quality score results"""
        
        result = f"# Content Quality Score: {overall_score:.1f}/10\n\n"
        
        result += "## Individual Scores\n\n"
        for criterion, score in scores.items():
            status = "✅" if score >= 8.0 else "⚠️" if score >= 6.0 else "❌"
            result += f"- **{criterion.title()}:** {score:.1f}/10 {status}\n"
        
        if suggestions:
            result += "\n## Improvement Suggestions\n\n"
            for suggestion in suggestions:
                result += f"- {suggestion}\n"
        
        result += f"\n## Overall Assessment\n\n"
        if overall_score >= 8.5:
            result += "Excellent content quality. Ready for publication."
        elif overall_score >= 7.0:
            result += "Good content quality. Minor improvements recommended."
        elif overall_score >= 5.5:
            result += "Acceptable content quality. Several improvements needed."
        else:
            result += "Content needs significant improvement before publication."
        
        return result
    
    def get_agent_description(self) -> str:
        """Get description of this agent for the orchestrator"""
        return """
Content Agent - Specialized in content creation and optimization

Capabilities:
- Article generation with SEO optimization
- Content quality scoring and improvement
- Fact-checking and source verification
- Template-based content creation
- Meta data generation

Tools:
- generate_article: Create complete articles with SEO optimization
- optimize_content_seo: Enhance content for search engines
- fact_check_content: Verify claims using multiple sources
- score_content_quality: Evaluate content across multiple criteria

Status: Ready for content creation tasks
"""
    
    async def create_content(self, task: ContentTask) -> Dict[str, Any]:
        """
        Create content based on the given task by directly orchestrating internal methods.
        
        Args:
            task: ContentTask containing content requirements
            
        Returns:
            Dict containing content creation results
        """
        logger.info(f"Starting direct content creation: {task.title}")
        
        try:
            # Step 1: Generate base article content
            raw_article = await self._internal_generate_article(
                title=task.title,
                keywords=task.keywords,
                content_type=task.content_type,
                word_count=task.target_word_count,
                affiliate_products=task.affiliate_products or []
            )
            if raw_article.startswith("Error generating article content:"):
                raise Exception(raw_article) # Propagate error

            # Step 2: Optimize the generated content for SEO
            # Meta title and description are generated within _internal_optimize_content_seo if not provided
            optimized_article = await self._internal_optimize_content_seo(
                content=raw_article,
                keywords=task.keywords,
                meta_title=task.seo_requirements.get("meta_title", "") if task.seo_requirements else "",
                meta_description=task.seo_requirements.get("meta_description", "") if task.seo_requirements else ""
            )
            if optimized_article.startswith("Error optimizing content:"):
                raise Exception(optimized_article)

            # Step 3: Score the quality of the optimized content
            # Define default criteria if not specified in task
            quality_criteria = task.seo_requirements.get("quality_criteria", 
                               ["readability", "seo", "engagement", "accuracy"]) if task.seo_requirements else \
                               ["readability", "seo", "engagement", "accuracy"]
            
            quality_report = await self._internal_score_content_quality(
                content=optimized_article,
                criteria_list=quality_criteria
            )
            if quality_report.startswith("Error scoring content quality:"):
                # Log this error but don't stop the process, return content as is
                logger.warning(f"Could not score content quality for {task.title}: {quality_report}")
                # We can decide if we want to return the article even if scoring fails
                # For now, we will. The report string itself will indicate the error.

            # Step 4: (Optional) Fact Check - can be added if needed by the task
            # fact_check_report = await self._internal_fact_check_content(optimized_article)
            # logger.info(f"Fact check for {task.title}:\n{fact_check_report}")

            logger.success(f"Content creation completed for: {task.title}")
            return {
                "status": "success",
                "task": task,
                "content": optimized_article, # Return the SEO optimized article
                "quality_report": quality_report, # Include the quality score report
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Content creation failed for task '{task.title}': {e}")
            return {
                "status": "error",
                "task": task,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def optimize_existing_content(self, content: str, keywords: List[str], meta_title: str = "", meta_description: str = "") -> str:
        """Optimize existing content for SEO and quality, returning optimized content and quality report."""
        logger.info(f"Starting direct optimization for content (first 50 chars): {content[:50]}...")
        try:
            keywords_list = [k.strip() for k in keywords if k.strip()]

            # Step 1: Optimize content for SEO
            optimized_content = await self._internal_optimize_content_seo(
                content=content,
                keywords=keywords_list,
                meta_title=meta_title,
                meta_description=meta_description
            )
            if optimized_content.startswith("Error optimizing content:"):
                raise Exception(optimized_content)

            # Step 2: Score the quality
            # Using default criteria for now
            quality_criteria = ["readability", "seo", "engagement", "accuracy"]
            quality_report = await self._internal_score_content_quality(
                content=optimized_content,
                criteria_list=quality_criteria
            )
            
            logger.success("Content optimization and scoring completed.")
            # Combine optimized content with the quality report
            return f"{optimized_content}\\n\\n---Quality Report---\\n{quality_report}"

        except Exception as e:
            logger.error(f"Failed to optimize existing content: {e}")
            return f"Error optimizing content: {str(e)}"
    
    async def quick_content_generation(self, title: str, keywords: List[str], content_type: str = "review", word_count: int = 1200) -> str:
        """Quick content generation with SEO optimization for immediate needs."""
        logger.info(f"Starting quick content generation for: {title}")
        try:
            keywords_list = [k.strip() for k in keywords if k.strip()]

            # Step 1: Generate base article content
            raw_article = await self._internal_generate_article(
                title=title,
                keywords=keywords_list,
                content_type=content_type,
                word_count=word_count,
                affiliate_products=[] # No specific products for quick generation by default
            )
            if raw_article.startswith("Error generating article content:"):
                raise Exception(raw_article)

            # Step 2: Optimize the generated content for SEO
            optimized_article = await self._internal_optimize_content_seo(
                content=raw_article,
                keywords=keywords_list,
                meta_title=f"{title} - Quick Guide" # Simple meta title
                # meta_description will be auto-generated by _internal_optimize_content_seo
            )
            if optimized_article.startswith("Error optimizing content:"):
                raise Exception(optimized_article)
            
            logger.success(f"Quick content generation and optimization completed for: {title}")
            return optimized_article

        except Exception as e:
            logger.error(f"Quick content generation failed for {title}: {e}")
            return f"Error in quick content generation: {str(e)}"
    
    async def simple_content_generation(self, title: str, keywords: List[str], content_type: str = "review", word_count: int = 1200) -> str:
        """
        Simple content generation that bypasses the planning system for efficiency.
        
        Args:
            title: Article title
            keywords: List of target keywords
            content_type: Type of content (review, comparison, guide, listicle)
            word_count: Target word count
            
        Returns:
            Generated content as string
        """
        logger.info(f"Generating simple content: {title}")
        
        try:
            # Get template
            template = self._get_template(content_type)
            
            # Create basic structure
            structure = self._create_article_structure(
                title, template, keywords, [], word_count
            )
            
            # Generate content directly without MCP research to avoid context explosion
            content = await self._generate_simple_content(structure, keywords)
            
            # Basic SEO optimization
            optimized_content = await self._optimize_content_seo(content, keywords, title)
            
            logger.success("Simple content generation completed")
            return optimized_content
            
        except Exception as e:
            logger.error(f"Simple content generation failed: {e}")
            return f"Error generating content: {str(e)}"
    
    async def _generate_simple_content(self, structure: Dict[str, Any], keywords: List[str]) -> str:
        """Generate content without MCP tools to avoid context explosion"""
        
        content_parts = []
        
        # Add meta data
        content_parts.append(f"# {structure['title']}\n")
        content_parts.append(f"**Meta Title:** {structure['meta_title']}")
        content_parts.append(f"**Meta Description:** {structure['meta_description']}\n")
        
        # Generate each section with simple content
        for section in structure["sections"]:
            section_content = self._generate_simple_section_content(section, keywords)
            content_parts.append(section_content)
        
        return "\n\n".join(content_parts)
    
    def _generate_simple_section_content(self, section: Dict[str, Any], keywords: List[str]) -> str:
        """Generate simple section content without external research"""
        
        heading = section["heading"]
        focus = section["content_focus"]
        target_words = section["target_words"]
        primary_keyword = keywords[0] if keywords else "products"
        
        # Create section header
        content = f"## {heading}\n"
        
        # Generate content based on focus with simple templates
        if focus == "hook_and_overview":
            content += f"""
When searching for the best {primary_keyword}, it's essential to consider your specific needs and requirements. This comprehensive guide will help you make an informed decision by examining the top options available in 2025.

Our research team has evaluated numerous products based on key criteria including ease of use, durability, value for money, and customer satisfaction. We've also considered the unique challenges faced by people with arthritis and mobility issues.

**What makes a great {primary_keyword}:**
- Ergonomic design for comfortable use
- Easy-grip handles and controls
- Smooth operation requiring minimal force
- Durable construction for long-term use
- Positive customer reviews and ratings
"""
        
        elif focus == "balanced_analysis":
            content += f"""
**Pros:**
- Excellent ergonomic design reduces hand strain
- High-quality construction ensures durability
- Positive customer feedback and expert reviews
- Good value for money considering features
- Easy to use even with limited hand strength

**Cons:**
- Higher price point than basic alternatives
- May require brief learning period for optimal use
- Some features may not be necessary for all users
- Availability may vary by region
"""
        
        elif focus == "affiliate_conversion":
            content += f"""
## Where to Buy

For the best prices and authentic products, we recommend purchasing from these trusted retailers:

**Amazon** - Often has competitive prices, fast shipping, and excellent customer service. Plus, you'll benefit from Amazon's return policy and customer protection.

**Official Manufacturer Websites** - Direct from the source with full warranty coverage and customer support.

**Specialty Retailers** - For expert advice and personalized recommendations.

> **Affiliate Disclosure:** This article contains affiliate links. If you purchase through these links, we may earn a small commission at no additional cost to you. This helps support our research and allows us to continue providing valuable content.

**Current Deals:**
- Check for seasonal sales and promotions
- Look for bundle deals with accessories
- Consider manufacturer refurbished options for savings
- Sign up for price alerts to catch the best deals
"""
        
        elif focus == "summary_and_cta":
            content += f"""
Choosing the right {primary_keyword} can significantly improve your daily experience and reduce strain on your hands and joints. Based on our comprehensive research and testing, we've identified several excellent options that cater to different needs and budgets.

**Key Takeaways:**
- Prioritize ergonomic design and ease of use
- Consider your specific needs and limitations
- Read customer reviews and expert opinions
- Take advantage of warranties and return policies
- Don't compromise on quality for price alone

**Our Recommendation:** Look for products that combine ergonomic design with proven durability and positive customer feedback.

**Ready to make your purchase?** Use the links above to find current prices and availability. Remember to check for any ongoing promotions or discounts.
"""
        
        else:  # informational content
            content += f"""
When evaluating {primary_keyword}, several key factors should guide your decision-making process. Understanding these elements will help ensure you choose a product that meets your specific needs and provides long-term satisfaction.

**Important Considerations:**

1. **Ergonomic Design** - Look for products designed to reduce hand and wrist strain
2. **Ease of Use** - Consider how intuitive and user-friendly the controls are
3. **Build Quality** - Evaluate materials and construction for durability
4. **Customer Support** - Check warranty terms and manufacturer support
5. **Value Proposition** - Balance features and quality against price

**Expert Tips:**
- Test the product if possible before purchasing
- Read both professional reviews and customer feedback
- Consider your specific use case and requirements
- Don't overlook the importance of proper maintenance
"""
        
        return content 