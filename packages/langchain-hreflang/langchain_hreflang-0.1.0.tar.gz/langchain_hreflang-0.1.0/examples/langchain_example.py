"""
LangChain Agent Example with Hreflang Tools

This example shows how to use langchain-hreflang tools with standard LangChain agents
for international SEO analysis.
"""

import os
from langchain_openai import ChatOpenAI
from langchain.agents import initialize_agent, AgentType
from langchain_hreflang import hreflang_tools


def create_seo_agent():
    """Create a LangChain agent specialized for international SEO analysis."""
    
    # Initialize OpenAI LLM (you can use other providers too)
    llm = ChatOpenAI(
        temperature=0,
        model="gpt-3.5-turbo",
        # model="gpt-4",  # Use GPT-4 for better analysis
    )
    
    # Create agent with hreflang tools
    agent = initialize_agent(
        tools=hreflang_tools,
        llm=llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,  # Set to False to reduce output
        max_iterations=5,
        handle_parsing_errors=True
    )
    
    return agent


def analyze_single_website():
    """Example: Analyze a single website for hreflang implementation."""
    
    print("🔍 Single Website Analysis Example")
    print("=" * 50)
    
    agent = create_seo_agent()
    
    result = agent.run("""
    Please analyze the hreflang implementation for https://airbnb.com:
    
    1. First, check my account status to see available limits
    2. Test the main URL for hreflang implementation
    3. Provide a detailed analysis of:
       - Languages detected
       - Any implementation issues
       - SEO recommendations for improvement
    4. Summarize your findings in a professional report format
    """)
    
    print("\n" + "=" * 50)
    print("📊 Analysis Complete:")
    print(result)


def compare_multiple_websites():
    """Example: Compare hreflang implementation across multiple websites."""
    
    print("\n🔄 Multi-Website Comparison Example")
    print("=" * 50)
    
    agent = create_seo_agent()
    
    result = agent.run("""
    Compare the hreflang implementation between these international websites:
    
    1. https://booking.com
    2. https://expedia.com
    
    For each website:
    - Test the hreflang implementation 
    - Identify the languages supported
    - Note any implementation differences
    - Provide recommendations
    
    Then create a comparison summary highlighting best practices.
    """)
    
    print("\n" + "=" * 50)
    print("📊 Comparison Complete:")
    print(result)


def audit_sitemap():
    """Example: Comprehensive sitemap audit."""
    
    print("\n🗺️ Sitemap Audit Example")
    print("=" * 50)
    
    agent = create_seo_agent()
    
    result = agent.run("""
    Perform a comprehensive sitemap audit for international SEO:
    
    1. Check my account limits first
    2. Test this sitemap: https://www.booking.com/sitemap.xml
    3. Analyze the results and provide:
       - Total URLs found
       - Language coverage analysis  
       - Implementation issues found
       - Recommendations for improvement
       - Action items for the SEO team
    """)
    
    print("\n" + "=" * 50)
    print("📊 Sitemap Audit Complete:")
    print(result)


def interactive_seo_consultation():
    """Example: Interactive SEO consultation session."""
    
    print("\n💬 Interactive SEO Consultation")
    print("=" * 50)
    print("Ask the SEO agent questions about hreflang implementation!")
    print("Type 'quit' to exit")
    
    agent = create_seo_agent()
    
    while True:
        question = input("\n🤔 Your question: ").strip()
        
        if question.lower() in ['quit', 'exit', 'q']:
            print("👋 Thanks for the consultation!")
            break
            
        if not question:
            continue
            
        try:
            response = agent.run(question)
            print(f"\n🧠 SEO Agent: {response}")
            
        except KeyboardInterrupt:
            print("\n\n👋 Session interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")


def main():
    """Run different examples based on user choice."""
    
    # Check for required API keys
    if not os.getenv("HREFLANG_API_KEY"):
        print("❌ HREFLANG_API_KEY environment variable required")
        print("Get your free API key from: https://app.hreflang.org/")
        return
        
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY environment variable required")  
        print("Get your API key from: https://platform.openai.com/api-keys")
        return
    
    print("🚀 LangChain Hreflang Analysis Examples")
    print("=" * 50)
    print("Choose an example to run:")
    print("1. Single Website Analysis")
    print("2. Multi-Website Comparison") 
    print("3. Sitemap Audit")
    print("4. Interactive SEO Consultation")
    
    choice = input("\nEnter your choice (1-4): ").strip()
    
    if choice == "1":
        analyze_single_website()
    elif choice == "2":
        compare_multiple_websites()
    elif choice == "3":
        audit_sitemap()
    elif choice == "4":
        interactive_seo_consultation()
    else:
        print("Invalid choice. Running single website analysis...")
        analyze_single_website()


if __name__ == "__main__":
    main()