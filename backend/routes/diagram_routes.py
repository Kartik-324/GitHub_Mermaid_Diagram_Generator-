# backend/routes/diagram_routes.py - COMPLETE & TESTED
from fastapi import APIRouter, HTTPException
from models import DiagramRequest, DiagramResponse, CustomDiagramRequest
from services.github_service import fetch_github_repo_structure, format_file_structure, format_file_contents
from services.llm_service import get_llm, clean_mermaid_code, detect_diagram_type, validate_mermaid_syntax
from services.prompt_templates import get_diagram_prompt, get_custom_diagram_prompt
import traceback

router = APIRouter()

@router.post("/generate-diagram", response_model=DiagramResponse)
async def generate_diagram(request: DiagramRequest):
    """Generate a specific type of detailed diagram from repository analysis"""
    try:
        print(f"\n{'='*60}")
        print(f"🎨 Diagram Generation Request")
        print(f"📦 Repository: {request.repo_url}")
        print(f"📊 Type: {request.diagram_type}")
        print(f"🔒 Auth: {'Yes' if request.github_token else 'No'}")
        print(f"{'='*60}\n")
        
        # Validate inputs
        if not request.repo_url or not request.repo_url.strip():
            raise HTTPException(status_code=400, detail="Repository URL is required")
        
        if not request.diagram_type or not request.diagram_type.strip():
            raise HTTPException(status_code=400, detail="Diagram type is required")
        
        # Fetch repository data
        try:
            print("🔍 Step 1: Analyzing repository...")
            repo_data = fetch_github_repo_structure(
                request.repo_url, 
                deep_fetch=True,
                github_token=request.github_token
            )
            print(f"✅ Repository analyzed: {repo_data.get('total_files_analyzed', 0)} files")
            print()
        except HTTPException:
            raise
        except Exception as e:
            print(f"❌ Repository fetch failed: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to fetch repository: {str(e)}")
        
        # Initialize LLM
        try:
            print("🤖 Step 2: Initializing AI...")
            llm = get_llm()
            print("✅ AI initialized")
            print()
        except Exception as e:
            print(f"❌ AI initialization failed: {str(e)}")
            raise HTTPException(status_code=500, detail=f"AI initialization failed: {str(e)}")
        
        # Build context
        try:
            print("📝 Step 3: Building analysis context...")
            context = f"""
Repository: {repo_data.get('name', 'Unknown')}
Description: {repo_data.get('description', 'No description')}
Primary Language: {repo_data.get('language', 'Unknown')}
All Languages: {', '.join([f"{k} ({v} files)" for k, v in list(repo_data.get('languages', {}).items())[:5]])}
Stars: {repo_data.get('stars', 0)} | Forks: {repo_data.get('forks', 0)}

COMPLETE FILE STRUCTURE:
{format_file_structure(repo_data.get('file_structure', {}), max_items=150)}

KEY FILE CONTENTS (First 5KB of each file):
{format_file_contents(repo_data.get('file_contents', {}), max_files=60)}

README:
{repo_data.get('readme', '')[:8000]}

DEPENDENCIES:
{', '.join(repo_data.get('dependencies', {}).keys())}
"""
            print(f"✅ Context built ({len(context)} characters)")
            print()
        except Exception as e:
            print(f"❌ Context building failed: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Context building failed: {str(e)}")
        
        # Get diagram prompt
        try:
            print(f"💭 Step 4: Creating {request.diagram_type} diagram prompt...")
            prompt = get_diagram_prompt(request.diagram_type, context)
            print(f"✅ Prompt ready")
            print()
        except Exception as e:
            print(f"❌ Prompt creation failed: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Prompt creation failed: {str(e)}")
        
        # Generate diagram with retry logic
        max_retries = 3
        attempt = 0
        
        while attempt < max_retries:
            try:
                print(f"🎨 Step 5: Generating detailed diagram (attempt {attempt + 1}/{max_retries})...")
                response = llm.invoke(prompt)
                print("✅ AI response received")
                
                # Clean and validate
                mermaid_code = clean_mermaid_code(response.content)
                
                if not mermaid_code or len(mermaid_code.strip()) < 10:
                    raise ValueError("Generated diagram is empty or too short")
                
                # Validate syntax
                is_valid, errors = validate_mermaid_syntax(mermaid_code)
                
                if not is_valid and attempt < max_retries - 1:
                    print(f"⚠️ Syntax errors detected: {errors[:2]}")
                    print(f"🔄 Retrying with improved instructions...")
                    
                    retry_prompt = prompt + f"""

PREVIOUS ATTEMPT HAD ERRORS: {', '.join(errors[:3])}

REGENERATE with these STRICT RULES:
1. Node IDs: ONLY letters, numbers, underscores (NO SPACES!)
   ✅ Good: user_service, auth_controller, UserModel
   ❌ BAD: user service, auth controller
2. Arrows: ONLY --> or -.-> or ==>
3. Include 15-20+ major components for detailed view
4. Use actual file names from the repository
5. Organize with subgraphs by folder/module

Generate a DETAILED, comprehensive diagram with ALL major components:"""
                    
                    prompt = retry_prompt
                    attempt += 1
                    continue
                
                print(f"✅ Diagram generated successfully!")
                print(f"   - Size: {len(mermaid_code)} characters")
                print(f"   - Type: {request.diagram_type}")
                print()
                print(f"{'='*60}")
                print("✨ SUCCESS: Diagram ready!")
                print(f"{'='*60}\n")
                
                return DiagramResponse(
                    mermaid_code=mermaid_code,
                    diagram_type=request.diagram_type,
                    repo_name=repo_data.get('name', 'Unknown')
                )
                
            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"⚠️ Attempt {attempt + 1} failed: {str(e)}")
                    attempt += 1
                    continue
                else:
                    print(f"❌ All attempts failed: {str(e)}")
                    raise HTTPException(
                        status_code=500,
                        detail=f"Failed to generate valid diagram after {max_retries} attempts"
                    )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"\n{'='*60}")
        print(f"❌ UNEXPECTED ERROR")
        print(f"{'='*60}")
        print(traceback.format_exc())
        print(f"{'='*60}\n")
        
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@router.post("/generate-custom-diagram", response_model=DiagramResponse)
async def generate_custom_diagram(request: CustomDiagramRequest):
    """Generate a custom detailed diagram based on user's specific request"""
    try:
        print(f"\n{'='*60}")
        print(f"🎨 Custom Diagram Generation")
        print(f"📦 Repository: {request.repo_url}")
        print(f"💬 Prompt: {request.user_prompt[:80]}...")
        print(f"{'='*60}\n")
        
        # Validate inputs
        if not request.repo_url or not request.repo_url.strip():
            raise HTTPException(status_code=400, detail="Repository URL is required")
        
        if not request.user_prompt or not request.user_prompt.strip():
            raise HTTPException(status_code=400, detail="User prompt is required")
        
        # Fetch repository data
        try:
            print("🔍 Step 1: Analyzing repository...")
            repo_data = fetch_github_repo_structure(
                request.repo_url, 
                deep_fetch=True,
                github_token=request.github_token
            )
            print(f"✅ Repository analyzed: {repo_data.get('total_files_analyzed', 0)} files")
            print()
        except HTTPException:
            raise
        except Exception as e:
            print(f"❌ Repository fetch failed: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to fetch repository: {str(e)}")
        
        # Initialize LLM
        try:
            print("🤖 Step 2: Initializing AI...")
            llm = get_llm()
            print("✅ AI initialized")
            print()
        except Exception as e:
            print(f"❌ AI initialization failed: {str(e)}")
            raise HTTPException(status_code=500, detail=f"AI initialization failed: {str(e)}")
        
        # Build context
        try:
            print("📝 Step 3: Building context...")
            context = f"""
Repository: {repo_data.get('name', 'Unknown')}
Description: {repo_data.get('description', 'No description')}
Language: {repo_data.get('language', 'Unknown')}

FILE STRUCTURE:
{format_file_structure(repo_data.get('file_structure', {}), max_items=150)}

FILE CONTENTS:
{format_file_contents(repo_data.get('file_contents', {}), max_files=60)}

DEPENDENCIES:
{repo_data.get('dependencies', {})}
"""
            print(f"✅ Context ready")
            print()
        except Exception as e:
            print(f"❌ Context building failed: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Context building failed: {str(e)}")
        
        # Get custom prompt
        try:
            print("💭 Step 4: Creating custom prompt...")
            prompt = get_custom_diagram_prompt(request.user_prompt, context)
            print("✅ Prompt ready")
            print()
        except Exception as e:
            print(f"❌ Prompt creation failed: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Prompt creation failed: {str(e)}")
        
        # Generate diagram with retry logic
        max_retries = 3
        attempt = 0
        
        while attempt < max_retries:
            try:
                print(f"🎨 Step 5: Generating custom diagram (attempt {attempt + 1}/{max_retries})...")
                response = llm.invoke(prompt)
                print("✅ AI response received")
                
                # Clean and detect type
                mermaid_code = clean_mermaid_code(response.content)
                
                if not mermaid_code or len(mermaid_code.strip()) < 10:
                    raise ValueError("Generated diagram is empty")
                
                # Validate syntax
                is_valid, errors = validate_mermaid_syntax(mermaid_code)
                
                if not is_valid and attempt < max_retries - 1:
                    print(f"⚠️ Syntax errors: {errors[:2]}")
                    print(f"🔄 Retrying...")
                    
                    retry_prompt = prompt + f"""

SYNTAX ERRORS IN PREVIOUS ATTEMPT: {', '.join(errors[:3])}

FIX THESE AND REGENERATE:
1. Node IDs: NO SPACES (use underscore: user_service not user service)
2. Only use these arrows: --> or -.-> or ==>
3. Include 15-20+ components for detail
4. Use actual file names from repository

Generate corrected detailed diagram:"""
                    
                    prompt = retry_prompt
                    attempt += 1
                    continue
                
                diagram_type = detect_diagram_type(mermaid_code)
                
                print(f"✅ Custom diagram generated!")
                print(f"   - Type: {diagram_type}")
                print(f"   - Size: {len(mermaid_code)} characters")
                print()
                print(f"{'='*60}")
                print("✨ SUCCESS: Custom diagram ready!")
                print(f"{'='*60}\n")
                
                return DiagramResponse(
                    mermaid_code=mermaid_code,
                    diagram_type=diagram_type,
                    repo_name=repo_data.get('name', 'Unknown')
                )
                
            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"⚠️ Attempt {attempt + 1} failed: {str(e)}")
                    attempt += 1
                    continue
                else:
                    print(f"❌ All attempts failed")
                    raise HTTPException(
                        status_code=500,
                        detail=f"Failed to generate valid diagram after {max_retries} attempts"
                    )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"\n{'='*60}")
        print(f"❌ UNEXPECTED ERROR")
        print(f"{'='*60}")
        print(traceback.format_exc())
        print(f"{'='*60}\n")
        
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")