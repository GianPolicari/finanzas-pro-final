"""
Login View - User Authentication
Handles Sign Up and Sign In with Supabase Auth
"""

import streamlit as st
from database import get_supabase_client
import re

def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password: str) -> tuple[bool, str]:
    """
    Validate password strength
    Returns: (is_valid, error_message)
    """
    if len(password) < 6:
        return False, "La contraseña debe tener al menos 6 caracteres"
    return True, ""

def render_login():
    """
    Render the authentication page with Sign In and Sign Up tabs
    """
    # Center the login form
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # App branding
        st.markdown("# 💰 Finanzas Pro")
        st.markdown("### Tu asistente financiero personal")
        st.markdown("---")
        
        # Create tabs for Login and Sign Up
        tab1, tab2 = st.tabs(["🔐 Iniciar Sesión", "📝 Registrarse"])
        
        # ============================================
        # TAB 1: SIGN IN
        # ============================================
        with tab1:
            st.markdown("#### Accede a tu cuenta")
            
            with st.form("login_form", clear_on_submit=False):
                email = st.text_input(
                    "📧 Email",
                    placeholder="tu@email.com",
                    key="login_email"
                )
                
                password = st.text_input(
                    "🔒 Contraseña",
                    type="password",
                    placeholder="Tu contraseña",
                    key="login_password"
                )
                
                submit_login = st.form_submit_button(
                    "Iniciar Sesión",
                    use_container_width=True,
                    type="primary"
                )
                
                if submit_login:
                    if not email or not password:
                        st.error("⚠️ Por favor completa todos los campos")
                    elif not validate_email(email):
                        st.error("⚠️ Email inválido")
                    else:
                        try:
                            supabase = get_supabase_client()
                            
                            # Attempt sign in
                            response = supabase.auth.sign_in_with_password({
                                "email": email,
                                "password": password
                            })
                            
                            if response.user:
                                # Store user in session state
                                st.session_state['user'] = response.user
                                st.session_state['user_id'] = response.user.id
                                
                                st.success(f"✅ Bienvenido, {email}!")
                                st.balloons()
                                
                                # Rerun to show the main app
                                st.rerun()
                            else:
                                st.error("❌ Error al iniciar sesión")
                                
                        except Exception as e:
                            error_message = str(e)
                            
                            # Handle common errors
                            if "Invalid login credentials" in error_message or "invalid" in error_message.lower():
                                st.error("❌ Email o contraseña incorrectos")
                            elif "Email not confirmed" in error_message:
                                st.warning("⚠️ Por favor confirma tu email antes de iniciar sesión")
                            else:
                                st.error(f"❌ Error: {error_message}")
        
        # ============================================
        # TAB 2: SIGN UP
        # ============================================
        with tab2:
            st.markdown("#### Crea tu cuenta")
            
            with st.form("signup_form", clear_on_submit=True):
                signup_email = st.text_input(
                    "📧 Email",
                    placeholder="tu@email.com",
                    key="signup_email"
                )
                
                signup_password = st.text_input(
                    "🔒 Contraseña",
                    type="password",
                    placeholder="Mínimo 6 caracteres",
                    key="signup_password"
                )
                
                signup_password_confirm = st.text_input(
                    "🔒 Confirmar Contraseña",
                    type="password",
                    placeholder="Repite tu contraseña",
                    key="signup_password_confirm"
                )
                
                submit_signup = st.form_submit_button(
                    "Crear Cuenta",
                    use_container_width=True,
                    type="primary"
                )
                
                if submit_signup:
                    # Validation
                    if not signup_email or not signup_password or not signup_password_confirm:
                        st.error("⚠️ Por favor completa todos los campos")
                    elif not validate_email(signup_email):
                        st.error("⚠️ Email inválido")
                    elif signup_password != signup_password_confirm:
                        st.error("⚠️ Las contraseñas no coinciden")
                    else:
                        # Validate password strength
                        is_valid, error_msg = validate_password(signup_password)
                        if not is_valid:
                            st.error(f"⚠️ {error_msg}")
                        else:
                            try:
                                supabase = get_supabase_client()
                                
                                # Attempt sign up
                                response = supabase.auth.sign_up({
                                    "email": signup_email,
                                    "password": signup_password
                                })
                                
                                if response.user:
                                    st.success("✅ ¡Cuenta creada exitosamente!")
                                    
                                    # Check if email confirmation is required
                                    if response.session:
                                        # Auto-login (email confirmation disabled in Supabase)
                                        st.session_state['user'] = response.user
                                        st.session_state['user_id'] = response.user.id
                                        st.info("🎉 Iniciando sesión automáticamente...")
                                        st.rerun()
                                    else:
                                        # Email confirmation required
                                        st.info("📧 Por favor revisa tu email para confirmar tu cuenta antes de iniciar sesión.")
                                        st.info("Luego regresa a la pestaña 'Iniciar Sesión'")
                                else:
                                    st.error("❌ Error al crear la cuenta")
                                    
                            except Exception as e:
                                error_message = str(e)
                                
                                # Handle common errors
                                if "already registered" in error_message.lower() or "already exists" in error_message.lower():
                                    st.error("❌ Este email ya está registrado. Usa la pestaña 'Iniciar Sesión'")
                                elif "Password should be" in error_message:
                                    st.error("⚠️ La contraseña no cumple con los requisitos mínimos")
                                else:
                                    st.error(f"❌ Error: {error_message}")
        
        # ============================================
        # FOOTER
        # ============================================
        st.markdown("---")
        st.caption("🔒 Tus datos están protegidos con Supabase Auth")
        st.caption("Cada usuario tiene acceso exclusivo a su información financiera")

if __name__ == "__main__":
    render_login()
