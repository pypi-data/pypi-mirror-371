"""
LangGraph Agent Example with Hreflang Tools

This example shows how to use langchain-hreflang tools with the modern LangGraph 
framework for more sophisticated international SEO analysis workflows.

Requirements:
- pip install langgraph
- pip install langchain-openai
"""

import os
from typing import Annotated, Sequence, TypedDict
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.sqlite import SqliteSaver
from langchain_hreflang import hreflang_tools


class AgentState(TypedDict):
    """State for the SEO analysis workflow."""
    messages: Sequence[BaseMessage]
    website_url: str
    analysis_type: str
    findings: dict


def create_seo_react_agent():
    """Create a LangGraph ReAct agent with hreflang tools."""
    
    # Initialize LLM
    llm = ChatOpenAI(
        model="gpt-3.5-turbo",
        temperature=0,
    )
    
    # Create React agent with tools
    agent = create_react_agent(
        model=llm,
        tools=hreflang_tools,
        checkpointer=SqliteSaver.from_conn_string(":memory:")  # Memory-based state
    )
    
    return agent


def create_advanced_seo_workflow():
    """Create an advanced multi-step SEO analysis workflow."""
    
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
    
    def account_check_node(state: AgentState):
        """Check account status and limits."""
        from langchain_hreflang import check_hreflang_account_status
        
        print("🔍 Checking account status...")
        result = check_hreflang_account_status.run("")
        
        return {
            "messages": state["messages"] + [HumanMessage(content=f"Account status: {result}")],
            "findings": {**state.get("findings", {}), "account_status": result}
        }
    
    def url_analysis_node(state: AgentState):
        """Analyze URL for hreflang implementation."""
        from langchain_hreflang import test_hreflang_urls
        
        print(f"🔍 Analyzing URL: {state['website_url']}")
        result = test_hreflang_urls.run(state["website_url"])
        
        return {
            "messages": state["messages"] + [HumanMessage(content=f"URL analysis: {result}")],
            "findings": {**state.get("findings", {}), "url_analysis": result}
        }
    
    def sitemap_analysis_node(state: AgentState):
        """Analyze sitemap if requested."""
        from langchain_hreflang import test_hreflang_sitemap
        
        if state["analysis_type"] == "comprehensive":
            print(f"🗺️ Analyzing sitemap for: {state['website_url']}")
            sitemap_url = f"{state['website_url'].rstrip('/')}/sitemap.xml"
            result = test_hreflang_sitemap.run(sitemap_url)
            
            return {
                "messages": state["messages"] + [HumanMessage(content=f"Sitemap analysis: {result}")],
                "findings": {**state.get("findings", {}), "sitemap_analysis": result}
            }
        else:
            return state
    
    def report_generation_node(state: AgentState):
        """Generate comprehensive SEO report."""
        
        print("📊 Generating SEO report...")
        
        # Use LLM to create a comprehensive report
        report_prompt = f"""
        Based on the following hreflang analysis data, create a comprehensive SEO report:
        
        Website: {state['website_url']}
        Analysis Type: {state['analysis_type']}
        
        Findings:
        {state['findings']}
        
        Please provide:
        1. Executive Summary
        2. Technical Findings
        3. Issues Identified
        4. Recommendations
        5. Action Items
        
        Format as a professional SEO audit report.
        """
        
        response = llm.invoke([HumanMessage(content=report_prompt)])
        
        return {
            "messages": state["messages"] + [response],
            "findings": {**state.get("findings", {}), "final_report": response.content}
        }
    
    def should_analyze_sitemap(state: AgentState):
        """Decide whether to analyze sitemap."""
        if state["analysis_type"] == "comprehensive":
            return "sitemap_analysis"
        else:
            return "report_generation"
    
    # Build the workflow graph
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("account_check", account_check_node)
    workflow.add_node("url_analysis", url_analysis_node)
    workflow.add_node("sitemap_analysis", sitemap_analysis_node)
    workflow.add_node("report_generation", report_generation_node)
    
    # Add edges
    workflow.set_entry_point("account_check")
    workflow.add_edge("account_check", "url_analysis")
    workflow.add_conditional_edges(
        "url_analysis",
        should_analyze_sitemap,
        {
            "sitemap_analysis": "sitemap_analysis",
            "report_generation": "report_generation"
        }
    )
    workflow.add_edge("sitemap_analysis", "report_generation")
    workflow.add_edge("report_generation", END)
    
    return workflow.compile()


def simple_react_example():
    """Simple ReAct agent example."""
    
    print("🚀 LangGraph ReAct Agent Example")
    print("=" * 50)
    
    agent = create_seo_react_agent()
    
    # Run the agent
    config = {"configurable": {"thread_id": "seo-analysis-1"}}
    
    response = agent.invoke(
        {
            "messages": [HumanMessage(content="""
            Please analyze the hreflang implementation for https://www.diffen.com:
            
            1. Check my account status first
            2. Test the URL for hreflang implementation  
            3. Provide insights and recommendations
            """)]
        },
        config=config
    )
    
    print("\n📊 ReAct Agent Results:")
    for message in response["messages"]:
        if hasattr(message, 'content'):
            print(f"\n{message.__class__.__name__}: {message.content}")


def advanced_workflow_example():
    """Advanced multi-step workflow example."""
    
    print("\n🔧 Advanced SEO Workflow Example")
    print("=" * 50)
    
    workflow = create_advanced_seo_workflow()
    
    # Run basic analysis
    print("\n--- Basic Analysis ---")
    result = workflow.invoke({
        "messages": [HumanMessage(content="Starting SEO analysis")],
        "website_url": "https://www.diffen.com",
        "analysis_type": "basic",
        "findings": {}
    })
    
    print("\n📊 Basic Analysis Report:")
    print(result["findings"]["final_report"])
    
    # Run comprehensive analysis  
    print("\n--- Comprehensive Analysis ---")
    result = workflow.invoke({
        "messages": [HumanMessage(content="Starting comprehensive SEO analysis")],
        "website_url": "https://booking.com", 
        "analysis_type": "comprehensive",
        "findings": {}
    })
    
    print("\n📊 Comprehensive Analysis Report:")
    print(result["findings"]["final_report"])


def streaming_analysis_example():
    """Example with streaming output for real-time updates."""
    
    print("\n🔄 Streaming Analysis Example")
    print("=" * 50)
    
    agent = create_seo_react_agent()
    config = {"configurable": {"thread_id": "streaming-analysis"}}
    
    inputs = {
        "messages": [HumanMessage(content="""
        Perform a comprehensive hreflang analysis for https://airbnb.com:
        1. Check account status
        2. Analyze URL implementation
        3. Provide detailed recommendations
        
        Stream your analysis as you work through each step.
        """)]
    }
    
    print("🔄 Streaming results...")
    for chunk in agent.stream(inputs, config=config):
        for node_name, node_output in chunk.items():
            print(f"\n--- {node_name.upper()} ---")
            if 'messages' in node_output:
                latest_message = node_output['messages'][-1]
                if hasattr(latest_message, 'content'):
                    print(latest_message.content[:200] + "..." if len(latest_message.content) > 200 else latest_message.content)


def main():
    """Run different LangGraph examples."""
    
    # Check for required API keys and packages
    if not os.getenv("HREFLANG_API_KEY"):
        print("❌ HREFLANG_API_KEY environment variable required")
        return
        
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY environment variable required")
        return
    
    try:
        import langgraph
    except ImportError:
        print("❌ LangGraph not installed. Install with: pip install langgraph")
        return
    
    print("🚀 LangGraph Hreflang Analysis Examples")
    print("=" * 50)
    print("Choose an example to run:")
    print("1. Simple ReAct Agent")
    print("2. Advanced Multi-Step Workflow")
    print("3. Streaming Analysis")
    
    choice = input("\nEnter your choice (1-3): ").strip()
    
    if choice == "1":
        simple_react_example()
    elif choice == "2":
        advanced_workflow_example()
    elif choice == "3":
        streaming_analysis_example()
    else:
        print("Invalid choice. Running simple ReAct example...")
        simple_react_example()


if __name__ == "__main__":
    main()