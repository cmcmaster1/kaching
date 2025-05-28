#!/usr/bin/env python3
"""
Comprehensive Keyword Research Demo for KaChing Project

This script demonstrates using both Research Agent and Content Agent
to find and analyze keywords for the arthritis-friendly kitchen tools niche.
"""

import asyncio
import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import nest_asyncio
nest_asyncio.apply()

from kaching.config import KaChingConfig
from kaching.agents.research_agent import ResearchAgent
from kaching.agents.content_agent import ContentAgent


async def comprehensive_keyword_research():
    """Perform comprehensive keyword research for the arthritis kitchen tools niche"""
    
    print("🔍 KaChing Comprehensive Keyword Research")
    print("=" * 60)
    print("Niche: Arthritis-Friendly Kitchen Tools")
    print("Goal: Find 30+ keywords with KD < 25, volume > 150/month")
    print()
    
    # Initialize configuration and agents
    config = KaChingConfig.from_env()
    research_agent = ResearchAgent(config)
    content_agent = ContentAgent(config)
    
    print("✅ Agents initialized")
    print()
    
    # Phase 1: Seed keyword research
    print("📋 Phase 1: Seed Keyword Research")
    print("-" * 40)
    
    seed_keywords = [
        "arthritis kitchen tools",
        "ergonomic can opener",
        "easy grip kitchen utensils",
        "arthritis friendly knives",
        "ergonomic cooking tools",
        "easy open jar opener",
        "lightweight kitchen tools",
        "non-slip cutting board",
        "ergonomic peeler",
        "arthritis cooking aids"
    ]
    
    print(f"🌱 Seed keywords ({len(seed_keywords)}):")
    for i, keyword in enumerate(seed_keywords, 1):
        print(f"  {i:2d}. {keyword}")
    print()
    
    # Phase 2: Research Agent keyword expansion
    print("📋 Phase 2: Research Agent Keyword Expansion")
    print("-" * 40)
    
    try:
        research_results = await research_agent.quick_keyword_research(seed_keywords[:5])  # Use first 5 seeds
        
        print("✅ Research Agent completed keyword expansion")
        print(f"📊 Research results keys: {list(research_results.keys())}")
        
        # Extract keywords from research results
        expanded_keywords = []
        if 'keyword_opportunities' in research_results:
            for opportunity in research_results['keyword_opportunities']:
                if isinstance(opportunity, dict) and 'keyword' in opportunity:
                    expanded_keywords.append(opportunity['keyword'])
                elif isinstance(opportunity, str):
                    expanded_keywords.append(opportunity)
        
        print(f"🔍 Expanded keywords found: {len(expanded_keywords)}")
        for i, keyword in enumerate(expanded_keywords[:10], 1):  # Show first 10
            print(f"  {i:2d}. {keyword}")
        if len(expanded_keywords) > 10:
            print(f"  ... and {len(expanded_keywords) - 10} more")
        print()
        
    except Exception as e:
        print(f"❌ Research Agent keyword expansion failed: {e}")
        expanded_keywords = []
        print()
    
    # Phase 3: Content research for top keywords
    print("📋 Phase 3: Content Research for Top Keywords")
    print("-" * 40)
    
    # Combine seed and expanded keywords
    all_keywords = seed_keywords + expanded_keywords
    top_keywords = list(set(all_keywords))[:15]  # Remove duplicates, take top 15
    
    print(f"🎯 Analyzing top {len(top_keywords)} keywords for content opportunities:")
    
    content_opportunities = []
    
    for i, keyword in enumerate(top_keywords[:5], 1):  # Analyze first 5 in detail
        print(f"\n  {i}. Analyzing: '{keyword}'")
        
        try:
            # Use Content Agent to research the topic
            research_data = await content_agent._research_content_topic(
                title=f"Best {keyword.title()} Guide",
                keywords=[keyword]
            )
            
            # Analyze the research data
            search_count = len(research_data.get('search_results', []))
            content_count = len(research_data.get('fetched_content', []))
            
            opportunity = {
                'keyword': keyword,
                'search_results': search_count,
                'content_fetched': content_count,
                'competition_level': 'Medium' if search_count > 2 else 'Low',
                'content_potential': 'High' if content_count > 0 else 'Medium'
            }
            
            content_opportunities.append(opportunity)
            
            print(f"     📊 Search results: {search_count}")
            print(f"     📄 Content fetched: {content_count}")
            print(f"     🏆 Competition: {opportunity['competition_level']}")
            print(f"     💡 Content potential: {opportunity['content_potential']}")
            
        except Exception as e:
            print(f"     ❌ Analysis failed: {e}")
    
    print()
    
    # Phase 4: Content type mapping
    print("📋 Phase 4: Content Type Mapping")
    print("-" * 40)
    
    content_types = {
        'review': [],
        'comparison': [],
        'guide': [],
        'listicle': []
    }
    
    # Map keywords to content types based on intent
    for keyword in top_keywords:
        keyword_lower = keyword.lower()
        
        if any(word in keyword_lower for word in ['best', 'top', 'review']):
            content_types['review'].append(keyword)
        elif any(word in keyword_lower for word in ['vs', 'compare', 'comparison']):
            content_types['comparison'].append(keyword)
        elif any(word in keyword_lower for word in ['how to', 'guide', 'tips']):
            content_types['guide'].append(keyword)
        elif any(word in keyword_lower for word in ['tools', 'utensils', 'aids']):
            content_types['listicle'].append(keyword)
        else:
            # Default to review for product-focused keywords
            content_types['review'].append(keyword)
    
    print("🗂️ Content type mapping:")
    for content_type, keywords in content_types.items():
        print(f"  📝 {content_type.title()}: {len(keywords)} keywords")
        for keyword in keywords[:3]:  # Show first 3
            print(f"     - {keyword}")
        if len(keywords) > 3:
            print(f"     ... and {len(keywords) - 3} more")
        print()
    
    # Phase 5: Priority recommendations
    print("📋 Phase 5: Priority Recommendations")
    print("-" * 40)
    
    # Prioritize based on research data
    high_priority = []
    medium_priority = []
    
    for opportunity in content_opportunities:
        if (opportunity['content_potential'] == 'High' and 
            opportunity['competition_level'] in ['Low', 'Medium']):
            high_priority.append(opportunity['keyword'])
        else:
            medium_priority.append(opportunity['keyword'])
    
    # Add remaining keywords to medium priority
    analyzed_keywords = [opp['keyword'] for opp in content_opportunities]
    remaining_keywords = [kw for kw in top_keywords if kw not in analyzed_keywords]
    medium_priority.extend(remaining_keywords)
    
    print("🎯 High Priority Keywords (start here):")
    for i, keyword in enumerate(high_priority, 1):
        print(f"  {i:2d}. {keyword}")
    
    print(f"\n📋 Medium Priority Keywords ({len(medium_priority)} total):")
    for i, keyword in enumerate(medium_priority[:5], 1):  # Show first 5
        print(f"  {i:2d}. {keyword}")
    if len(medium_priority) > 5:
        print(f"  ... and {len(medium_priority) - 5} more")
    
    print()
    
    # Summary
    print("📊 Research Summary")
    print("-" * 40)
    print(f"✅ Total keywords identified: {len(all_keywords)}")
    print(f"🎯 Top keywords analyzed: {len(top_keywords)}")
    print(f"📝 Content opportunities: {len(content_opportunities)}")
    print(f"🏆 High priority keywords: {len(high_priority)}")
    print(f"📋 Medium priority keywords: {len(medium_priority)}")
    print()
    
    print("💡 Next Steps:")
    print("1. Start content creation with high priority keywords")
    print("2. Create content calendar based on keyword mapping")
    print("3. Set up affiliate product research for top keywords")
    print("4. Begin WordPress site setup and configuration")
    print()
    
    return {
        'seed_keywords': seed_keywords,
        'expanded_keywords': expanded_keywords,
        'top_keywords': top_keywords,
        'content_opportunities': content_opportunities,
        'content_types': content_types,
        'high_priority': high_priority,
        'medium_priority': medium_priority
    }


if __name__ == "__main__":
    print("🚀 Starting Comprehensive Keyword Research...")
    results = asyncio.run(comprehensive_keyword_research())
    print("✨ Keyword research completed!") 