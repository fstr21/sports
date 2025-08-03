What is Steering?
Steering gives Kiro persistent knowledge about your project through markdown files in .kiro/steering/. Instead of explaining your conventions in every chat, steering files ensure Kiro consistently follows your established patterns, libraries, and standards.

Copied!Key Benefits
Consistent Code Generation - Every component, API endpoint, or test follows your team's established patterns and conventions.

Reduced Repetition - No need to explain project standards in each conversation. Kiro remembers your preferences.

Team Alignment - All developers work with the same standards, whether they're new to the project or seasoned contributors.

Scalable Project Knowledge - Documentation that grows with your codebase, capturing decisions and patterns as your project evolves.

Copied!Getting Started with Steering Files
Kiro provides foundational steering files to establish core project context. You can generate these files as follows:

Navigate to the Steering section in the Kiro panel
Click the Generate Steering Docs button
Kiro will create three foundational files:
Product Overview (product.md) - Defines your product's purpose, target users, key features, and business objectives. This helps Kiro understand the "why" behind technical decisions and suggest solutions aligned with your product goals.

Technology Stack (tech.md) - Documents your chosen frameworks, libraries, development tools, and technical constraints. When Kiro suggests implementations, it will prefer your established stack over alternatives.

Project Structure (structure.md) - Outlines file organization, naming conventions, import patterns, and architectural decisions. This ensures generated code fits seamlessly into your existing codebase.

These foundation files are included in every interaction by default, forming the baseline of Kiro's project understanding.

Copied!Creating Custom Steering Files
Extend Kiro's understanding with specialized guidance tailored to your project's unique needs:

Navigate to the Steering section in the Kiro panel
Click the + button to create a new .md file
Choose a descriptive filename (e.g., api-standards.md)
Write your guidance using standard markdown syntax
Use natural language to describe your requirements, then select the Refine button and Kiro will format it
Copied!Inclusion Modes
Steering files can be configured to load at different times based on your needs. This flexibility helps optimize performance and ensures relevant context is available when needed.

Configure inclusion modes by adding front matter to the top of your steering files. The front matter uses YAML syntax and must be placed at the very beginning of the file, enclosed by triple dashes (---).

Copied!Always Included (Default)
yaml

---
inclusion: always
---
These files are loaded into every Kiro interaction automatically. Use this mode for core standards that should influence all code generation and suggestions. Examples include your technology stack, coding conventions, and fundamental architectural principles.

Best for: Project-wide standards, technology preferences, security policies, and coding conventions that apply universally.

Copied!Conditional Inclusion
yaml

---
inclusion: fileMatch
fileMatchPattern: "components/**/*.tsx"
---
Files are automatically included only when working with files that match the specified pattern. This keeps context relevant and reduces noise by loading specialized guidance only when needed.

Common patterns:

"*.tsx" - React components and JSX files
"app/api/**/*" - API routes and backend logic
"**/*.test.*" - Test files and testing utilities
"src/components/**/*" - Component-specific guidelines
"*.md" - Documentation files
Best for: Domain-specific standards like component patterns, API design rules, testing approaches, or deployment procedures that only apply to certain file types.

Copied!Manual Inclusion
yaml

---
inclusion: manual
---
Files are available on-demand by referencing them with #steering-file-name in your chat messages. This gives you precise control over when specialized context is needed without cluttering every interaction.

Usage: Type #troubleshooting-guide or #performance-optimization in chat to include that steering file for the current conversation.

Best for: Specialized workflows, troubleshooting guides, migration procedures, or context-heavy documentation that's only needed occasionally.

Copied!File References
Link to live project files to keep steering current:

markdown

#[[file:<relative_file_name>]]
Examples:

API specs: #[[file:api/openapi.yaml]]
Component patterns: #[[file:components/ui/button.tsx]]
Config templates: #[[file:.env.example]]
Copied!Best Practices
Keep Files Focused One domain per file - API design, testing, or deployment procedures.

Use Clear Names

api-rest-conventions.md - REST API standards
testing-unit-patterns.md - Unit testing approaches
components-form-validation.md - Form component standards
Include Context Explain why decisions were made, not just what the standards are.

Provide Examples Use code snippets and before/after comparisons to demonstrate standards.

Security First Never include API keys, passwords, or sensitive data. Steering files are part of your codebase.

Maintain Regularly

Review during sprint planning and architecture changes
Test file references after restructuring
Treat steering changes like code changes - require reviews
Copied!Common Steering File Strategies
API Standards (api-standards.md) - Define REST conventions, error response formats, authentication flows, and versioning strategies. Include endpoint naming patterns, HTTP status code usage, and request/response examples.

Testing Approach (testing-standards.md) - Establish unit test patterns, integration test strategies, mocking approaches, and coverage expectations. Document preferred testing libraries, assertion styles, and test file organization.

Code Style (code-conventions.md) - Specify naming patterns, file organization, import ordering, and architectural decisions. Include examples of preferred code structures, component patterns, and anti-patterns to avoid.

Security Guidelines (security-policies.md) - Document authentication requirements, data validation rules, input sanitization standards, and vulnerability prevention measures. Include secure coding practices specific to your application.

Deployment Process (deployment-workflow.md) - Outline build procedures, environment configurations, deployment steps, and rollback strategies. Include CI/CD pipeline details and environment-specific requirements.

Custom steering files are stored in .kiro/steering/ and become immediately available across all Kiro interactions.