# frontend/components/sidebar.py - VOICE FEATURE REMOVED
import streamlit as st

def render_sidebar():
    """Render sidebar with settings and configuration"""
    
    with st.sidebar:
        st.markdown("## ⚙️ Settings")
        
        # API Endpoint Configuration
        st.markdown("### 🔌 API Endpoint")
        api_endpoint = st.text_input(
            "Backend URL",
            value=st.session_state.get('api_endpoint', 'http://localhost:8000'),
            help="FastAPI backend server address"
        )
        st.session_state.api_endpoint = api_endpoint
        
        # Test connection
        if st.button("🔍 Test Connection"):
            import requests
            try:
                response = requests.get(f"{api_endpoint}/", timeout=5)
                if response.status_code == 200:
                    st.success("✅ Connected successfully!")
                else:
                    st.error(f"❌ Server returned: {response.status_code}")
            except Exception as e:
                st.error(f"❌ Connection failed: {str(e)}")
        
        st.divider()
        
        # GitHub Token (for private repos)
        st.markdown("### 🔐 GitHub Token")
        st.info("💡 **Required for private repositories**")
        
        with st.expander("📖 How to get a token", expanded=False):
            st.markdown("""
**Steps to create a GitHub token:**

1. Go to [GitHub Settings](https://github.com/settings/tokens)
2. Click **Generate new token** → **Classic**
3. Check the **`repo`** permission
4. Copy the token
5. Paste it below

**Note:** Public repos don't need a token.
            """)
        
        github_token = st.text_input(
            "GitHub Personal Access Token",
            type="password",
            value=st.session_state.get('github_token', ''),
            help="Required for private repositories. Needs 'repo' scope."
        )
        
        if github_token != st.session_state.get('github_token', ''):
            st.session_state.github_token = github_token
            if github_token:
                st.success("🔒 Token saved! Private repos now accessible.")
            else:
                st.info("Public repos only")
        
        st.divider()
        
        # Theme Selection
        st.markdown("### 🎨 Theme")
        theme = st.selectbox(
            "Choose Theme",
            options=["Dark", "Light"],
            index=0 if st.session_state.get('theme', 'Dark') == 'Dark' else 1,
            key="theme_selector"
        )
        
        if theme != st.session_state.get('theme'):
            st.session_state.theme = theme
            st.rerun()
        
        st.divider()
        
        # App Info
        st.markdown("### ℹ️ About")
        st.markdown("""
**RepoVision AI v2.0**

Transform GitHub repositories into detailed Mermaid diagrams using AI.

**Features:**
- 📊 Multiple diagram types
- 💬 Interactive AI chat
- 🔍 Deep code analysis
- 🔒 Private repo support
- 💾 Export PNG/SVG

**Powered by:**
- OpenAI GPT-4
- FastAPI
- Streamlit
        """)
        
        # Statistics
        if st.session_state.diagram_history:
            st.divider()
            st.markdown("### 📊 Statistics")
            st.metric("Diagrams Generated", len(st.session_state.diagram_history))
        
        # Clear all data
        st.divider()
        if st.button("🗑️ Clear All Data", use_container_width=True):
            st.session_state.chat_history = []
            st.session_state.diagram_history = []
            st.session_state.query_history = []
            st.success("✅ All data cleared!")
            st.rerun()
    
    return api_endpoint