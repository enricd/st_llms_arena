import streamlit as st


# Function to create a contributor card
def contributor_card(image_url="", name="", role="", linkedin_url="", github_url=""):
    """
    Creates a contributor card with profile image, name, role, and LinkedIn profile link.
    """
    card = f"""
        <div style="border-radius: 10px; padding: 1rem; background-color: #484c63; display: flex; align-items: center; margin-bottom: 0.5rem;">
            <img src="{image_url}" alt="Profile picture" style="border-radius: 50%; width: 60px; height: 60px; margin-right: 1rem;">
            <div style="line-height: 1;">
                <div style="font-weight: bold; margin-bottom: 0.2rem;">{name}</div>
                <div style="font-style: italic; font-size: 0.8rem; margin-bottom: 0.2rem;">{role}</div>
                <a href="{linkedin_url}" target="_blank" style="font-size: 0.8rem;">LinkedIn</a>
                <span style="font-size: 0.8rem; margin: 0 0.3rem;">-</span>
                <a href="{github_url}" target="_blank" style="font-size: 0.8rem;">GitHub</a>
            </div>
        </div>
    """
    
    return card


enric_info = {
    "name": "Enric Domingo",
    "role": "ML and Software Engineer",
    "image_url": "https://avatars.githubusercontent.com/u/6952495?v=4",
    "linkedin_url": "https://www.linkedin.com/in/e-domingo/",
    "github_url": "https://www.github.com/enricd",
}