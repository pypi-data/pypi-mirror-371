#!/usr/bin/env python3
"""
Example: Programmatic usage of reasoning deployment service components
"""

import os
import threading
import time

def example_cli_usage():
    """Example of starting CLI editor programmatically."""
    print("📋 CLI Editor Example:")
    print("-" * 30)
    
    try:
        from reasoning_deployment_service.cli_editor import CLIRunner
        
        # Create CLI runner
        cli = CLIRunner()
        
        # Note: cli.run() is interactive and will block
        # For demo purposes, we'll just show it's available
        print("✅ CLI Runner created successfully")
        print("💡 To run: cli.run()")
        print("🔄 This will start an interactive CLI session")
        
        return cli
        
    except Exception as e:
        print(f"❌ Error with CLI: {e}")
        return None

def example_gui_usage():
    """Example of starting GUI editor programmatically.""" 
    print("\n🖼️ GUI Editor Example:")
    print("-" * 30)
    
    try:
        from reasoning_deployment_service.gui_editor import GUIEditor
        
        # Note: We don't actually create the GUI to avoid issues in headless environments
        print("✅ GUI Editor class available")
        print("💡 To run: app = GUIEditor(); app.mainloop()")
        print("🔄 This will start the tkinter GUI application")
        
        return GUIEditor
        
    except Exception as e:
        print(f"❌ Error with GUI: {e}")
        return None

def example_core_deployment():
    """Example of using core deployment service."""
    print("\n⚙️ Core Deployment Service Example:")
    print("-" * 40)
    
    try:
        from reasoning_deployment_service import ReasoningEngineDeploymentService
        
        print("✅ Core deployment service available")
        print("💡 Usage:")
        print("   service = ReasoningEngineDeploymentService(agent, 'DEV')")
        print("   service.one_deployment_with_everything_on_it()")
        
        return ReasoningEngineDeploymentService
        
    except Exception as e:
        print(f"❌ Error with core service: {e}")
        return None

def example_integrated_workflow():
    """Example of an integrated workflow."""
    print("\n🔗 Integrated Workflow Example:")
    print("-" * 35)
    
    print("""
def integrated_agent_workflow():
    # 1. Deploy your agent
    from reasoning_deployment_service import ReasoningEngineDeploymentService
    from google.adk.agents import BaseAgent
    
    class MyAgent(BaseAgent):
        def invoke(self, input_text: str) -> str:
            return f"Agent response: {input_text}"
    
    agent = MyAgent()
    service = ReasoningEngineDeploymentService(agent, "DEV")
    service.one_deployment_with_everything_on_it()
    
    # 2. Launch management interface
    choice = input("Choose interface (cli/gui): ")
    
    if choice == "cli":
        from reasoning_deployment_service.cli_editor import CLIRunner
        cli = CLIRunner()
        cli.run()
    elif choice == "gui":
        from reasoning_deployment_service.gui_editor import GUIEditor
        app = GUIEditor()
        app.mainloop()
""")

def check_environment():
    """Check if environment is properly configured."""
    print("\n🔍 Environment Check:")
    print("-" * 20)
    
    required_vars = [
        "DEV_PROJECT_ID", "DEV_PROJECT_NUMBER", 
        "DEV_PROJECT_LOCATION", "DEV_STAGING_BUCKET"
    ]
    
    missing = []
    for var in required_vars:
        if not os.getenv(var):
            missing.append(var)
    
    if missing:
        print(f"⚠️ Missing environment variables: {missing}")
        print("💡 Set these in your .env file before using the services")
        return False
    else:
        print("✅ Environment variables look good!")
        return True

def main():
    """Main example function."""
    print("🚀 Reasoning Deployment Service - Programmatic Usage Examples")
    print("=" * 65)
    
    # Check environment
    env_ok = check_environment()
    
    # Show component examples
    cli = example_cli_usage()
    gui_class = example_gui_usage() 
    core = example_core_deployment()
    example_integrated_workflow()
    
    # Summary
    print("\n📝 Summary:")
    print("-" * 12)
    print(f"✅ CLI Editor: {'Available' if cli else 'Not available'}")
    print(f"✅ GUI Editor: {'Available' if gui_class else 'Not available'}")
    print(f"✅ Core Service: {'Available' if core else 'Not available'}")
    print(f"✅ Environment: {'Configured' if env_ok else 'Needs setup'}")
    
    if cli and gui_class and core:
        print("\n🎉 All components are ready for programmatic use!")
    else:
        print("\n⚠️ Some components may need additional setup or dependencies.")

if __name__ == "__main__":
    main()
