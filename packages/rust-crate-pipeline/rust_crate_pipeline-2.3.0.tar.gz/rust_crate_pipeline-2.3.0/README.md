# Rust Crate Pipeline v2.3.0

A comprehensive system for gathering, enriching, and analyzing metadata for Rust crates using AI-powered insights, web scraping, and enhanced Rust analysis tools. This pipeline provides deep analysis of Rust crates with support for multiple LLM providers, advanced web scraping, the Sigil Protocol for Sacred Chain analysis, and comprehensive Rust code quality assessment.

## 🚀 Quick Start

### Option 1: Install via pip (Recommended for users)

```bash
# Install the package (includes automatic setup)
pip install rust-crate-pipeline

# The package will automatically run setup for Playwright, Crawl4AI, and Rust tools
# You can also run setup manually:
rust-crate-pipeline --setup

# Run with your preferred LLM provider
rust-crate-pipeline --llm-provider ollama --llm-model tinyllama --crates serde tokio
```

### Option 2: Clone and run from repository (Recommended for developers)

```bash
# Clone the repository
git clone https://github.com/Superuser666-Sigil/SigilDERG-Data_Production.git
cd SigilDERG-Data_Production

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Run setup for all components
python -m rust_crate_pipeline --setup

# Run the pipeline
python run_with_llm.py --llm-provider ollama --llm-model tinyllama --crates serde tokio
```

## ✨ Key Features

- **🤖 Multi-Provider LLM Support**: Azure OpenAI, OpenAI, Anthropic, Ollama, LM Studio, Lambda.AI, and all LiteLLM providers
- **🌐 Advanced Web Scraping**: Crawl4AI + Playwright for intelligent content extraction
- **🔧 Enhanced Rust Analysis**: cargo-geiger, cargo-outdated, cargo-license, cargo-tarpaulin, cargo-deny
- **⚡ Auto-Resume Capability**: Automatically skips already processed crates
- **📊 Real-time Progress Tracking**: Comprehensive monitoring and error recovery
- **🔒 Sigil Protocol Support**: Sacred Chain analysis with IRL trust scoring
- **🐳 Docker Support**: Containerized deployment with docker-compose
- **📦 Batch Processing**: Configurable memory optimization and cost control
- **🛡️ Security Analysis**: Privacy and security scanning with Presidio
- **📈 Comprehensive Output**: JSON metadata with detailed crate analysis
- **🔍 Unsafe Code Detection**: Cargo-geiger integration for safety analysis
- **📋 Quality Scoring**: Automated quality and security risk assessment

## 📋 Requirements

- **Python 3.11+** (required)
- **Git** (for repository operations)
- **Cargo** (for Rust crate analysis)
- **Playwright browsers** (auto-installed via setup)
- **Rust analysis tools** (auto-installed via setup)

## 🔧 Installation & Setup

### For End Users (pip install)

The package now includes automatic setup that configures all dependencies:

```bash
# Install the package (includes all dependencies and automatic setup)
pip install rust-crate-pipeline

# Check setup status
rust-crate-pipeline --setup-check

# Run setup manually if needed
rust-crate-pipeline --setup --verbose-setup
```

### For Developers (repository clone)

```bash
# Clone the repository
git clone https://github.com/Superuser666-Sigil/SigilDERG-Data_Production.git
cd SigilDERG-Data_Production

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Run comprehensive setup
python -m rust_crate_pipeline --setup --verbose-setup

# Set up environment variables (optional but recommended)
export AZURE_OPENAI_ENDPOINT="your_endpoint"
export AZURE_OPENAI_API_KEY="your_api_key"
export GITHUB_TOKEN="your_github_token"
```

## 🎯 Usage Examples

### Basic Usage with Ollama (Local LLM)

```bash
# Start Ollama and pull a model
ollama serve
ollama pull tinyllama

# Run pipeline with Ollama
rust-crate-pipeline --llm-provider ollama --llm-model tinyllama --crates serde tokio
```

### Advanced Usage with Azure OpenAI

```bash
# Set environment variables
export AZURE_OPENAI_ENDPOINT="your_endpoint"
export AZURE_OPENAI_API_KEY="your_api_key"

# Run with Azure OpenAI
rust-crate-pipeline --llm-provider azure --llm-model gpt-4o --crates actix-web rocket
```

### Batch Processing with Auto-Resume

```bash
# Process from crate list with auto-resume
rust-crate-pipeline --crates-file data/crate_list.txt --auto-resume --batch-size 5

# Force restart processing
rust-crate-pipeline --crates-file data/crate_list.txt --force-restart
```

### Enhanced Analysis with All Tools

```bash
# Run with enhanced Rust analysis (cargo-geiger, cargo-outdated, etc.)
rust-crate-pipeline --llm-provider ollama --llm-model tinyllama --crates serde --verbose
```

## 🔍 Enhanced Rust Analysis

The pipeline now includes comprehensive Rust analysis tools:

- **cargo-geiger**: Unsafe code detection and safety scoring
- **cargo-outdated**: Dependency update recommendations
- **cargo-license**: License analysis and compliance
- **cargo-tarpaulin**: Code coverage analysis
- **cargo-deny**: Comprehensive dependency checking

### Analysis Output

Each crate analysis includes:

```json
{
  "enhanced_analysis": {
    "build": { "returncode": 0, "stdout": "...", "stderr": "..." },
    "test": { "returncode": 0, "stdout": "...", "stderr": "..." },
    "clippy": { "returncode": 0, "stdout": "...", "stderr": "..." },
    "geiger": { "returncode": 0, "stdout": "...", "stderr": "..." },
    "insights": {
      "overall_quality_score": 0.85,
      "security_risk_level": "low",
      "code_quality": "excellent",
      "geiger_insights": {
        "total_unsafe_items": 2,
        "safety_score": 0.98,
        "risk_level": "low"
      },
      "recommendations": [
        "Consider updating dependencies",
        "Review 2 unsafe code items detected by cargo-geiger"
      ]
    }
  }
}
```

## 🤖 LLM Provider Support

### Supported Providers

| Provider | Setup | Usage |
|----------|-------|-------|
| **Ollama** | `ollama serve` + `ollama pull model` | `--llm-provider ollama --llm-model tinyllama` |
| **Azure OpenAI** | Set env vars | `--llm-provider azure --llm-model gpt-4o` |
| **OpenAI** | Set `OPENAI_API_KEY` | `--llm-provider openai --llm-model gpt-4` |
| **Anthropic** | Set `ANTHROPIC_API_KEY` | `--llm-provider anthropic --llm-model claude-3` |
| **LM Studio** | Start LM Studio server | `--llm-provider lmstudio --llm-model local-model` |
| **llama-cpp** | Download .gguf file | `--llm-provider llama-cpp --llm-model path/to/model.gguf` |

### Provider Configuration

```bash
# Ollama (recommended for local development)
rust-crate-pipeline --llm-provider ollama --llm-model tinyllama

# Azure OpenAI (recommended for production)
rust-crate-pipeline --llm-provider azure --llm-model gpt-4o

# OpenAI
rust-crate-pipeline --llm-provider openai --llm-model gpt-4

# Local llama-cpp model
rust-crate-pipeline --llm-provider llama-cpp --llm-model ~/models/deepseek.gguf
```

## 📊 Output and Results

### Analysis Reports

The pipeline generates comprehensive analysis reports:

- **Basic Metadata**: Crate information, dependencies, downloads
- **Web Scraping Results**: Documentation from crates.io, docs.rs, lib.rs
- **Enhanced Analysis**: Rust tool outputs and quality metrics
- **LLM Enrichment**: AI-generated insights and recommendations
- **Sacred Chain Analysis**: Trust scoring and security assessment

### Output Structure

```
output/
├── serde_analysis_report.json      # Complete analysis
├── tokio_analysis_report.json      # Complete analysis
├── checkpoint_batch_1_20250821.jsonl  # Progress checkpoints
└── pipeline_status.json            # Overall status
```

### Audit Logs

Comprehensive audit logs are stored in `audits/records/` for compliance and traceability.

## 🔧 Setup and Configuration

### Automatic Setup

The package includes automatic setup for all dependencies:

```bash
# Run setup (automatically runs on pip install)
rust-crate-pipeline --setup

# Check setup status
rust-crate-pipeline --setup-check

# Verbose setup with detailed output
rust-crate-pipeline --setup --verbose-setup
```

### Manual Setup

If automatic setup fails, you can run components manually:

```bash
# Install Playwright browsers
playwright install

# Install Rust analysis tools
cargo install cargo-geiger cargo-outdated cargo-license cargo-tarpaulin cargo-deny

# Configure environment variables
cp ~/.rust_crate_pipeline/.env.template .env
# Edit .env with your API keys
```

### Configuration Files

Setup creates configuration files in `~/.rust_crate_pipeline/`:

- `crawl4ai_config.json`: Crawl4AI settings
- `rust_tools_config.json`: Rust tool status
- `llm_providers_config.json`: LLM provider configurations
- `system_checks.json`: System compatibility results
- `.env.template`: Environment variable template

## 🐳 Docker Support

### Quick Docker Setup

```bash
# Build and run with Docker Compose
docker-compose up -d

# Run pipeline in container
docker-compose exec rust-pipeline rust-crate-pipeline --crates serde tokio
```

### Custom Docker Configuration

```dockerfile
# Use the provided Dockerfile
FROM python:3.12-slim

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Install Rust and tools
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
RUN cargo install cargo-geiger cargo-outdated cargo-license cargo-tarpaulin cargo-deny

# Install Playwright
RUN playwright install

# Copy application
COPY . /app
WORKDIR /app

# Run setup
RUN python -m rust_crate_pipeline --setup
```

## 🔍 Troubleshooting

### Common Issues

1. **Playwright browsers not installed**
   ```bash
   playwright install
   ```

2. **Rust tools not available**
   ```bash
   rust-crate-pipeline --setup
   ```

3. **LLM connection issues**
   ```bash
   # Check Ollama
   curl http://localhost:11434/api/tags
   
   # Check Azure OpenAI
   curl -H "api-key: $AZURE_OPENAI_API_KEY" "$AZURE_OPENAI_ENDPOINT/openai/deployments"
   ```

4. **Setup failures**
   ```bash
   # Check setup status
   rust-crate-pipeline --setup-check
   
   # Run verbose setup
   rust-crate-pipeline --setup --verbose-setup
   ```

### Logs and Debugging

```bash
# Enable debug logging
rust-crate-pipeline --log-level DEBUG --crates serde

# Check setup logs
cat ~/.rust_crate_pipeline/setup_results.json
```

## 📈 Performance and Optimization

### Batch Processing

```bash
# Optimize for memory usage
rust-crate-pipeline --batch-size 2 --max-workers 2

# Optimize for speed
rust-crate-pipeline --batch-size 10 --max-workers 8
```

### Cost Control

```bash
# Skip expensive operations
rust-crate-pipeline --skip-ai --skip-source-analysis

# Limit processing
rust-crate-pipeline --limit 50 --batch-size 5
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Run the test suite
6. Submit a pull request

### Development Setup

```bash
# Clone and setup development environment
git clone https://github.com/Superuser666-Sigil/SigilDERG-Data_Production.git
cd SigilDERG-Data_Production

# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest tests/

# Run linting
black rust_crate_pipeline/
flake8 rust_crate_pipeline/
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Crawl4AI** for advanced web scraping capabilities
- **Playwright** for browser automation
- **Rust community** for the excellent analysis tools
- **Ollama** for local LLM serving
- **All LLM providers** for their APIs and models

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/Superuser666-Sigil/SigilDERG-Data_Production/issues)
- **Documentation**: [Wiki](https://github.com/Superuser666-Sigil/SigilDERG-Data_Production/wiki)
- **Discussions**: [GitHub Discussions](https://github.com/Superuser666-Sigil/SigilDERG-Data_Production/discussions)

---

**Rust Crate Pipeline v2.3.0** - Comprehensive Rust crate analysis with AI-powered insights and enhanced tooling.
