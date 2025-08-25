"""
CrewAI Example with Hreflang Tools

This example demonstrates how to create specialized AI agent crews for 
international SEO analysis using langchain-hreflang tools.

CrewAI allows multiple AI agents to collaborate on complex tasks, making it
perfect for comprehensive SEO audits that require different perspectives.

Requirements:
- pip install crewai
- HREFLANG_API_KEY environment variable
- OPENAI_API_KEY environment variable (or other LLM provider)
"""

import os
from crewai import Agent, Task, Crew, Process
from langchain_hreflang import hreflang_tools

def create_seo_crew():
    """Create a crew of AI agents specialized in international SEO analysis."""
    
    # SEO Specialist Agent
    seo_specialist = Agent(
        role="International SEO Specialist",
        goal="Analyze and optimize hreflang implementation for international websites",
        backstory="""You are an expert in international SEO with deep knowledge of 
        hreflang implementation, search engine guidelines, and multilingual website 
        optimization. You understand how to identify issues and provide actionable 
        recommendations for improving international search visibility.""",
        tools=hreflang_tools,
        verbose=True,
        allow_delegation=False
    )
    
    # SEO Auditor Agent
    seo_auditor = Agent(
        role="SEO Technical Auditor", 
        goal="Provide detailed technical analysis and recommendations",
        backstory="""You are a technical SEO auditor who specializes in analyzing 
        the technical implementation of international websites. You can identify 
        complex issues with hreflang implementation and provide specific, 
        actionable recommendations for developers and SEO teams.""",
        tools=hreflang_tools,
        verbose=True,
        allow_delegation=False
    )
    
    return [seo_specialist, seo_auditor]


def analyze_website(website_url: str, sitemap_url: str = None):
    """
    Analyze a website's hreflang implementation.
    
    Args:
        website_url: The main website URL to analyze
        sitemap_url: Optional sitemap URL for comprehensive analysis
    """
    agents = create_seo_crew()
    seo_specialist, seo_auditor = agents
    
    # Task 1: Initial hreflang analysis
    analysis_task = Task(
        description=f"""
        Conduct a comprehensive hreflang analysis for {website_url}.
        
        Your analysis should include:
        1. Test the main website and its language versions
        2. Check account status to understand testing limits
        3. Identify the language versions available
        4. Test key pages for proper hreflang implementation
        
        Focus on finding the main language variations and testing them thoroughly.
        """,
        agent=seo_specialist,
        expected_output="A detailed report on hreflang implementation with specific findings"
    )
    
    # Task 2: Sitemap analysis (if provided)
    if sitemap_url:
        sitemap_task = Task(
            description=f"""
            Perform a comprehensive sitemap analysis for {sitemap_url}.
            
            Your analysis should include:
            1. Test the entire sitemap for hreflang implementation
            2. Analyze language coverage across the site
            3. Identify any widespread issues or patterns
            4. Compare findings with the initial URL analysis
            
            Provide statistics on implementation quality across the entire site.
            """,
            agent=seo_auditor,
            expected_output="A comprehensive sitemap-level hreflang analysis with statistics"
        )
        tasks = [analysis_task, sitemap_task]
    else:
        tasks = [analysis_task]
    
    # Task 3: Recommendations and action plan
    recommendations_task = Task(
        description=f"""
        Based on all previous analysis of {website_url}, create a comprehensive 
        action plan for improving hreflang implementation.
        
        Your recommendations should include:
        1. Priority issues to fix immediately
        2. Technical implementation guidance
        3. Best practices for ongoing maintenance
        4. Expected impact of implementing fixes
        
        Make recommendations specific, actionable, and prioritized by impact.
        """,
        agent=seo_auditor,
        expected_output="A prioritized action plan with specific recommendations",
        context=tasks  # Use results from previous tasks
    )
    
    tasks.append(recommendations_task)
    
    # Create and run the crew
    crew = Crew(
        agents=agents,
        tasks=tasks,
        verbose=True
    )
    
    return crew.kickoff()


def competitive_analysis():
    """Example: Competitive SEO analysis between multiple websites."""
    
    print("🏆 Competitive Hreflang Analysis Example")
    print("=" * 50)
    
    agents = create_seo_crew()
    seo_specialist, seo_auditor = agents
    
    competitors = [
        "https://booking.com",
        "https://expedia.com", 
        "https://airbnb.com"
    ]
    
    # Create analysis tasks for each competitor
    analysis_tasks = []
    for i, competitor in enumerate(competitors):
        task = Task(
            description=f"""
            Analyze the hreflang implementation for {competitor}.
            
            Focus on:
            1. Testing main pages for hreflang tags
            2. Identifying supported languages
            3. Finding implementation strengths and weaknesses
            4. Noting any unique approaches or issues
            
            Store findings for comparison with other competitors.
            """,
            agent=seo_specialist if i % 2 == 0 else seo_auditor,
            expected_output=f"Detailed hreflang analysis for {competitor}"
        )
        analysis_tasks.append(task)
    
    # Competitive comparison task
    comparison_task = Task(
        description=f"""
        Create a comprehensive competitive analysis comparing hreflang 
        implementations across these websites: {', '.join(competitors)}.
        
        Your analysis should include:
        1. Side-by-side comparison of implementation approaches
        2. Best practices identified from leaders
        3. Common issues across competitors  
        4. Recommendations for gaining competitive advantage
        5. Implementation complexity rankings
        
        Provide actionable insights for outperforming competitors.
        """,
        agent=seo_auditor,
        expected_output="Competitive hreflang analysis with strategic recommendations",
        context=analysis_tasks
    )
    
    all_tasks = analysis_tasks + [comparison_task]
    
    # Create crew with sequential process for ordered analysis
    crew = Crew(
        agents=agents,
        tasks=all_tasks,
        process=Process.sequential,
        verbose=True
    )
    
    return crew.kickoff()


def enterprise_audit():
    """Example: Enterprise-level comprehensive SEO audit."""
    
    print("🏢 Enterprise SEO Audit Example")
    print("=" * 50)
    
    # Create specialized enterprise agents
    technical_lead = Agent(
        role="Technical SEO Lead",
        goal="Conduct thorough technical analysis of enterprise websites",
        backstory="""You are a senior technical SEO consultant with 10+ years 
        of experience auditing enterprise websites. You understand complex 
        technical implementations and can provide strategic recommendations 
        for large-scale international websites.""",
        tools=hreflang_tools,
        verbose=True
    )
    
    seo_manager = Agent(
        role="SEO Strategy Manager", 
        goal="Translate technical findings into business impact and strategy",
        backstory="""You are an SEO strategy manager who excels at translating 
        technical SEO findings into business language and creating actionable 
        strategic plans. You understand ROI, prioritization, and resource 
        allocation for SEO initiatives.""",
        tools=hreflang_tools,
        verbose=True
    )
    
    # Multi-phase audit tasks
    discovery_task = Task(
        description="""
        Conduct discovery phase for enterprise SEO audit:
        
        1. Check account limits and capabilities
        2. Perform initial hreflang analysis on main pages
        3. Identify the scope of international presence
        4. Document current implementation approach
        5. Assess technical complexity level
        
        This is the foundation for the comprehensive audit.
        """,
        agent=technical_lead,
        expected_output="Discovery phase report with technical baseline"
    )
    
    deep_analysis_task = Task(
        description="""
        Conduct deep technical analysis phase:
        
        1. Perform comprehensive sitemap analysis if available
        2. Test multiple language versions and regional sites
        3. Identify patterns in implementation issues
        4. Document technical debt and maintenance needs
        5. Assess scalability of current implementation
        
        Focus on enterprise-scale concerns and technical architecture.
        """,
        agent=technical_lead,
        expected_output="Comprehensive technical analysis with detailed findings",
        context=[discovery_task]
    )
    
    strategy_task = Task(
        description="""
        Create strategic recommendations and implementation roadmap:
        
        1. Prioritize findings by business impact
        2. Estimate resource requirements for fixes
        3. Create phased implementation timeline
        4. Calculate potential SEO impact and ROI
        5. Develop success metrics and monitoring plan
        
        Translate technical findings into business strategy.
        """,
        agent=seo_manager,
        expected_output="Strategic roadmap with prioritized recommendations and ROI analysis",
        context=[discovery_task, deep_analysis_task]
    )
    
    # Create enterprise crew
    crew = Crew(
        agents=[technical_lead, seo_manager],
        tasks=[discovery_task, deep_analysis_task, strategy_task],
        process=Process.sequential,
        verbose=True
    )
    
    return crew.kickoff()


def quick_site_check():
    """Example: Quick hreflang health check."""
    
    print("⚡ Quick Site Check Example")
    print("=" * 50)
    
    agents = create_seo_crew()
    seo_specialist = agents[0]
    
    quick_check_task = Task(
        description="""
        Perform a quick hreflang health check:
        
        1. Check account status
        2. Test the main URL for hreflang implementation
        3. Identify immediate issues requiring attention
        4. Provide quick recommendations for critical fixes
        
        Keep analysis focused and actionable for immediate implementation.
        """,
        agent=seo_specialist,
        expected_output="Quick hreflang health check with immediate action items"
    )
    
    crew = Crew(
        agents=[seo_specialist],
        tasks=[quick_check_task],
        verbose=True
    )
    
    return crew.kickoff()


def main():
    """Main function with multiple example options."""
    
    # Check for required API keys
    if not os.getenv("HREFLANG_API_KEY"):
        print("❌ HREFLANG_API_KEY environment variable required")
        print("Get your API key from: https://app.hreflang.org/")
        return
        
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY environment variable required")
        print("Get your API key from: https://platform.openai.com/api-keys")
        return
    
    try:
        import crewai
    except ImportError:
        print("❌ CrewAI not installed. Install with: pip install crewai")
        return
    
    print("🚀 CrewAI Hreflang Analysis Examples")
    print("=" * 50)
    print("Choose an example to run:")
    print("1. Basic Website Analysis")
    print("2. Competitive Analysis")
    print("3. Enterprise SEO Audit")
    print("4. Quick Site Check")
    
    choice = input("\nEnter your choice (1-4): ").strip()
    
    try:
        if choice == "1":
            website = input("Enter website URL (or press Enter for diffen.com): ").strip()
            if not website:
                website = "https://www.diffen.com"
            result = analyze_website(website)
            
        elif choice == "2":
            result = competitive_analysis()
            
        elif choice == "3":
            result = enterprise_audit()
            
        elif choice == "4":
            result = quick_site_check()
            
        else:
            print("Invalid choice. Running quick site check...")
            result = quick_site_check()
        
        print("\n" + "="*50)
        print("🎉 ANALYSIS COMPLETE!")
        print("="*50)
        print(result)
        
    except Exception as e:
        print(f"❌ Error during analysis: {str(e)}")
        print("Please check your API keys and network connection.")


if __name__ == "__main__":
    main()