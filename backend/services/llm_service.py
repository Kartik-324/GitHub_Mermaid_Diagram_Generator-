# backend/services/llm_service.py
import os
import re
from dotenv import load_dotenv
load_dotenv()
from langchain_openai import ChatOpenAI
from langchain.messages import HumanMessage, SystemMessage, AIMessage

def get_llm():
    """Initialize LLM with settings optimized for consistency"""
    return ChatOpenAI(
        model="gpt-4o",
        temperature=0.05,  # Very low for consistency
        openai_api_key=os.getenv("OPENAI_API_KEY")
    )

def validate_diagram_completeness(mermaid_code: str, repo_data: dict) -> tuple:
    """Validate that diagram is comprehensive enough"""
    issues = []
    
    # Count nodes/components
    lines = mermaid_code.split('\n')
    node_count = 0
    for line in lines:
        if '[' in line and ']' in line and not line.strip().startswith('%%'):
            node_count += 1
    
    # Get repo size
    file_count = len(repo_data.get('file_contents', {}))
    
    # Enforce minimum nodes based on repo size
    if file_count < 20:
        min_nodes = 15
    elif file_count < 50:
        min_nodes = 25
    else:
        min_nodes = 35
    
    if node_count < min_nodes:
        issues.append(f"Diagram too simple: only {node_count} components (need {min_nodes}+)")
    
    # Check for subgraphs (organization)
    has_subgraphs = 'subgraph' in mermaid_code.lower()
    if not has_subgraphs and file_count > 10:
        issues.append("Missing organization: no subgraphs used")
    
    # Check for generic names (placeholders)
    generic_names = ['service', 'component', 'module', 'handler', 'controller', 'utility']
    code_lower = mermaid_code.lower()
    for generic in generic_names:
        if f'[{generic}]' in code_lower or f'{generic}[' in code_lower:
            issues.append(f"Found generic placeholder: '{generic}'")
    
    return len(issues) == 0, issues

def validate_mermaid_syntax(mermaid_code: str) -> tuple:
    """Validate Mermaid syntax and return errors if any"""
    errors = []
    lines = mermaid_code.strip().split('\n')
    
    if not lines:
        return False, ["Empty diagram code"]
    
    first_line = lines[0].strip()
    valid_types = [
        'sequenceDiagram', 'graph', 'flowchart', 'classDiagram',
        'erDiagram', 'stateDiagram', 'journey', 'gantt', 'mindmap',
        'pie', 'gitGraph'
    ]
    
    if not any(first_line.startswith(t) for t in valid_types):
        errors.append(f"Invalid diagram type: {first_line[:50]}")
        return False, errors
    
    for i, line in enumerate(lines[1:], 1):
        line = line.strip()
        if not line or line.startswith('%%'):
            continue
        
        if line.startswith('subgraph') or line == 'end':
            continue
        
        if line.count('[') != line.count(']'):
            errors.append(f"Line {i}: Unmatched brackets")
        if line.count('(') != line.count(')'):
            errors.append(f"Line {i}: Unmatched parentheses")
        if line.count('{') != line.count('}'):
            errors.append(f"Line {i}: Unmatched braces")
    
    return len(errors) == 0, errors

def fix_mermaid_syntax(mermaid_code: str) -> str:
    """Auto-fix common Mermaid syntax errors"""
    code = mermaid_code.strip()
    
    if code.startswith("```mermaid"):
        code = code.replace("```mermaid", "").replace("```", "").strip()
    elif code.startswith("```"):
        code = code.replace("```", "").strip()
    
    lines = code.split('\n')
    fixed_lines = []
    
    for line in lines:
        line = line.strip()
        
        if not line or line.startswith('%%'):
            fixed_lines.append(line)
            continue
        
        if line.startswith('subgraph') or line == 'end':
            fixed_lines.append(line)
            continue
        
        # Fix arrow syntax
        line = re.sub(r'-{4,}>', '-->', line)
        line = re.sub(r'\.{4,}>', '-..->', line)
        line = line.replace('===>', '-->')
        line = line.replace('....>', '-..->')
        
        # Fix node IDs with spaces - only before brackets
        if '[' in line or '(' in line or '-->' in line or '-..->' in line:
            parts = line.split('[', 1)
            if len(parts) > 1:
                before_bracket = parts[0]
                before_bracket = re.sub(r'(\w+)\s+(\w+)(?=\s*$)', r'\1_\2', before_bracket)
                line = before_bracket + '[' + parts[1]
        
        line = re.sub(r';+', ';', line)
        
        fixed_lines.append(line)
    
    return '\n'.join(fixed_lines)

def extract_detailed_repo_components(repo_data: dict) -> dict:
    """Extract and categorize ALL components from repository"""
    
    components = {
        'frontend_files': [],
        'backend_files': [],
        'services': [],
        'routes': [],
        'models': [],
        'components': [],
        'pages': [],
        'utils': [],
        'config_files': [],
        'database_files': [],
        'api_endpoints': [],
        'dependencies': [],
        'folders': [],
        'all_files': []
    }
    
    file_structure = repo_data.get('file_structure', {})
    
    def traverse_structure(obj, path=""):
        if isinstance(obj, dict):
            for key, value in obj.items():
                current_path = f"{path}/{key}" if path else key
                
                if isinstance(value, dict):
                    components['folders'].append(current_path)
                    traverse_structure(value, current_path)
                else:
                    components['all_files'].append(current_path)
                    
                    if 'frontend' in current_path.lower() or 'client' in current_path.lower():
                        components['frontend_files'].append(current_path)
                    if 'backend' in current_path.lower() or 'server' in current_path.lower():
                        components['backend_files'].append(current_path)
                    if 'service' in current_path.lower():
                        components['services'].append(current_path)
                    if 'route' in current_path.lower() or 'router' in current_path.lower():
                        components['routes'].append(current_path)
                    if 'model' in current_path.lower() or 'schema' in current_path.lower():
                        components['models'].append(current_path)
                    if 'component' in current_path.lower():
                        components['components'].append(current_path)
                    if 'page' in current_path.lower() or 'view' in current_path.lower():
                        components['pages'].append(current_path)
                    if 'util' in current_path.lower() or 'helper' in current_path.lower():
                        components['utils'].append(current_path)
                    if current_path.endswith(('.json', '.yaml', '.yml', '.env', '.toml', '.ini')):
                        components['config_files'].append(current_path)
                    if 'database' in current_path.lower() or 'db' in current_path.lower() or current_path.endswith('.sql'):
                        components['database_files'].append(current_path)
    
    traverse_structure(file_structure)
    
    # Extract dependencies
    file_contents = repo_data.get('file_contents', {})
    for filename, content in file_contents.items():
        if 'requirements.txt' in filename or 'package.json' in filename or 'pyproject.toml' in filename:
            if isinstance(content, str):
                lines = content.split('\n')
                for line in lines[:50]:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        components['dependencies'].append(line.split('==')[0].split('>=')[0].strip())
    
    return components

def analyze_repo_with_chat(repo_data: dict, question: str, chat_history: list = None) -> dict:
    """Analyze repository with ENFORCED comprehensive diagram generation"""
    llm = get_llm()
    
    if chat_history is None:
        chat_history = []
    
    from .github_service import format_file_structure, format_file_contents
    
    components = extract_detailed_repo_components(repo_data)
    
    # Build ultra-comprehensive context
    context = f"""
==============================================================================
REPOSITORY ANALYSIS - YOU MUST USE ALL THIS DATA TO CREATE COMPREHENSIVE DIAGRAMS
==============================================================================

Repository: {repo_data.get('name', 'Unknown')}
Language: {repo_data.get('language', 'Unknown')}
Total Files: {len(components['all_files'])}
Stars: {repo_data.get('stars', 0)} | Forks: {repo_data.get('forks', 0)}

==============================================================================
COMPLETE FILE STRUCTURE (USE ALL OF THIS):
==============================================================================
{format_file_structure(repo_data.get('file_structure', {}))}

==============================================================================
CATEGORIZED COMPONENTS (INCLUDE ALL IN DIAGRAM):
==============================================================================

📁 ALL FOLDERS ({len(components['folders'])} total):
{chr(10).join('   - ' + f for f in components['folders'])}

📄 ALL FILES ({len(components['all_files'])} total):
{chr(10).join('   - ' + f for f in components['all_files'][:50])}

🎨 FRONTEND FILES ({len(components['frontend_files'])}):
{chr(10).join('   - ' + f for f in components['frontend_files'])}

⚙️ BACKEND FILES ({len(components['backend_files'])}):
{chr(10).join('   - ' + f for f in components['backend_files'])}

🔧 SERVICES ({len(components['services'])}):
{chr(10).join('   - ' + f for f in components['services'])}

🛣️ ROUTES/API ({len(components['routes'])}):
{chr(10).join('   - ' + f for f in components['routes'])}

📊 MODELS ({len(components['models'])}):
{chr(10).join('   - ' + f for f in components['models'])}

🧩 COMPONENTS ({len(components['components'])}):
{chr(10).join('   - ' + f for f in components['components'])}

📄 PAGES ({len(components['pages'])}):
{chr(10).join('   - ' + f for f in components['pages'])}

🛠️ UTILITIES ({len(components['utils'])}):
{chr(10).join('   - ' + f for f in components['utils'])}

⚙️ CONFIG FILES ({len(components['config_files'])}):
{chr(10).join('   - ' + f for f in components['config_files'])}

💾 DATABASE FILES ({len(components['database_files'])}):
{chr(10).join('   - ' + f for f in components['database_files'])}

==============================================================================
FILE CONTENTS (ACTUAL CODE):
==============================================================================
{format_file_contents(repo_data.get('file_contents', {}))}

==============================================================================
MANDATORY DIAGRAM REQUIREMENTS - YOU MUST FOLLOW:
==============================================================================

1. COMPREHENSIVENESS (NON-NEGOTIABLE):
   • Include MINIMUM {max(20, len(components['all_files']) // 2)} components
   • Show ALL folders as subgraphs
   • Include ALL major files listed above
   • Don't skip any important files
   • Use actual filenames - NO GENERIC NAMES

2. ORGANIZATION (REQUIRED):
   • Use subgraphs for each major folder
   • Group related files together
   • Show clear hierarchy
   • Include external dependencies

3. SYNTAX (STRICT):
   • Node IDs: ONLY letters, numbers, underscores (NO SPACES)
   • Arrows: ONLY --> or -.-> or ==>
   • Use [DIAGRAM_START] before diagram
   • Use [DIAGRAM_END] after diagram
   • NO markdown code blocks

4. QUALITY STANDARDS:
   Small repos (< 20 files): minimum 15-20 nodes
   Medium repos (20-50 files): minimum 25-35 nodes
   Large repos (50+ files): minimum 35-50 nodes
   
   This repo has {len(components['all_files'])} files - your diagram MUST include
   at least {max(15, len(components['all_files']) // 2)} components.

5. FORBIDDEN (DO NOT DO):
   ✗ Generic names like "Service", "Component", "Module"
   ✗ Placeholder nodes
   ✗ Incomplete diagrams
   ✗ Skipping major files or folders
   ✗ Made-up filenames

==============================================================================
EXAMPLE OF COMPREHENSIVE DIAGRAM:
==============================================================================

[DIAGRAM_START]
flowchart TB
    subgraph Frontend["🎨 Frontend"]
        subgraph Pages["pages/"]
            chat_page["chat_interface.py"]
            history_page["diagram_history.py"]
            quick_page["quick_diagrams.py"]
        end
        
        subgraph Components["components/"]
            mermaid_comp["mermaid_renderer.py"]
            sidebar_comp["sidebar.py"]
            voice_comp["voice_input.py"]
            theme_comp["theme_manager.py"]
        end
        
        subgraph FrontendUtils["utils/"]
            state_util["state_manager.py"]
            helpers_util["helpers.py"]
        end
    end
    
    subgraph Backend["⚙️ Backend"]
        subgraph Routes["routes/"]
            chat_route["chat_routes.py"]
            diagram_route["diagram_routes.py"]
        end
        
        subgraph Services["services/"]
            llm_svc["llm_service.py"]
            github_svc["github_service.py"]
            prompt_svc["prompt_templates.py"]
        end
        
        models_file["models.py"]
        main_file["main.py"]
        config_file["config.py"]
    end
    
    subgraph External["🌐 External"]
        github_api["GitHub API"]
        openai_api["OpenAI GPT-4"]
        mermaid_api["Mermaid.ink"]
    end
    
    %% Connections (30+ connections for comprehensive view)
    chat_page-->chat_route
    chat_page-->mermaid_comp
    chat_page-->voice_comp
    chat_page-->sidebar_comp
    history_page-->diagram_route
    quick_page-->diagram_route
    
    mermaid_comp-->mermaid_api
    sidebar_comp-->theme_comp
    chat_page-->state_util
    history_page-->state_util
    
    chat_route-->llm_svc
    diagram_route-->llm_svc
    llm_svc-->github_svc
    llm_svc-->prompt_svc
    llm_svc-->openai_api
    
    github_svc-->github_api
    main_file-->chat_route
    main_file-->diagram_route
    config_file-->llm_svc
    config_file-->github_svc
[DIAGRAM_END]

NOW CREATE YOUR COMPREHENSIVE DIAGRAM USING ALL THE DATA ABOVE!
"""
    
    messages = [SystemMessage(content=context)]
    
    for msg in chat_history[-10:]:
        role = msg.get('role', '')
        content = msg.get('content', '')
        
        if role == 'user':
            messages.append(HumanMessage(content=content))
        elif role == 'assistant':
            messages.append(AIMessage(content=content))
    
    messages.append(HumanMessage(content=question))
    
    # Retry with enforcement
    max_retries = 3
    attempt = 0
    
    while attempt < max_retries:
        try:
            print(f"\n🎨 Generating diagram (attempt {attempt + 1}/{max_retries})...")
            
            response = llm.invoke(messages)
            answer_text = response.content
            
            answer, mermaid_code, diagram_type = extract_diagram_from_response(answer_text)
            
            if mermaid_code:
                mermaid_code = fix_mermaid_syntax(mermaid_code)
                
                # Validate syntax
                is_valid_syntax, syntax_errors = validate_mermaid_syntax(mermaid_code)
                
                # Validate completeness
                is_complete, completeness_issues = validate_diagram_completeness(mermaid_code, repo_data)
                
                if not is_valid_syntax and attempt < max_retries - 1:
                    print(f"   ❌ Syntax errors: {syntax_errors}")
                    error_msg = f"""
SYNTAX ERRORS FOUND: {', '.join(syntax_errors[:3])}

FIX THESE ISSUES:
1. Check node IDs - use underscores, no spaces
2. Use only --> or -.-> or ==> for arrows
3. Balance all brackets, parentheses, braces

REGENERATE with correct syntax.
"""
                    messages.append(AIMessage(content=answer_text))
                    messages.append(HumanMessage(content=error_msg))
                    attempt += 1
                    continue
                
                if not is_complete and attempt < max_retries - 1:
                    print(f"   ⚠️ Incompleteness issues: {completeness_issues}")
                    error_msg = f"""
DIAGRAM TOO SIMPLE: {', '.join(completeness_issues)}

YOU MUST:
1. Include at least {max(20, len(components['all_files']) // 2)} components
2. Use subgraphs for all major folders
3. Include ALL services, routes, pages, components listed
4. Show ALL major connections
5. Use REAL filenames from the repository data

REGENERATE with COMPREHENSIVE, detailed diagram including 30-50 components.
"""
                    messages.append(AIMessage(content=answer_text))
                    messages.append(HumanMessage(content=error_msg))
                    attempt += 1
                    continue
                
                print(f"   ✅ Diagram validated successfully!")
            
            follow_ups = generate_follow_up_questions(answer, mermaid_code is not None, diagram_type)
            
            return {
                "answer": answer,
                "mermaid_code": mermaid_code,
                "diagram_type": diagram_type,
                "has_diagram": mermaid_code is not None,
                "follow_up_questions": follow_ups,
                "repo_name": repo_data.get('name', 'Unknown')
            }
        
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
            if attempt < max_retries - 1:
                attempt += 1
                continue
            
            return {
                "answer": f"Error: {str(e)}",
                "mermaid_code": None,
                "diagram_type": None,
                "has_diagram": False,
                "follow_up_questions": [],
                "repo_name": repo_data.get('name', 'Unknown')
            }
    
    return {
        "answer": answer if 'answer' in locals() else "Unable to generate diagram",
        "mermaid_code": None,
        "diagram_type": None,
        "has_diagram": False,
        "follow_up_questions": [],
        "repo_name": repo_data.get('name', 'Unknown')
    }

def clean_mermaid_code(mermaid_code: str) -> str:
    """Clean and validate Mermaid code"""
    cleaned = fix_mermaid_syntax(mermaid_code)
    is_valid, errors = validate_mermaid_syntax(cleaned)
    if not is_valid:
        print(f"Validation warnings: {', '.join(errors)}")
    return cleaned

def detect_diagram_type(mermaid_code: str) -> str:
    """Detect the type of Mermaid diagram"""
    code_lower = mermaid_code.lower().strip()
    
    if code_lower.startswith("sequencediagram"):
        return "sequence"
    elif code_lower.startswith(("flowchart", "graph")):
        return "flowchart"
    elif code_lower.startswith("classdiagram"):
        return "class"
    elif code_lower.startswith("erdiagram"):
        return "database"
    elif code_lower.startswith("statediagram"):
        return "state"
    else:
        return "custom"

def extract_diagram_from_response(response_text: str) -> tuple:
    """Extract diagram code from chat response"""
    mermaid_code = None
    diagram_type = None
    answer = response_text.strip()
    
    if "[DIAGRAM_START]" in answer and "[DIAGRAM_END]" in answer:
        try:
            start_idx = answer.index("[DIAGRAM_START]") + len("[DIAGRAM_START]")
            end_idx = answer.index("[DIAGRAM_END]")
            raw_code = answer[start_idx:end_idx].strip()
            
            mermaid_code = clean_mermaid_code(raw_code)
            diagram_type = detect_diagram_type(mermaid_code)
            
            answer = answer[:answer.index("[DIAGRAM_START]")].strip()
            
        except Exception as e:
            print(f"Error extracting diagram: {e}")
            mermaid_code = None
            diagram_type = None
    
    return answer, mermaid_code, diagram_type

def generate_follow_up_questions(answer: str, has_diagram: bool, diagram_type: str = None) -> list:
    """Generate contextual follow-up questions"""
    
    if has_diagram:
        return [
            "Add more implementation details to the diagram",
            "Show error handling and edge cases",
            "Include deployment and infrastructure"
        ]
    
    return [
        "Create a comprehensive architecture diagram",
        "Show complete data flow with all components",
        "Generate detailed sequence diagram"
    ]