# Implementation Plan: MkDocs Template Setup

## Overview

This implementation plan adds complete MkDocs documentation infrastructure and Python development tooling to the py-repo-template repository. Tasks are organized into phases that build incrementally, with each phase completing before moving to the next.

## Task List

- [x] 1. Configuration Files Setup





  - Create all configuration files for MkDocs, ReadTheDocs, and development tools
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 2.1-2.5, 4.1-4.5, 5.1-5.5, 12.1-12.6_
- [x] 1.1 Create mkdocs.yml configuration file




- [x] 1.1 Create mkdocs.yml configuration file



  - Create mkdocs.yml in repository root with complete configuration
  - Include site metadata with template placeholders ({{PROJECT_NAME}}, {{PROJECT_DESCRIPTION}})
  - Configure Material theme with content.code.copy feature
  - Configure plugins: search, mkdocstrings (Google-style), print-site
  - Configure markdown extensions: admonitions, tables, fenced_code, toc
  - Define navigation structure: Home, Users, Developers, API Reference, Appendices
  - _Requirements: 1.1, 1.5, 2.1-2.5, 3.9, 6.1-6.3, 6.5_

- [x] 1.2 Create .readthedocs.yaml configuration file


  - Create .readthedocs.yaml in repository root
  - Set version to 2
  - Configure build OS as ubuntu-24.04
  - Configure Python 3.13 as build tool
  - Reference mkdocs.yml for MkDocs configuration
  - Reference docs/requirements.txt for dependencies
  - _Requirements: 1.2, 5.1-5.5_

- [x] 1.3 Create docs/requirements.txt file


  - Create docs/requirements.txt with MkDocs dependencies
  - Include mkdocstrings
  - Include mkdocstrings-python
  - Include mkdocs-material
  - Include mkdocs-print-site-plugin
  - _Requirements: 1.3, 4.1-4.4_

- [x] 1.4 Update pyproject.toml with optional dependencies


  - Add [project.optional-dependencies] section if not exists
  - Add docs group with mkdocs>=1.4.0 and mkdocstrings[python]>=0.20.0
  - Add dev group with ruff>=0.1.0, black>=23.0.0, pre-commit>=3.0.0
  - Add [tool.ruff] configuration with line-length=88, target-version="py312"
  - Add ruff select rules: E, W, F, I, B, C4, UP
  - Add [tool.black] configuration with line-length=88, target-version=['py312']
  - Add [tool.ruff.isort] with known-first-party=["{{PACKAGE_NAME}}"]
  - _Requirements: 1.4, 4.5, 12.1-12.3, 12.5-12.6_

- [x] 1.5 Create .pre-commit-config.yaml file


  - Create .pre-commit-config.yaml in repository root
  - Add pre-commit-hooks repo with trailing-whitespace, end-of-file-fixer, check-yaml, check-added-large-files, check-toml
  - Add black repo with black hook for Python 3.12
  - Add ruff-pre-commit repo with ruff hook with --fix and --exit-non-zero-on-fix args
  - _Requirements: 12.4_

- [x] 2. Documentation Directory Structure





  - Create complete docs/ directory structure following organization standards
  - _Requirements: 3.1-3.9_


- [x] 2.1 Create docs/ directory structure

  - Create docs/ directory
  - Create docs/articles/ directory
  - Create docs/articles/users/ directory
  - Create docs/articles/users/tutorials/ directory (with .gitkeep)
  - Create docs/articles/devs/ directory
  - Create docs/articles/devs/architecture/ directory (with .gitkeep)
  - Create docs/articles/devs/contribution_guidelines/ directory (with .gitkeep)
  - Create docs/articles/devs/implementation_guides/ directory (with .gitkeep)
  - Create docs/articles/api/ directory
  - Create docs/articles/appendices/ directory
  - _Requirements: 3.1-3.6_


- [x] 2.2 Create docs/resources/ directory structure

  - Create docs/resources/ directory
  - Create docs/resources/diagrams/ directory
  - Create docs/resources/diagrams/mermaid/ directory
  - Create docs/resources/images/ directory (with .gitkeep)
  - Create docs/resources/images/screenshots/ directory (with .gitkeep)
  - Create docs/resources/images/logos/ directory (with .gitkeep)
  - Create docs/resources/images/icons/ directory (with .gitkeep)
  - _Requirements: 3.7, 3.8_

- [x] 3. Core Documentation Content





  - Write all required documentation files following organization style guide
  - _Requirements: 7.1-7.7, 11.1-11.5_

- [x] 3.1 Create docs/index.md homepage


  - Write welcoming homepage with project overview using {{PROJECT_NAME}} and {{PROJECT_DESCRIPTION}}
  - Include navigation guidance to main sections
  - Add quick start information
  - Include links to Users, Developers, API Reference, and Appendices sections
  - Use focused professional tone with warmth at transitions
  - Use present tense and active voice
  - _Requirements: 3.1, 6.4, 7.1, 7.8, 7.9_

- [x] 3.2 Create docs/articles/index.md landing page


  - Write main landing page for articles
  - Include links to Users, Developers, API Reference, and Appendices sections
  - Provide brief description of each section's purpose
  - Use compelling conciseness with precise paragraphs
  - _Requirements: 3.2, 7.2, 11.1_

- [x] 3.3 Create docs/articles/users/GettingStarted.md


  - Write getting started guide with installation instructions
  - Include installation from source and from PyPI
  - Add basic usage examples with {{PACKAGE_NAME}} placeholder
  - Include next steps and links to tutorials
  - Follow style guide: focused, professional tone
  - Use present tense and active voice
  - _Requirements: 3.3, 6.4, 7.3, 7.8, 7.9_

- [x] 3.4 Create docs/articles/devs/index.md


  - Write developer overview with development environment setup
  - Include instructions for installing dependencies: pip install -e .[docs,dev]
  - Add instructions for setting up pre-commit hooks: pre-commit install
  - Include instructions for running code quality tools: pre-commit run --all-files
  - Add instructions for running tests
  - Include conventional commits guidance
  - Add contributing guidelines overview
  - Include links to detailed developer documentation sections
  - _Requirements: 3.4, 7.4_

- [x] 3.5 Create docs/articles/api/index.md


  - Write API reference overview
  - Explain how to use mkdocstrings for automated API documentation
  - Include getting started section with import examples using {{PACKAGE_NAME}}
  - Add module index with descriptions
  - Provide usage examples demonstrating mkdocstrings syntax
  - Show example of ::: {{PACKAGE_NAME}}.module_name syntax
  - _Requirements: 3.5, 6.4, 7.5_

- [x] 3.6 Create docs/articles/api/core.md


  - Create API documentation file for core module
  - Use mkdocstrings syntax: ::: {{PACKAGE_NAME}}.core
  - Add brief introduction to core module functionality
  - _Requirements: 3.5, 6.5_

- [x] 3.7 Create docs/articles/appendices/index.md


  - Write appendices overview
  - Provide table of contents linking to all appendix articles
  - Include link to glossary
  - Explain purpose of appendices section
  - _Requirements: 3.6, 7.6_

- [x] 3.8 Create docs/articles/appendices/glossary.md


  - Write glossary template with example terms
  - Organize terms in alphabetical order with letter sections (A, B, C, etc.)
  - Include instructions for adding project-specific terms
  - Add example terms: MkDocs, mkdocstrings, Material Theme, ReadTheDocs, etc.
  - _Requirements: 3.6, 7.7_

- [x] 4. Resources and Examples




  - Create example Mermaid diagrams and demonstrate usage
  - _Requirements: 10.1-10.5_

- [x] 4.1 Create example Mermaid diagram file


  - Create docs/resources/diagrams/mermaid/example-architecture.mmd
  - Write example architecture diagram showing User -> CLI -> Core -> Functionality -> Output
  - Use high contrast colors with black text and borders
  - Include comments explaining diagram structure using %% syntax
  - Use graph TD or graph LR for appropriate layout
  - _Requirements: 10.2, 10.4_

- [x] 4.2 Add inline Mermaid diagram example to documentation


  - Add embedded Mermaid diagram to docs/index.md or docs/articles/devs/index.md
  - Use ```mermaid code block syntax
  - Include simple example (e.g., flowchart or sequence diagram)
  - Add comments explaining the diagram
  - _Requirements: 10.1, 10.3, 10.4_

- [x] 4.3 Test MkDocs Mermaid rendering



  - Run mkdocs build command
  - Verify Mermaid diagrams render correctly in generated HTML
  - Check both inline and external diagram references
  - _Requirements: 10.5_

- [x] 5. Code Documentation Enhancement




  - Enhance template Python code with complete Google-style docstrings
  - _Requirements: 9.1-9.5_

- [x] 5.1 Enhance {{PACKAGE_NAME}}/__init__.py with complete docstrings


  - Update module-level docstring with detailed description
  - Add typical usage example in module docstring
  - Include Classes and Functions sections in module docstring
  - Ensure all sections use {{PROJECT_NAME}}, {{PACKAGE_NAME}}, {{PROJECT_DESCRIPTION}} placeholders
  - _Requirements: 9.1, 9.2_

- [x] 5.2 Enhance {{PACKAGE_NAME}}/core.py with complete docstrings


  - Update module-level docstring with detailed description and usage example
  - Ensure hello_world() function has complete docstring with Args, Returns, Example sections
  - Ensure ExampleClass has complete docstring with Attributes and Example sections
  - Ensure ExampleClass.__init__() has complete docstring with Args section
  - Ensure ExampleClass.greet() has complete docstring with Returns and Example sections
  - Verify all type hints match docstring descriptions
  - Ensure all examples are runnable
  - _Requirements: 9.1, 9.3, 9.4_

- [x] 5.3 Test mkdocstrings API documentation generation


  - Run mkdocs build command
  - Verify API documentation generates correctly from docstrings
  - Check that all sections (Args, Returns, Examples) appear in generated docs
  - Verify type hints display correctly
  - _Requirements: 9.5_

- [x] 6. README and Template Usage Updates





  - Update README.md and TEMPLATE_USAGE.md with new features
  - _Requirements: 8.1-8.3, 12.7, 13.1-13.10_

- [x] 6.1 Update README.md with documentation link


  - Replace "Coming Soon" in Links section with actual documentation URL
  - Use pattern: https://crackingshells.github.io/{{PROJECT_NAME}}/
  - _Requirements: 8.1, 8.2_

- [x] 6.2 Add documentation build instructions to README.md


  - Add "Building Documentation" subsection to Development section
  - Include command: mkdocs serve (for local development)
  - Include command: mkdocs build (for production build)
  - Add note about documentation being published automatically via ReadTheDocs
  - _Requirements: 8.3_

- [x] 6.3 Add pre-commit setup instructions to README.md


  - Add "Code Quality Tools" subsection to Development section
  - Include command: pip install -e .[dev]
  - Include command: pre-commit install
  - Include command: pre-commit run --all-files (manual run)
  - Explain that hooks run automatically on git commit
  - _Requirements: 12.7_

- [x] 6.4 Update TEMPLATE_USAGE.md with documentation files


  - Add mkdocs.yml to "Files to update" list
  - Add .readthedocs.yaml to "Files to update" list
  - Add .pre-commit-config.yaml to "Files to update" list
  - Add docs/index.md to "Files to update" list
  - Add docs/articles/**/*.md (all documentation files) to "Files to update" list
  - _Requirements: 13.1, 13.2, 13.3_

- [x] 6.5 Add template variable replacement commands to TEMPLATE_USAGE.md


  - Add PowerShell commands for Windows in "Variable Replacement" section
  - Add Bash commands for Linux/Mac in "Variable Replacement" section
  - Include commands that replace {{PROJECT_NAME}}, {{PACKAGE_NAME}}, {{PROJECT_DESCRIPTION}}
  - Cover file types: *.md, *.yml, *.toml, *.py, *.json
  - _Requirements: 13.4_

- [x] 6.6 Add documentation setup instructions to TEMPLATE_USAGE.md


  - Update "Initial Setup" section with: pip install -e .[docs,dev]
  - Add: pre-commit install
  - Add: mkdocs serve (for local documentation)
  - Add: pre-commit run --all-files (for code quality checks)
  - _Requirements: 13.5, 13.6, 13.7_

- [x] 6.7 Update "What's Included" section in TEMPLATE_USAGE.md


  - Add "Documentation Infrastructure" subsection
  - List: Complete MkDocs setup, Material theme, mkdocstrings for API docs, ReadTheDocs integration, Mermaid diagram support
  - Add "Code Quality Tools" subsection
  - List: ruff for linting, black for formatting, pre-commit hooks for automated checks
  - Update "Development Workflow" subsection
  - Add: Pre-commit hooks, code quality automation, documentation generation
  - _Requirements: 13.8, 13.9_

- [x] 6.8 Update "What's NOT Included" section in TEMPLATE_USAGE.md


  - Remove "Code Quality Tools (Deferred)" section (now included)
  - Remove "Comprehensive Documentation (Deferred)" section (now included)
  - Keep "Advanced Testing (Deferred)" section (still waiting for wobble)
  - _Requirements: 13.10_

- [x] 7. Testing and Validation



  - Test all components and validate against requirements
  - _Requirements: All_

- [x] 7.1 Test MkDocs build locally


  - Run: mkdocs build
  - Verify build completes without errors or warnings
  - Check that site/ directory is created with HTML files
  - _Requirements: All configuration and content requirements_


- [x] 7.2 Test MkDocs serve and navigation

  - Run: mkdocs serve
  - Open http://127.0.0.1:8000 in browser
  - Verify all navigation links work correctly
  - Check that all pages load without errors
  - Verify Material theme renders correctly
  - Test search functionality
  - _Requirements: All navigation and content requirements_



- [ ] 7.3 Test pre-commit hooks
  - Run: pre-commit install
  - Run: pre-commit run --all-files
  - Verify all hooks execute successfully
  - Check that ruff and black run without errors on template code
  - Make a test commit to verify hooks run automatically


  - _Requirements: 12.1-12.7_

- [ ] 7.4 Validate template placeholder consistency
  - Search all files for hardcoded project names


  - Verify all project-specific values use {{PROJECT_NAME}}, {{PACKAGE_NAME}}, or {{PROJECT_DESCRIPTION}}
  - Check mkdocs.yml, documentation files, and Python code
  - _Requirements: 1.5, 6.1-6.5_




- [ ] 7.5 Test template variable replacement commands
  - Test PowerShell commands on Windows (if available)
  - Test Bash commands on Linux/Mac (if available)
  - Verify all placeholders are replaced correctly
  - Check that no placeholders remain after replacement
  - _Requirements: 13.4_

- [ ] 8. Final Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise
  - Verify all requirements are met
  - Confirm documentation builds successfully
  - Confirm pre-commit hooks work correctly
  - Validate that projects created from template have working documentation and dev tools
