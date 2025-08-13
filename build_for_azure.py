#!/usr/bin/env python3
"""
Build script for CallSight360 Azure App Service deployment
This script builds the React frontend and prepares the deployment package
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

def run_command(command, cwd=None, shell=True):
    """Run a shell command and handle errors"""
    print(f"🔧 Running: {command}")
    try:
        result = subprocess.run(
            command, 
            shell=shell, 
            cwd=cwd, 
            check=True, 
            capture_output=True, 
            text=True
        )
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        if e.stdout:
            print(f"Output: {e.stdout}")
        if e.stderr:
            print(f"Error: {e.stderr}")
        return False

def main():
    """Main build process"""
    print("🚀 Building CallSight360 for Azure App Service deployment...")
    print("=" * 60)
    
    # Get current directory
    root_dir = Path(__file__).parent.absolute()
    frontend_dir = root_dir / "frontend"
    backend_dir = root_dir / "backend"
    static_dir = root_dir / "static"
    
    print(f"📁 Root directory: {root_dir}")
    print(f"📁 Frontend directory: {frontend_dir}")
    print(f"📁 Backend directory: {backend_dir}")
    
    # Step 1: Check prerequisites
    print("\n📋 Checking prerequisites...")
    
    if not frontend_dir.exists():
        print("❌ Frontend directory not found!")
        return False
    
    if not backend_dir.exists():
        print("❌ Backend directory not found!")
        return False
    
    if not (frontend_dir / "package.json").exists():
        print("❌ Frontend package.json not found!")
        return False
    
    if not (backend_dir / "requirements.txt").exists():
        print("❌ Backend requirements.txt not found!")
        return False
    
    print("✅ All prerequisites found")
    
    # Step 2: Build React frontend
    print("\n📦 Building React frontend...")
    
    # Install dependencies (this will install cross-env)
    print("📥 Installing frontend dependencies (including cross-env)...")
    if not run_command("npm install", cwd=frontend_dir):
        print("❌ Failed to install frontend dependencies")
        return False
    
    # Create .env.production file for consistent environment
    print("🔧 Creating production environment file...")
    env_prod_content = """GENERATE_SOURCEMAP=false
REACT_APP_API_URL=/api/v1
PUBLIC_URL=.
SKIP_PREFLIGHT_CHECK=true
CI=false"""
    
    env_prod_path = frontend_dir / ".env.production"
    try:
        with open(env_prod_path, 'w') as f:
            f.write(env_prod_content)
        print("✅ Created .env.production file")
    except Exception as e:
        print(f"⚠️ Warning: Could not create .env.production file: {e}")
    
    # Try building with the azure script first, fallback to regular build
    print("🏗️ Building React app for Azure...")
    build_success = False
    
    # Try the azure build script
    if run_command("npm run build:azure", cwd=frontend_dir):
        build_success = True
        print("✅ Azure build successful")
    else:
        print("⚠️ Azure build failed, trying regular build...")
        # Fallback to regular build
        if run_command("npm run build", cwd=frontend_dir):
            build_success = True
            print("✅ Regular build successful")
        else:
            print("❌ Both build attempts failed")
            
            # Try manual build as last resort
            print("🔄 Attempting manual build...")
            manual_build_cmd = "npx react-scripts build"
            
            # Set environment variables for the process
            env = os.environ.copy()
            env['GENERATE_SOURCEMAP'] = 'false'
            env['REACT_APP_API_URL'] = '/api/v1'
            env['PUBLIC_URL'] = '.'
            
            try:
                result = subprocess.run(
                    manual_build_cmd,
                    shell=True,
                    cwd=frontend_dir,
                    check=True,
                    env=env,
                    capture_output=True,
                    text=True
                )
                print("✅ Manual build successful")
                build_success = True
            except subprocess.CalledProcessError as e:
                print(f"❌ Manual build also failed: {e}")
                if e.stdout:
                    print(f"Output: {e.stdout}")
                if e.stderr:
                    print(f"Error: {e.stderr}")
    
    if not build_success:
        print("❌ All build attempts failed!")
        return False
    
    # Step 3: Copy React build to static directory
    print("\n📁 Copying React build to static directory...")
    build_dir = frontend_dir / "build"
    
    if static_dir.exists():
        shutil.rmtree(static_dir)
        print("🗑️ Removed existing static directory")
    
    if build_dir.exists():
        shutil.copytree(build_dir, static_dir)
        print("✅ React build copied to static directory")
        
        # List some key files to verify
        key_files = ["index.html", "static/js", "static/css"]
        for file_path in key_files:
            full_path = static_dir / file_path
            if full_path.exists():
                print(f"   ✓ {file_path}")
            else:
                print(f"   ⚠️ Missing: {file_path}")
    else:
        print("❌ React build directory not found!")
        return False
    
    # Step 4: Verify deployment structure
    print("\n🔍 Verifying deployment structure...")
    
    required_files = [
        "startup.py",
        "web.config", 
        "backend/app/main.py",
        "backend/requirements.txt",
        "static/index.html"
    ]
    
    all_good = True
    for file_path in required_files:
        full_path = root_dir / file_path
        if full_path.exists():
            print(f"   ✅ {file_path}")
        else:
            print(f"   ❌ Missing: {file_path}")
            all_good = False
    
    if not all_good:
        print("❌ Some required files are missing!")
        return False
    
    # Step 5: Create requirements.txt in root (copy from backend)
    print("\n📋 Creating root requirements.txt...")
    backend_requirements = backend_dir / "requirements.txt"
    root_requirements = root_dir / "requirements.txt"
    
    if backend_requirements.exists():
        shutil.copy2(backend_requirements, root_requirements)
        print("✅ Requirements.txt copied to root")
    
    # Step 6: Display deployment summary
    print("\n" + "=" * 60)
    print("🎉 Build completed successfully!")
    print("\n📊 Deployment Structure:")
    print("├── startup.py           # Azure entry point")
    print("├── web.config           # Azure configuration")
    print("├── requirements.txt     # Python dependencies")
    print("├── static/              # React build files")
    print("│   ├── index.html")
    print("│   ├── static/js/")
    print("│   └── static/css/")
    print("└── backend/             # FastAPI application")
    print("    ├── app/")
    print("    └── requirements.txt")
    
    print(f"\n📈 Statistics:")
    print(f"   • Static files: {len(list(static_dir.rglob('*')))} files")
    print(f"   • Total size: {get_directory_size(static_dir):.2f} MB")
    
    print("\n🚀 Ready for Azure deployment!")
    print("\n📝 Next steps:")
    print("1. Open Cursor with your project")
    print("2. Install Azure App Service extension")
    print("3. Sign in to your Azure account")
    print("4. Right-click on the root folder")
    print("5. Select 'Deploy to Web App...'")
    print("6. Choose your Azure Web App: CTS-VibeAppca3602-1")
    print("7. Wait for deployment to complete")
    
    print(f"\n🌐 Your app will be available at:")
    print("https://CTS-VibeAppca3602-1.azurewebsites.net")
    
    return True

def get_directory_size(directory):
    """Calculate directory size in MB"""
    total_size = 0
    for file_path in Path(directory).rglob('*'):
        if file_path.is_file():
            total_size += file_path.stat().st_size
    return total_size / (1024 * 1024)  # Convert to MB

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n❌ Build interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1) 