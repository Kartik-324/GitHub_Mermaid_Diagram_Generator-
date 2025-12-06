# frontend/components/mermaid_renderer.py
import streamlit as st
import streamlit.components.v1 as components
from utils.helpers import generate_key
import re

def validate_and_fix_mermaid_syntax(mermaid_code: str) -> tuple:
    """Validate and fix common Mermaid syntax errors"""
    errors = []
    fixed_code = mermaid_code.strip()
    
    # Remove markdown code blocks
    if fixed_code.startswith("```mermaid"):
        fixed_code = fixed_code.replace("```mermaid", "").replace("```", "").strip()
    elif fixed_code.startswith("```"):
        fixed_code = fixed_code.replace("```", "").strip()
    
    # Remove [DIAGRAM_START] and [DIAGRAM_END] markers if present
    fixed_code = fixed_code.replace("[DIAGRAM_START]", "").replace("[DIAGRAM_END]", "").strip()
    
    # Fix common syntax issues
    lines = fixed_code.split('\n')
    fixed_lines = []
    
    for line in lines:
        original_line = line
        line = line.strip()
        
        if not line or line.startswith('%%'):
            fixed_lines.append(line)
            continue
        
        if line.startswith('subgraph') or line == 'end':
            fixed_lines.append(line)
            continue
        
        # Fix arrow syntax
        line = re.sub(r'-{3,}>', '-->', line)
        line = re.sub(r'\.{3,}>', '-..->', line)
        
        # Fix node IDs with spaces - more conservative approach
        if '-->' in line or '-..->' in line or '==>' in line:
            parts = line.split('[', 1)
            if len(parts) > 1:
                before_bracket = parts[0]
                before_bracket = re.sub(r'(\w+)\s+(\w+)(?=\s*$)', r'\1_\2', before_bracket)
                line = before_bracket + '[' + parts[1]
        
        if line != original_line.strip():
            errors.append(f"Fixed: {original_line.strip()[:50]}...")
        
        fixed_lines.append(line)
    
    fixed_code = '\n'.join(fixed_lines)
    
    return fixed_code, errors

def render_mermaid(mermaid_code, height=800, unique_id=None, theme='dark'):
    """Render mermaid diagram with ZOOM, PAN, and FULLSCREEN controls"""
    if not unique_id:
        unique_id = generate_key(mermaid_code)
    
    # Validate and fix syntax
    fixed_code, syntax_fixes = validate_and_fix_mermaid_syntax(mermaid_code)
    
    # Show syntax fixes if any
    if syntax_fixes:
        with st.expander("🔧 Auto-fixed Syntax Issues", expanded=False):
            for fix in syntax_fixes:
                st.info(fix)
    
    # Escape code for safe embedding
    safe_mermaid_code = fixed_code.replace('`', '\\`').replace('${', '\\${').replace('</script>', '<\\/script>')
    
    # FIXED: Enhanced theme configuration with proper text contrast
    if theme == 'dark':
        theme_vars = {
            'primaryColor': '#8b5cf6',
            'primaryTextColor': '#ffffff',  # WHITE text on colored backgrounds
            'primaryBorderColor': '#6d28d9',
            'lineColor': '#a78bfa',
            'secondaryColor': '#4c1d95',
            'tertiaryColor': '#2e1065',
            'background': '#1a1a1a',
            'mainBkg': '#2d2d2d',
            'secondBkg': '#3d3d3d',
            'textColor': '#ffffff',  # WHITE text for dark backgrounds
            'border1': '#404040',
            'border2': '#525252',
            'nodeBorder': '#6d28d9',
            'clusterBkg': '#2d2d2d',
            'clusterBorder': '#6d28d9',
            'defaultLinkColor': '#a78bfa',
            'titleColor': '#ffffff',  # WHITE titles
            'edgeLabelBackground': '#2d2d2d',
            'actorBorder': '#6d28d9',
            'actorBkg': '#3d3d3d',
            'actorTextColor': '#ffffff',  # WHITE actor text
            'actorLineColor': '#a78bfa',
            'signalColor': '#ffffff',  # WHITE signal text
            'signalTextColor': '#ffffff',  # WHITE signal text
            'labelBoxBkgColor': '#2d2d2d',
            'labelBoxBorderColor': '#6d28d9',
            'labelTextColor': '#ffffff',  # WHITE label text
            'loopTextColor': '#ffffff',  # WHITE loop text
            'noteBorderColor': '#6d28d9',
            'noteBkgColor': '#3d3d3d',
            'noteTextColor': '#ffffff',  # WHITE note text
            'activationBorderColor': '#6d28d9',
            'activationBkgColor': '#4c1d95',
            'sequenceNumberColor': '#1a1a1a',
            'fontSize': '14px',
            'fontFamily': '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
        }
    else:  # Light mode
        theme_vars = {
            'primaryColor': '#7c3aed',
            'primaryTextColor': '#ffffff',  # WHITE text on colored backgrounds
            'primaryBorderColor': '#6d28d9',
            'lineColor': '#8b5cf6',
            'secondaryColor': '#ede9fe',
            'tertiaryColor': '#f5f3ff',
            'background': '#ffffff',
            'mainBkg': '#f7f7f8',
            'secondBkg': '#ffffff',
            'textColor': '#000000',  # BLACK text for light backgrounds
            'border1': '#e5e5e5',
            'border2': '#d4d4d4',
            'nodeBorder': '#6d28d9',
            'clusterBkg': '#f7f7f8',
            'clusterBorder': '#6d28d9',
            'defaultLinkColor': '#8b5cf6',
            'titleColor': '#000000',  # BLACK titles
            'edgeLabelBackground': '#ffffff',
            'actorBorder': '#6d28d9',
            'actorBkg': '#ffffff',
            'actorTextColor': '#000000',  # BLACK actor text
            'actorLineColor': '#8b5cf6',
            'signalColor': '#000000',  # BLACK signal text
            'signalTextColor': '#000000',  # BLACK signal text
            'labelBoxBkgColor': '#f7f7f8',
            'labelBoxBorderColor': '#6d28d9',
            'labelTextColor': '#000000',  # BLACK label text
            'loopTextColor': '#000000',  # BLACK loop text
            'noteBorderColor': '#6d28d9',
            'noteBkgColor': '#ffffff',
            'noteTextColor': '#000000',  # BLACK note text
            'activationBorderColor': '#6d28d9',
            'activationBkgColor': '#ede9fe',
            'sequenceNumberColor': '#ffffff',
            'fontSize': '14px',
            'fontFamily': '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
        }
    
    mermaid_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <script src="https://unpkg.com/@panzoom/panzoom@4.5.1/dist/panzoom.min.js"></script>
        <script type="module">
            import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
            
            let hasError = false;
            let panzoomInstance = null;
            
            mermaid.initialize({{ 
                startOnLoad: false,
                theme: 'base',
                themeVariables: {{
                    primaryColor: '{theme_vars['primaryColor']}',
                    primaryTextColor: '{theme_vars['primaryTextColor']}',
                    primaryBorderColor: '{theme_vars['primaryBorderColor']}',
                    lineColor: '{theme_vars['lineColor']}',
                    secondaryColor: '{theme_vars['secondaryColor']}',
                    tertiaryColor: '{theme_vars['tertiaryColor']}',
                    background: '{theme_vars['background']}',
                    mainBkg: '{theme_vars['mainBkg']}',
                    secondBkg: '{theme_vars['secondBkg']}',
                    textColor: '{theme_vars['textColor']}',
                    border1: '{theme_vars['border1']}',
                    border2: '{theme_vars['border2']}',
                    nodeBorder: '{theme_vars['nodeBorder']}',
                    clusterBkg: '{theme_vars['clusterBkg']}',
                    clusterBorder: '{theme_vars['clusterBorder']}',
                    defaultLinkColor: '{theme_vars['defaultLinkColor']}',
                    titleColor: '{theme_vars['titleColor']}',
                    edgeLabelBackground: '{theme_vars['edgeLabelBackground']}',
                    actorBorder: '{theme_vars['actorBorder']}',
                    actorBkg: '{theme_vars['actorBkg']}',
                    actorTextColor: '{theme_vars['actorTextColor']}',
                    actorLineColor: '{theme_vars['actorLineColor']}',
                    signalColor: '{theme_vars['signalColor']}',
                    signalTextColor: '{theme_vars['signalTextColor']}',
                    labelBoxBkgColor: '{theme_vars['labelBoxBkgColor']}',
                    labelBoxBorderColor: '{theme_vars['labelBoxBorderColor']}',
                    labelTextColor: '{theme_vars['labelTextColor']}',
                    loopTextColor: '{theme_vars['loopTextColor']}',
                    noteBorderColor: '{theme_vars['noteBorderColor']}',
                    noteBkgColor: '{theme_vars['noteBkgColor']}',
                    noteTextColor: '{theme_vars['noteTextColor']}',
                    activationBorderColor: '{theme_vars['activationBorderColor']}',
                    activationBkgColor: '{theme_vars['activationBkgColor']}',
                    sequenceNumberColor: '{theme_vars['sequenceNumberColor']}',
                    fontSize: '{theme_vars['fontSize']}',
                    fontFamily: '{theme_vars['fontFamily']}'
                }},
                securityLevel: 'loose',
                logLevel: 'error',
                suppressErrorRendering: false,
                flowchart: {{
                    useMaxWidth: false,
                    htmlLabels: true,
                    curve: 'basis',
                    padding: 30,
                    nodeSpacing: 80,
                    rankSpacing: 80,
                    diagramPadding: 20
                }},
                sequence: {{
                    useMaxWidth: false,
                    diagramMarginX: 30,
                    diagramMarginY: 30,
                    actorMargin: 80,
                    width: 180,
                    height: 80,
                    boxMargin: 15,
                    messageMargin: 50,
                    mirrorActors: true,
                    wrap: true,
                    wrapPadding: 15
                }},
                class: {{
                    useMaxWidth: false,
                    padding: 30
                }},
                er: {{
                    useMaxWidth: false,
                    padding: 30,
                    layoutDirection: 'TB',
                    minEntityWidth: 150,
                    minEntityHeight: 100,
                    entityPadding: 20
                }},
                gantt: {{
                    useMaxWidth: false,
                    titleTopMargin: 25,
                    barHeight: 30,
                    barGap: 8,
                    topPadding: 50,
                    leftPadding: 100,
                    gridLineStartPadding: 35,
                    fontSize: 14
                }}
            }});
            
            function showErrorMessage(errorDetails) {{
                const container = document.getElementById('diagram-wrapper');
                if (container) {{
                    container.innerHTML = `
                        <div class="error-container">
                            <div class="error-icon">⚠️</div>
                            <div class="error-title">Diagram Rendering Error</div>
                            <div class="error-message">
                                <p><strong>The AI generated invalid Mermaid syntax</strong></p>
                                <div class="error-details">
                                    <p>${{errorDetails || 'Unknown error'}}</p>
                                </div>
                                <div class="suggestions">
                                    <p>💡 <strong>How to fix:</strong></p>
                                    <ul>
                                        <li>Click "Regenerate" and ask: <em>"Create a detailed diagram with correct syntax"</em></li>
                                        <li>Try: <em>"Show me an architecture diagram"</em></li>
                                        <li>Alternative: <em>"Create a simple flowchart"</em></li>
                                    </ul>
                                </div>
                            </div>
                        </div>
                    `;
                }}
            }}
            
            function initZoomControls() {{
                const wrapper = document.getElementById('diagram-wrapper');
                const container = document.getElementById('diagram-container');
                
                if (!wrapper || !container) {{
                    console.warn('Wrapper or container not found');
                    return;
                }}
                
                try {{
                    if (typeof Panzoom === 'undefined') {{
                        console.error('Panzoom library not loaded');
                        return;
                    }}
                    
                    panzoomInstance = Panzoom(container, {{
                        maxScale: 5,
                        minScale: 0.3,
                        startScale: 1,
                        canvas: true
                    }});
                    
                    container.parentElement.addEventListener('wheel', panzoomInstance.zoomWithWheel);
                    
                    document.getElementById('zoom-in')?.addEventListener('click', () => {{
                        panzoomInstance.zoomIn();
                    }});
                    
                    document.getElementById('zoom-out')?.addEventListener('click', () => {{
                        panzoomInstance.zoomOut();
                    }});
                    
                    document.getElementById('zoom-reset')?.addEventListener('click', () => {{
                        panzoomInstance.reset();
                    }});
                    
                    document.getElementById('zoom-fit')?.addEventListener('click', () => {{
                        panzoomInstance.reset();
                        panzoomInstance.zoom(0.8, {{ animate: true }});
                    }});
                    
                    document.getElementById('fullscreen-btn')?.addEventListener('click', () => {{
                        if (!document.fullscreenElement) {{
                            wrapper.requestFullscreen().catch(err => {{
                                console.error('Fullscreen error:', err);
                            }});
                        }} else {{
                            document.exitFullscreen();
                        }}
                    }});
                    
                    document.addEventListener('fullscreenchange', () => {{
                        const btn = document.getElementById('fullscreen-btn');
                        if (btn) {{
                            if (document.fullscreenElement) {{
                                btn.textContent = '🗙 Exit Fullscreen';
                            }} else {{
                                btn.textContent = '⛶ Fullscreen';
                            }}
                        }}
                    }});
                    
                    console.log('✅ Zoom controls initialized');
                }} catch (error) {{
                    console.error('Error initializing zoom controls:', error);
                }}
            }}
            
            async function renderDiagram() {{
                try {{
                    const code = `{safe_mermaid_code}`;
                    const container = document.getElementById('diagram-container');
                    
                    if (!code || code.trim().length < 10) {{
                        throw new Error('Empty or invalid diagram code');
                    }}
                    
                    console.log('📊 Rendering diagram...');
                    
                    const renderPromise = mermaid.render('mermaid-svg-{unique_id}', code);
                    const timeoutPromise = new Promise((_, reject) => 
                        setTimeout(() => reject(new Error('Render timeout after 15s')), 15000)
                    );
                    
                    const result = await Promise.race([renderPromise, timeoutPromise]);
                    
                    container.innerHTML = result.svg;
                    console.log('✅ Diagram rendered successfully!');
                    
                    setTimeout(() => {{
                        const svg = container.querySelector('svg');
                        if (svg) {{
                            svg.style.maxWidth = 'none';
                            svg.style.height = 'auto';
                            
                            try {{
                                const bbox = svg.getBBox();
                                if (bbox && bbox.width > 0 && bbox.height > 0) {{
                                    const padding = 40;
                                    const viewBoxWidth = bbox.width + (padding * 2);
                                    const viewBoxHeight = bbox.height + (padding * 2);
                                    
                                    svg.setAttribute('viewBox', 
                                        `${{bbox.x - padding}} ${{bbox.y - padding}} ${{viewBoxWidth}} ${{viewBoxHeight}}`
                                    );
                                    
                                    if (bbox.width > 1000) {{
                                        svg.setAttribute('width', bbox.width);
                                        svg.setAttribute('height', bbox.height);
                                    }}
                                }}
                            }} catch (e) {{
                                console.warn('Could not get bbox:', e);
                            }}
                            
                            svg.setAttribute('preserveAspectRatio', 'xMidYMid meet');
                        }}
                        
                        initZoomControls();
                    }}, 100);
                    
                }} catch (error) {{
                    console.error('❌ Mermaid render error:', error);
                    hasError = true;
                    showErrorMessage(error.message || error.toString());
                }}
            }}
            
            window.addEventListener('error', (e) => {{
                console.error('Global error:', e);
                if (!hasError) showErrorMessage(e.message);
                return true;
            }});
            
            if (document.readyState === 'loading') {{
                document.addEventListener('DOMContentLoaded', () => setTimeout(renderDiagram, 100));
            }} else {{
                setTimeout(renderDiagram, 100);
            }}
        </script>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{
                background: {theme_vars['background']};
                font-family: {theme_vars['fontFamily']};
                overflow: hidden;
            }}
            
            #diagram-wrapper {{
                position: relative;
                width: 100vw;
                height: 100vh;
                overflow: hidden;
                background: {theme_vars['background']};
            }}
            
            #diagram-container {{
                width: 100%;
                height: 100%;
                display: flex;
                justify-content: center;
                align-items: center;
                cursor: grab;
                overflow: visible;
            }}
            
            #diagram-container:active {{
                cursor: grabbing;
            }}
            
            .zoom-controls {{
                position: fixed;
                top: 20px;
                right: 20px;
                background: rgba(0, 0, 0, 0.8);
                border-radius: 12px;
                padding: 10px;
                display: flex;
                flex-direction: column;
                gap: 8px;
                z-index: 1000;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
            }}
            
            .zoom-btn {{
                background: rgba(139, 92, 246, 0.9);
                color: white;
                border: none;
                padding: 10px 16px;
                border-radius: 8px;
                cursor: pointer;
                font-size: 14px;
                font-weight: 600;
                transition: all 0.2s;
                white-space: nowrap;
            }}
            
            .zoom-btn:hover {{
                background: rgba(124, 58, 237, 1);
                transform: translateY(-2px);
                box-shadow: 0 4px 8px rgba(139, 92, 246, 0.4);
            }}
            
            .zoom-btn:active {{
                transform: translateY(0);
            }}
            
            .fullscreen-btn {{
                background: rgba(34, 197, 94, 0.9);
                margin-top: 8px;
            }}
            
            .fullscreen-btn:hover {{
                background: rgba(22, 163, 74, 1);
                box-shadow: 0 4px 8px rgba(34, 197, 94, 0.4);
            }}
            
            .instructions {{
                position: fixed;
                bottom: 20px;
                left: 20px;
                background: rgba(0, 0, 0, 0.8);
                color: white;
                padding: 15px 20px;
                border-radius: 10px;
                font-size: 13px;
                z-index: 1000;
                max-width: 300px;
            }}
            
            .instructions strong {{
                display: block;
                margin-bottom: 8px;
                color: #8b5cf6;
            }}
            
            .instructions p {{
                margin: 4px 0;
                opacity: 0.9;
            }}
            
            .error-container {{
                background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
                border: 3px solid #ef4444;
                border-radius: 16px;
                padding: 40px;
                max-width: 700px;
                margin: 40px auto;
                text-align: center;
                box-shadow: 0 20px 25px -5px rgba(239, 68, 68, 0.15);
            }}
            
            .error-icon {{ font-size: 4rem; margin-bottom: 1.5rem; }}
            .error-title {{ font-size: 2rem; font-weight: 800; color: #991b1b; margin-bottom: 1.5rem; }}
            .error-message {{ color: #7f1d1d; font-size: 1.1rem; line-height: 1.7; }}
            .error-details {{
                background: rgba(255, 255, 255, 0.5);
                border-radius: 8px;
                padding: 15px;
                margin: 15px 0;
                text-align: left;
                font-family: monospace;
                font-size: 0.9rem;
            }}
            
            .suggestions {{
                background: rgba(255, 255, 255, 0.6);
                border-radius: 10px;
                padding: 25px;
                margin: 20px 0;
                text-align: left;
            }}
            
            .suggestions ul {{ list-style: none; padding: 0; }}
            .suggestions li {{
                margin: 12px 0;
                padding-left: 25px;
                position: relative;
                line-height: 1.6;
            }}
            
            .suggestions li:before {{
                content: "→";
                position: absolute;
                left: 0;
                font-weight: bold;
                color: #dc2626;
            }}
            
            svg {{
                filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.1));
                min-width: 800px !important;
                min-height: 600px !important;
            }}
            
            /* FORCE text color for better contrast */
            svg text {{
                fill: {theme_vars['textColor']} !important;
            }}
            
            .loading {{
                color: {theme_vars['textColor']};
                font-size: 1.2rem;
                animation: fadeInOut 1.5s infinite;
            }}
            
            @keyframes fadeInOut {{ 
                0%, 100% {{ opacity: 0.5; }} 
                50% {{ opacity: 1; }} 
            }}
        </style>
    </head>
    <body>
        <div id="diagram-wrapper">
            <div class="zoom-controls">
                <button id="zoom-in" class="zoom-btn">🔍+ Zoom In</button>
                <button id="zoom-out" class="zoom-btn">🔍− Zoom Out</button>
                <button id="zoom-reset" class="zoom-btn">↺ Reset</button>
                <button id="zoom-fit" class="zoom-btn">⛶ Fit</button>
                <button id="fullscreen-btn" class="zoom-btn fullscreen-btn">⛶ Fullscreen</button>
            </div>
            
            <div class="instructions">
                <strong>💡 Controls:</strong>
                <p>🖱️ Drag to pan</p>
                <p>🖱️ Scroll to zoom</p>
                <p>🔘 Use buttons for controls</p>
            </div>
            
            <div id="diagram-container">
                <div class="loading">⏳ Rendering diagram...</div>
            </div>
        </div>
    </body>
    </html>
    """
    
    try:
        components.html(mermaid_html, height=height, scrolling=False)
        return True
    except Exception as e:
        st.error(f"⚠️ Render Error: {str(e)}")
        with st.expander("🔍 View Fixed Code"):
            st.code(fixed_code, language="mermaid")
        return False