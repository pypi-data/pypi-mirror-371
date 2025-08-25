# LangChain Hreflang Tools

[![PyPI version](https://badge.fury.io/py/langchain-hreflang.svg)](https://badge.fury.io/py/langchain-hreflang)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A comprehensive set of LangChain tools for analyzing hreflang implementation using the [hreflang.org](https://hreflang.org) API. Perfect for international SEO analysis with AI agents.

## 🚀 Features

- **Three powerful LangChain tools** for hreflang analysis
- **Compatible with CrewAI** and any LangChain-based framework
- **Comprehensive hreflang auditing** for international websites
- **Sitemap analysis** for large-scale SEO audits
- **Account management** and usage tracking
- **Detailed error reporting** and recommendations

## 📦 Installation

```bash
pip install langchain-hreflang
```

For development with all extras:
```bash
pip install langchain-hreflang[all]
```

For CrewAI integration:
```bash
pip install langchain-hreflang[crewai]
```

## 🔑 Setup

1. **Get API Key**: Visit [hreflang.org](https://app.hreflang.org/), sign up (free), and generate an API key
2. **Set Environment Variable**:
   ```bash
   export HREFLANG_API_KEY="your_api_key_here"
   ```
   Or add to your `.env` file:
   ```
   HREFLANG_API_KEY=your_api_key_here
   ```

## 🛠️ Available Tools

### 1. `test_hreflang_urls`
Test specific URLs for hreflang implementation.

### 2. `test_hreflang_sitemap`
Analyze entire sitemaps for international SEO compliance.

### 3. `check_hreflang_account_status`
Monitor your API usage limits and test history.

## 📚 Usage Examples

### Basic LangChain Usage

```python
from langchain_hreflang import test_hreflang_urls, test_hreflang_sitemap

# Test specific URLs
result = test_hreflang_urls.run("https://example.com/en/, https://example.com/es/")
print(result)

# Test entire sitemap
result = test_hreflang_sitemap.run("https://example.com/sitemap.xml")
print(result)
```

### CrewAI Integration

```python
from crewai import Agent, Task, Crew
from langchain_hreflang import hreflang_tools

# Create SEO specialist agent
seo_agent = Agent(
    role="International SEO Specialist",
    goal="Analyze and optimize hreflang implementation for international websites",
    backstory="Expert in international SEO with deep knowledge of hreflang best practices.",
    tools=hreflang_tools,  # All three tools included
    verbose=True
)

# Create analysis task
task = Task(
    description="""
    Analyze the hreflang implementation for https://example.com:
    1. Test the main language versions
    2. Check the sitemap for comprehensive coverage
    3. Identify any implementation issues
    4. Provide specific recommendations
    """,
    agent=seo_agent
)

# Run the analysis
crew = Crew(agents=[seo_agent], tasks=[task])
result = crew.kickoff()
```

### LangChain Agents

```python
from langchain.agents import initialize_agent, AgentType
from langchain.llms import OpenAI
from langchain_hreflang import hreflang_tools

llm = OpenAI(temperature=0)
agent = initialize_agent(
    hreflang_tools,
    llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

result = agent.run("""
Analyze the hreflang implementation for airbnb.com.
Check their main international pages and provide a summary
including any issues found.
""")
```

## 🔍 What Gets Analyzed

- **Hreflang tag implementation** across language versions
- **Self-declared language detection** (`<html lang="en">`)
- **Bidirectional linking** between language versions  
- **Return tag errors** and missing connections
- **Site-wide statistics** for entire domains
- **Broken URLs** and loading issues
- **Language coverage analysis**

## 📊 Example Output

```
Hreflang Test Results (Test ID: abc123...)
Total URLs tested: 3

URL: https://example.com/en/
  Self-declared language: en
  Hreflang links found: 3
    en: https://example.com/en/
    es: https://example.com/es/
    fr: https://example.com/fr/

URL: https://example.com/es/
  Self-declared language: es
  Hreflang links found: 3
    en: https://example.com/en/
    es: https://example.com/es/
    fr: https://example.com/fr/

Issues Found:
  ⚠️  Missing return link from FR to EN version
  ❌  https://example.com/de/ returns 404 error
```

## 🎯 Rate Limits

- **Free Tier**: 50 URLs per test, 10 tests per day
- **Premium Tier**: 1,000 URLs per test, 500 tests per day

Check your limits with `check_hreflang_account_status()`.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [hreflang.org](https://hreflang.org) for providing the excellent hreflang testing API
- [LangChain](https://langchain.com) for the powerful AI agent framework
- [CrewAI](https://crewai.com) for the collaborative AI agent platform

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/langchain-hreflang/issues)
- **Documentation**: [README](https://github.com/yourusername/langchain-hreflang#readme)
- **API Documentation**: [hreflang.org API docs](https://app.hreflang.org/api-docs.php)

---

**Made with ❤️ for the international SEO and AI community**